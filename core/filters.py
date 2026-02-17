from django import forms
import django_filters
from django.utils.translation import gettext_lazy as _

from .models import Machine, Maintenance, Claim, MachineModel, EngineModel, TransmissionModel, DriveAxleModel, SteerAxleModel, MaintenanceType, FailureNode, RecoveryMethod, User


class MachineFilter(django_filters.FilterSet):
    model = django_filters.ModelChoiceFilter(
        queryset=MachineModel.objects.all(),
        label=_("Модель техники"),
        empty_label=_("Все модели"),
    )
    engine_model = django_filters.ModelChoiceFilter(
        queryset=EngineModel.objects.all(),
        label=_("Модель двигателя"),
        empty_label=_("Все"),
    )
    transmission_model = django_filters.ModelChoiceFilter(
        queryset=TransmissionModel.objects.all(),
        label=_("Модель трансмиссии"),
        empty_label=_("Все"),
    )
    drive_axle_model = django_filters.ModelChoiceFilter(
        queryset=DriveAxleModel.objects.all(),
        label=_("Модель ведущего моста"),
        empty_label=_("Все"),
    )
    steer_axle_model = django_filters.ModelChoiceFilter(
        queryset=SteerAxleModel.objects.all(),
        label=_("Модель управляемого моста"),
        empty_label=_("Все"),
    )

    class Meta:
        model = Machine
        fields = [
            "model",
            "engine_model",
            "transmission_model",
            "drive_axle_model",
            "steer_axle_model",
        ]


class MaintenanceFilter(django_filters.FilterSet):
    type = django_filters.ModelChoiceFilter(
        queryset=MaintenanceType.objects.all(),
        label=_("Вид ТО"),
        empty_label=_("Все виды"),
    )
    machine__serial_number = django_filters.CharFilter(
        lookup_expr="icontains",
        label=_("Зав. № машины"),
        widget=forms.TextInput(attrs={"placeholder": "Например: 12345"}),
    )
    service_company = django_filters.ModelChoiceFilter(
        queryset=User.objects.filter(groups__name="Сервисная_организация"),
        label=_("Сервисная компания"),
        empty_label=_("Все"),
    )

    class Meta:
        model = Maintenance
        fields = ["type", "machine__serial_number", "service_company"]


class ClaimFilter(django_filters.FilterSet):
    failure_node = django_filters.ModelChoiceFilter(
        queryset=FailureNode.objects.all(),
        label=_("Узел отказа"),
        empty_label=_("Все"),
    )
    recovery_method = django_filters.ModelChoiceFilter(
        queryset=RecoveryMethod.objects.all(),
        label=_("Способ восстановления"),
        empty_label=_("Все"),
    )
    service_company = django_filters.ModelChoiceFilter(
        queryset=User.objects.filter(groups__name="Сервисная_организация"),
        label=_("Сервисная компания"),
        empty_label=_("Все"),
    )

    class Meta:
        model = Claim
        fields = ["failure_node", "recovery_method", "service_company"]