from django.urls import path
from .views import (HomeView, DashboardView, MachineDetailView, MachineCreateView, MachineUpdateView,
                    MaintenanceCreateView, MaintenanceUpdateView, ClaimCreateView, ClaimUpdateView,
                    MaintenanceDeleteView, ClaimDeleteView, export_machines,
                    )
app_name = "core"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),

    path("dashboard/", DashboardView.as_view(), name="dashboard"),

    path("machines/create/", MachineCreateView.as_view(), name="machine_create"),

    path("machines/<str:serial_number>/edit/", MachineUpdateView.as_view(), name="machine_edit"),

    path("machines/<str:serial_number>/", MachineDetailView.as_view(), name="machine_detail"),

    path('machines/<str:serial_number>/maintenance/create/', MaintenanceCreateView.as_view(), name='maintenance_create'),

    path('maintenance/<int:pk>/edit/', MaintenanceUpdateView.as_view(), name='maintenance_edit'),

    path('machines/<str:serial_number>/claims/create/', ClaimCreateView.as_view(), name='claim_create'),

    path('claims/<int:pk>/edit/', ClaimUpdateView.as_view(), name='claim_edit'),

    path('maintenance/<int:pk>/delete/', MaintenanceDeleteView.as_view(), name='maintenance_delete'),

    path('claim/<int:pk>/delete/', ClaimDeleteView.as_view(), name='claim_delete'),

    path('export/machines/', export_machines, name='export_machines'),



]