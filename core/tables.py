import django_tables2 as tables
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from .models import Machine, Maintenance, Claim


class MachineTable(tables.Table):
    serial_number = tables.Column(verbose_name=_("Зав. №"))
    model = tables.Column(verbose_name=_("Модель"))
    shipment_date = tables.DateColumn(format="d.m.Y", verbose_name=_("Дата отгрузки"))
    client = tables.Column(accessor="client.email", verbose_name=_("Клиент"))
    service_company = tables.Column(accessor="service_company.email", verbose_name=_("Сервисная орг."))

    class Meta:
        model = Machine
        template_name = "django_tables2/semantic.html"
        fields = ("serial_number", "model", "shipment_date", "client", "service_company")
        orderable = False
        attrs = {
            "class": "data-table",
            "thead": {"class": "no-sort"},
        }
        row_attrs = {
            "onclick": lambda
                record: f"window.location.href='{reverse('core:machine_detail', args=[record.serial_number])}';",
            "style": "cursor: pointer;",
        }


class MaintenanceTable(tables.Table):
    machine = tables.Column(
        accessor="machine.serial_number",
        verbose_name=_("Машина")
    )
    type = tables.Column(verbose_name=_("Вид ТО"))
    date = tables.DateColumn(format="d.m.Y", verbose_name=_("Дата"))
    hours = tables.Column(verbose_name=_("Наработка, м/ч"))

    # Два отдельных столбца вместо одного кастомного
    organization = tables.Column(
        accessor="organization.email",
        verbose_name=_("Организация"),
        empty_values=(),
    )
    service_company = tables.Column(
        accessor="service_company.email",
        verbose_name=_("Сервисная компания"),
        empty_values=(),
    )

    actions = tables.TemplateColumn(
        template_code="""
            {% if is_manager or request.user == record.organization or request.user == record.service_company %}
                <a href="{% url 'core:maintenance_edit' pk=record.pk %}" 
                   title="Редактировать" 
                   onclick="event.stopPropagation();">✏️</a>
                <a href="{% url 'core:maintenance_delete' pk=record.pk %}" 
                   title="Удалить" 
                   onclick="event.stopPropagation(); return confirm('Уверены?');">🗑</a>
            {% endif %}
        """,
        orderable=False,
        verbose_name=_("Действия"),
    )

    class Meta:
        model = Maintenance
        fields = (
            "machine",
            "type",
            "date",
            "hours",
            "organization",
            "service_company",
            "actions"
        )
        order_by = "-date"
        orderable = False
        attrs = {"class": "data-table", "thead": {"class": "no-sort"}}
        row_attrs = {
            "onclick": lambda
                record: f"window.location.href='{reverse('core:machine_detail', args=[record.machine.serial_number])}';",
            "style": "cursor: pointer;",
        }


class ClaimTable(tables.Table):
    machine = tables.Column(
        accessor="machine.serial_number",
        verbose_name=_("Машина")
    )
    failure_date = tables.DateColumn(format="d.m.Y", verbose_name=_("Дата отказа"))
    failure_node = tables.Column(verbose_name=_("Узел отказа"))
    recovery_date = tables.DateColumn(format="d.m.Y", verbose_name=_("Дата восстановления"))
    downtime = tables.Column(verbose_name=_("Простой (дней)"))
    service_company = tables.Column(
        accessor="service_company.email",
        verbose_name=_("Сервис"),
        empty_values=(),
    )
    actions = tables.TemplateColumn(
        template_code="""
            {% if is_manager or request.user == record.service_company %}
                <a href="{% url 'core:claim_edit' pk=record.pk %}" 
                   onclick="event.stopPropagation();">✏️</a>
                <a href="{% url 'core:claim_delete' pk=record.pk %}" 
                   onclick="event.stopPropagation(); return confirm('Уверены?');">🗑</a>
            {% endif %}
        """,
        orderable=False,
        verbose_name=_("Действия"),
    )

    class Meta:
        model = Claim  # ← было Maintenance — исправлено!
        fields = (
            "machine",
            "failure_date",
            "failure_node",
            "recovery_date",
            "downtime",
            "service_company",
            "actions"
        )
        order_by = "-failure_date"
        orderable = False
        attrs = {"class": "data-table", "thead": {"class": "no-sort"}}
        row_attrs = {
            "onclick": lambda
                record: f"window.location.href='{reverse('core:machine_detail', args=[record.machine.serial_number])}';",
            "style": "cursor: pointer;",
        }