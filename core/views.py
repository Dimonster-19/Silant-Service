from django.shortcuts import render
from django.views import View
from .models import Machine,  Maintenance, Claim
from .forms import MaintenanceForm, ClaimForm
from django.db import models
from django_filters.views import FilterView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.mixins import UserPassesTestMixin
from django_tables2 import RequestConfig
from .filters import MachineFilter, MaintenanceFilter, ClaimFilter
from .tables import MachineTable, MaintenanceTable, ClaimTable

from django_tables2 import RequestConfig

class ManagerOnlyMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='Менеджер').exists()

class HomeView(View):
    template_name = "core/home.html"

    def get(self, request):
        return render(request, self.template_name, {})

    def post(self, request):
        serial = request.POST.get("serial_number", "").strip()

        if not serial:
            return render(
                request,
                self.template_name,
                {"error": "Введите заводской номер машины"}
            )

        try:
            machine = Machine.objects.get(serial_number__iexact=serial)
        except Machine.DoesNotExist:
            return render(
                request,
                self.template_name,
                {"error": f"Машина с заводским номером «{serial}» не найдена в системе"}
            )

        # Показываем только первые 10 полей по заданию
        context = {
            "machine": machine,
            "fields": [
                ("Зав. № машины", machine.serial_number),
                ("Модель техники", machine.model.name if machine.model else "—"),
                ("Модель двигателя", machine.engine_model.name if machine.engine_model else "—"),
                ("Зав. № двигателя", machine.engine_serial or "—"),
                ("Модель трансмиссии", machine.transmission_model.name if machine.transmission_model else "—"),
                ("Зав. № трансмиссии", machine.transmission_serial or "—"),
                ("Модель ведущего моста", machine.drive_axle_model.name if machine.drive_axle_model else "—"),
                ("Зав. № ведущего моста", machine.drive_axle_serial or "—"),
                ("Модель управляемого моста", machine.steer_axle_model.name if machine.steer_axle_model else "—"),
                ("Зав. № управляемого моста", machine.steer_axle_serial or "—"),
            ]
        }

        return render(request, self.template_name, context)



@method_decorator(login_required, name='dispatch')
class DashboardView(View):
    template_name = "core/dashboard.html"

    def get(self, request):
        user = request.user
        tab = request.GET.get('tab', 'machines')
        is_manager = user.groups.filter(name='Менеджер').exists()

        # Определяем базовые queryset'ы в зависимости от роли
        if is_manager:
            machine_qs = Machine.objects.all()
            maintenance_qs = Maintenance.objects.all()
            claim_qs = Claim.objects.all()
        elif user.groups.filter(name='Клиент').exists():
            machine_qs = Machine.objects.filter(client=user)
            maintenance_qs = Maintenance.objects.filter(machine__client=user)
            claim_qs = Claim.objects.filter(machine__client=user)
        elif user.groups.filter(name='Сервисная_организация').exists():
            machine_qs = Machine.objects.filter(service_company=user)
            maintenance_qs = Maintenance.objects.filter(
                Q(organization=user) | Q(service_company=user)
            )
            claim_qs = Claim.objects.filter(service_company=user)
        else:
            machine_qs = Machine.objects.none()
            maintenance_qs = Maintenance.objects.none()
            claim_qs = Claim.objects.none()

        context = {
            'tab': tab,
            'is_manager': is_manager,
            'can_edit': is_manager,
        }

        # ────────────────────────────────────────────────
        # Вкладка МАШИНЫ
        # ────────────────────────────────────────────────
        # Быстрый поиск по зав. номеру (применяется первым)
        serial_quick = request.GET.get('serial_quick', '').strip()
        if serial_quick:
            machine_qs = machine_qs.filter(serial_number__icontains=serial_quick)

        machine_filter = MachineFilter(request.GET, queryset=machine_qs, prefix='m')
        machines_table = MachineTable(machine_filter.qs, request=request)
        RequestConfig(request, paginate={"per_page": 20}).configure(machines_table)

        context.update({
            'machine_filter': machine_filter,
            'machines_table': machines_table,
            'has_machines': machine_filter.qs.exists(),
        })

        # ────────────────────────────────────────────────
        # Вкладка ТО
        # ────────────────────────────────────────────────
        maintenance_filter = MaintenanceFilter(request.GET, queryset=maintenance_qs, prefix='mt')
        maintenances_table = MaintenanceTable(maintenance_filter.qs, request=request)
        RequestConfig(request, paginate={"per_page": 15}).configure(maintenances_table)

        context.update({
            'maintenance_filter': maintenance_filter,
            'maintenances_table': maintenances_table,
            'has_maintenances': maintenance_filter.qs.exists(),
        })

        # ────────────────────────────────────────────────
        # Вкладка РЕКЛАМАЦИИ
        # ────────────────────────────────────────────────
        claim_filter = ClaimFilter(request.GET, queryset=claim_qs, prefix='cl')
        claims_table = ClaimTable(claim_filter.qs, request=request)
        RequestConfig(request, paginate={"per_page": 15}).configure(claims_table)

        context.update({
            'claim_filter': claim_filter,
            'claims_table': claims_table,
            'has_claims': claim_filter.qs.exists(),
        })

        return render(request, self.template_name, context)

