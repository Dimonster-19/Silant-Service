# core/forms.py
from django import forms
from .models import (User, Machine, MachineModel, EngineModel, TransmissionModel,DriveAxleModel,
                     SteerAxleModel, Maintenance, Claim, MaintenanceType, RecoveryMethod, FailureNode,

                      )

class MachineForm(forms.ModelForm):
    class Meta:
        model = Machine
        fields = [
            'serial_number',
            'model',
            'engine_model',
            'engine_serial',
            'transmission_model',
            'transmission_serial',
            'drive_axle_model',
            'drive_axle_serial',
            'steer_axle_model',
            'steer_axle_serial',
            'contract_number',
            'contract_date',
            'shipment_date',
            'consignee',
            'operation_address',
            'options',
            'client',
            'service_company',
        ]

        widgets = {
            'shipment_date': forms.DateInput(attrs={'type': 'date'}),
            'contract_date': forms.DateInput(attrs={'type': 'date'}),
            'options': forms.Textarea(attrs={'rows': 4}),
            'operation_address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Ограничиваем выбор только пользователями из нужных групп
        self.fields['client'].queryset = User.objects.filter(groups__name='Клиент')
        self.fields['service_company'].queryset = User.objects.filter(groups__name='Сервисная_организация')

    def clean_serial_number(self):
        value = self.cleaned_data['serial_number'].strip().upper()
        if not value:
            raise forms.ValidationError("Заводской номер обязателен")

        # Можно добавить дополнительные проверки
        if not all(c.isalnum() or c in '-_' for c in value):
            raise forms.ValidationError(
                "Допускаются только латинские буквы, цифры, дефис и подчёркивание"
            )

        return value

class MaintenanceForm(forms.ModelForm):
    class Meta:
        model = Maintenance
        fields = [
            'type',
            'date',
            'hours',
            'order_number',
            'order_date',
            'organization',
            'service_company',
        ]  # machine задаётся в view

        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'order_date': forms.DateInput(attrs={'type': 'date'}),
            'hours': forms.NumberInput(attrs={'min': 0}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        qs = User.objects.filter(groups__name='Сервисная_организация')
        print("DEBUG MaintenanceForm: найдено пользователей в группе:", qs.count())
        print("DEBUG: их email:", [u.email for u in qs])

        # Ограничим выбор organization и service_company по группе
        self.fields['organization'].queryset = User.objects.filter(groups__name='Сервисная_организация')
        self.fields['service_company'].queryset = User.objects.filter(groups__name='Сервисная_организация')


class ClaimForm(forms.ModelForm):
    class Meta:
        model = Claim
        fields = [
            'failure_date',
            'hours',
            'failure_node',
            'failure_description',
            'recovery_method',
            'parts_used',
            'recovery_date',
            'service_company',
        ]  # machine задаётся в view

        widgets = {
            'failure_date': forms.DateInput(attrs={'type': 'date'}),
            'recovery_date': forms.DateInput(attrs={'type': 'date'}),
            'hours': forms.NumberInput(attrs={'min': 0}),
            'failure_description': forms.Textarea(attrs={'rows': 4}),
            'parts_used': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        qs = User.objects.filter(groups__name='Сервисная_организация')
        print("DEBUG MaintenanceForm: найдено пользователей в группе:", qs.count())
        print("DEBUG: их email:", [u.email for u in qs])

        self.fields['service_company'].queryset = User.objects.filter(groups__name='Сервисная_организация')


