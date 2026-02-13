from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # allauth — все маршруты авторизации
    path('accounts/', include('allauth.urls')),

    path('', include('core.urls')),
]