from django.http import Http404
from django.shortcuts import get_object_or_404


@method_decorator(login_required, name='dispatch')
class MachineDetailView(View):
    template_name = "core/machine_detail.html"

    def get(self, request, serial_number):
        machine = get_object_or_404(Machine, serial_number__iexact=serial_number)

        user = request.user
        can_view = False
        can_edit_machine = False
        can_add_maintenance = False
        can_add_claim = False

        if user.groups.filter(name='Менеджер').exists():
            can_view = True
            can_edit_machine = True
            can_add_maintenance = True
            can_add_claim = True
        elif user.groups.filter(name='Клиент').exists():
            can_view = machine.client == user
            can_add_maintenance = True          # клиент может добавлять ТО
            can_add_claim = False               # клиент НЕ может добавлять рекламации
        elif user.groups.filter(name='Сервисная_организация').exists():
            can_view = machine.service_company == user
            can_add_maintenance = True
            can_add_claim = True

        if not can_view:
            raise Http404("У вас нет доступа к этой машине")

        # Получаем связанные записи
        maintenances = machine.maintenances.order_by('-date')[:5]  # последние 5 ТО
        claims = machine.claims.order_by('-failure_date')[:5]  # последние 5 рекламаций

        # Подготавливаем все поля для отображения
        context = {
            "machine": machine,
            "can_edit": can_edit_machine,
            "can_add_maintenance": can_add_maintenance,
            "can_add_claim": can_add_claim,
            "maintenances": maintenances,  # ← добавлено
            "claims": claims,
            "fields": [
                ("Зав. № машины", machine.serial_number),
                ("Модель техники", machine.model.name if machine.model else "—"),
                ("Модель двигателя", machine.engine_model.name if machine.engine_model else "—"),
                ("Зав. № двигателя", machine.engine_serial or "—"),
                ("Модель трансмиссии", machine.transmission_model.name if machine.transmission_model else "—"),
                ("Зав. № трансмиссии", machine.transmission_serial or "—"),
                ("Модель ведущего моста", machine.drive_axle_model.name if machine.drive_axle_model else "—"),
                ("Зав. № ведущего моста", machine.drive_axle_serial or "—"),
                ("Модель управляемого моста", machine.steer_axle_model.name if machine.steer_axle_model else "—"),
                ("Зав. № управляемого моста", machine.steer_axle_serial or "—"),
                ("Договор поставки №", machine.contract_number or "—"),
                ("Дата договора", machine.contract_date.strftime("%d.%m.%Y") if machine.contract_date else "—"),
                ("Дата отгрузки с завода", machine.shipment_date.strftime("%d.%m.%Y") if machine.shipment_date else "—"),
                ("Грузополучатель (конечный потребитель)", machine.consignee or "—"),
                ("Адрес поставки (эксплуатации)", machine.operation_address or "—"),
                ("Комплектация (доп. опции)", machine.options or "—"),
                ("Клиент", machine.client.email if machine.client else "—"),
                ("Сервисная компания", machine.service_company.email if machine.service_company else "—"),
            ]
        }

        return render(request, self.template_name, context)

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from .forms import MachineForm
from .models import Machine


class MachineCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Machine
    form_class = MachineForm
    template_name = 'core/machine_form.html'
    success_url = reverse_lazy('core:dashboard')

    def test_func(self):
        return self.request.user.groups.filter(name='Менеджер').exists()

    def form_valid(self, form):
        # можно добавить дополнительные действия при успешном сохранении
        return super().form_valid(form)


class MachineUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Machine
    form_class = MachineForm
    template_name = 'core/machine_form.html'
    success_url = reverse_lazy('core:dashboard')

    def test_func(self):
        return self.request.user.groups.filter(name='Менеджер').exists()

    def get_object(self, queryset=None):
        # получаем по serial_number, а не по pk
        return Machine.objects.get(serial_number=self.kwargs['serial_number'])

from django.contrib import messages
from django.views.generic import DeleteView
from django.urls import reverse


class OwnershipMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        user = self.request.user
        if user.groups.filter(name='Менеджер').exists():
            return True
        if isinstance(obj, Maintenance):
            # Для ТО: проверяем organization или service_company == user, плюс доступ к машине
            if user.groups.filter(name='Сервисная_организация').exists():
                return (obj.organization == user or obj.service_company == user) and obj.machine.service_company == user
            elif user.groups.filter(name='Клиент').exists():
                # Клиент может edit ТО только если оно связано с его машиной (расширение ТЗ)
                return obj.machine.client == user
        elif isinstance(obj, Claim):
            # Для рекламаций: только service_company == user, плюс доступ к машине
            if user.groups.filter(name='Сервисная_организация').exists():
                return obj.service_company == user and obj.machine.service_company == user
        return False  # Клиент не edit/delete рекламации


class MaintenanceCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Maintenance
    form_class = MaintenanceForm
    template_name = 'core/machine_form.html'  # Переиспользуем, адаптируем title
    success_url = reverse_lazy('core:dashboard')

    def test_func(self):
        machine = get_object_or_404(Machine, serial_number=self.kwargs['serial_number'])
        user = self.request.user
        if user.groups.filter(name='Менеджер').exists():
            return True
        elif user.groups.filter(name='Клиент').exists() and machine.client == user:
            return True
        elif user.groups.filter(name='Сервисная_организация').exists() and machine.service_company == user:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавление ТО'
        return context

    def form_valid(self, form):
        machine = get_object_or_404(Machine, serial_number=self.kwargs['serial_number'])
        form.instance.machine = machine
        return super().form_valid(form)


class MaintenanceUpdateView(LoginRequiredMixin, OwnershipMixin, UpdateView):
    model = Maintenance
    form_class = MaintenanceForm
    template_name = 'core/machine_form.html'
    success_url = reverse_lazy('core:dashboard')

    def test_func(self):
        maintenance = self.get_object()
        user = self.request.user
        if user.groups.filter(name='Менеджер').exists():
            return True
        elif user.groups.filter(name='Клиент').exists() and maintenance.machine.client == user:
            return True
        elif user.groups.filter(name='Сервисная_организация').exists() and maintenance.machine.service_company == user:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование ТО'
        return context


class ClaimCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Claim
    form_class = ClaimForm
    template_name = 'core/machine_form.html'
    success_url = reverse_lazy('core:dashboard')

    def test_func(self):
        machine = get_object_or_404(Machine, serial_number=self.kwargs['serial_number'])
        user = self.request.user
        if user.groups.filter(name='Менеджер').exists():
            return True
        elif user.groups.filter(name='Сервисная_организация').exists() and machine.service_company == user:
            return True
        return False  # Клиент не может создавать/редактировать Claims

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавление рекламации'
        return context

    def form_valid(self, form):
        machine = get_object_or_404(Machine, serial_number=self.kwargs['serial_number'])
        form.instance.machine = machine
        return super().form_valid(form)


class ClaimUpdateView(LoginRequiredMixin, OwnershipMixin, UpdateView):
    model = Claim
    form_class = ClaimForm
    template_name = 'core/machine_form.html'
    success_url = reverse_lazy('core:dashboard')

    def test_func(self):
        claim = self.get_object()
        user = self.request.user
        if user.groups.filter(name='Менеджер').exists():
            return True
        elif user.groups.filter(name='Сервисная_организация').exists() and claim.machine.service_company == user:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование рекламации'
        return context

class MaintenanceDeleteView(LoginRequiredMixin, OwnershipMixin, DeleteView):
    model = Maintenance
    template_name = 'core/confirm_delete.html'  # Новый шаблон для подтверждения

    def get_success_url(self):
        return reverse('core:machine_detail', kwargs={'serial_number': self.object.machine.serial_number})

    def form_valid(self, form):
        messages.success(self.request, 'ТО успешно удалено.')
        return super().form_valid(form)

class ClaimDeleteView(LoginRequiredMixin, OwnershipMixin, DeleteView):
    model = Claim
    template_name = 'core/confirm_delete.html'

    def get_success_url(self):
        return reverse('core:machine_detail', kwargs={'serial_number': self.object.machine.serial_number})

    def form_valid(self, form):
        messages.success(self.request, 'Рекламация успешно удалена.')
        return super().form_valid(form)

from django.utils import timezone
from .utils.export import export_to_excel


@login_required
def export_machines(request):
    # Получаем тот же queryset, что и в дашборде
    user = request.user
    is_manager = user.groups.filter(name='Менеджер').exists()

    if is_manager:
        qs = Machine.objects.all()
    elif user.groups.filter(name='Клиент').exists():
        qs = Machine.objects.filter(client=user)
    elif user.groups.filter(name='Сервисная_организация').exists():
        qs = Machine.objects.filter(service_company=user)
    else:
        qs = Machine.objects.none()

    # Применяем те же фильтры
    filter_set = MachineFilter(request.GET, queryset=qs, prefix='m')
    qs = filter_set.qs

    # Если есть быстрый поиск
    serial_quick = request.GET.get('serial_quick', '').strip()
    if serial_quick:
        qs = qs.filter(serial_number__icontains=serial_quick)

    fields = ['serial_number', 'model', 'shipment_date', 'client', 'service_company']
    titles = ['Зав. №', 'Модель техники', 'Дата отгрузки', 'Клиент', 'Сервисная орг.']

    return export_to_excel(
        qs,
        fields,
        titles,
        filename=f"машины_{timezone.now().strftime('%Y-%m-%d')}.xlsx"
    )