from django.contrib import admin
from .models import (
    User,
    MachineModel, EngineModel, TransmissionModel,
    DriveAxleModel, SteerAxleModel,
    Machine, MaintenanceType, FailureNode, RecoveryMethod,
    Maintenance, Claim,
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('email',)
    list_filter = ('is_staff', 'is_superuser')


admin.site.register(MachineModel)
admin.site.register(EngineModel)
admin.site.register(TransmissionModel)
admin.site.register(DriveAxleModel)
admin.site.register(SteerAxleModel)


@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = (
        'serial_number', 'model', 'shipment_date',
        'client', 'service_company'
    )
    list_filter = ('model', 'shipment_date', 'service_company')
    search_fields = ('serial_number', 'engine_serial', 'transmission_serial')
    date_hierarchy = 'shipment_date'
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(MaintenanceType)
admin.site.register(FailureNode)
admin.site.register(RecoveryMethod)


@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    list_display = (
        'machine', 'type', 'date', 'hours', 'service_company'
    )
    list_filter = ('type', 'date', 'service_company')
    search_fields = ('machine__serial_number', 'order_number')
    date_hierarchy = 'date'
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = (
        'machine', 'failure_node', 'failure_date', 'recovery_date', 'downtime'
    )
    list_filter = ('failure_node', 'recovery_method', 'service_company')
    search_fields = ('machine__serial_number', 'failure_description')
    date_hierarchy = 'failure_date'
    readonly_fields = ('created_at', 'updated_at', 'downtime')  # downtime только для просмотра