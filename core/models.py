from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    Кастомный менеджер для модели пользователя без username
    """

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('Email обязателен'))

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Суперпользователь должен иметь is_staff=True'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Суперпользователь должен иметь is_superuser=True'))

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(
        _('email адрес'),
        unique=True,
        error_messages={
            'unique': _('Пользователь с таким email уже существует.'),
        },
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # можно добавить сюда поля, если захочешь их запрашивать при createsuperuser

    objects = CustomUserManager()

    class Meta:
        verbose_name = _('пользователь')
        verbose_name_plural = _('пользователи')

    def __str__(self):
        return self.email or "Без email"



# ────────────────────────────────────────────────
#                   Справочники
# ────────────────────────────────────────────────


class Directory(models.Model):
    """Базовая модель для всех справочников"""
    name = models.CharField(_('название'), max_length=200)
    description = models.TextField(_('описание'), blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class MachineModel(Directory):
    """Модель техники"""
    class Meta:
        verbose_name = _('модель техники')
        verbose_name_plural = _('модели техники')
        ordering = ['name']


class EngineModel(Directory):
    """Модель двигателя"""
    class Meta:
        verbose_name = _('модель двигателя')
        verbose_name_plural = _('модели двигателей')
        ordering = ['name']


class TransmissionModel(Directory):
    """Модель трансмиссии"""
    class Meta:
        verbose_name = _('модель трансмиссии')
        verbose_name_plural = _('модели трансмиссий')
        ordering = ['name']


class DriveAxleModel(Directory):
    """Модель ведущего моста"""
    class Meta:
        verbose_name = _('модель ведущего моста')
        verbose_name_plural = _('модели ведущих мостов')
        ordering = ['name']


class SteerAxleModel(Directory):
    """Модель управляемого моста"""
    class Meta:
        verbose_name = _('модель управляемого моста')
        verbose_name_plural = _('модели управляемых мостов')
        ordering = ['name']


# ────────────────────────────────────────────────
#                   Основная модель
# ────────────────────────────────────────────────

from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

serial_number_validator = RegexValidator(
    regex=r'^[A-Za-z0-9\-_]+$',
    message=_('Заводской номер может содержать только латинские буквы, цифры, дефис и подчёркивание.'),
    code='invalid_serial'
)

class Machine(models.Model):
    serial_number = models.CharField(
        _('зав. № машины'),
        max_length=100,
        unique=True,
        db_index=True,
        validators=[serial_number_validator],
        help_text=_('Только латинские буквы, цифры, -, _'),
    )

    model = models.ForeignKey(
        MachineModel, verbose_name=_('модель техники'),
        on_delete=models.PROTECT, related_name='machines'
    )
    engine_model = models.ForeignKey(
        EngineModel, verbose_name=_('модель двигателя'),
        on_delete=models.PROTECT, related_name='machines', null=True, blank=True
    )
    engine_serial = models.CharField(
        _('зав. № двигателя'), max_length=100, blank=True
    )
    transmission_model = models.ForeignKey(
        TransmissionModel, verbose_name=_('модель трансмиссии'),
        on_delete=models.PROTECT, related_name='machines', null=True, blank=True
    )
    transmission_serial = models.CharField(
        _('зав. № трансмиссии'), max_length=100, blank=True
    )
    drive_axle_model = models.ForeignKey(
        DriveAxleModel, verbose_name=_('модель ведущего моста'),
        on_delete=models.PROTECT, related_name='machines', null=True, blank=True
    )
    drive_axle_serial = models.CharField(
        _('зав. № ведущего моста'), max_length=100, blank=True
    )
    steer_axle_model = models.ForeignKey(
        SteerAxleModel, verbose_name=_('модель управляемого моста'),
        on_delete=models.PROTECT, related_name='machines', null=True, blank=True
    )
    steer_axle_serial = models.CharField(
        _('зав. № управляемого моста'), max_length=100, blank=True
    )

    contract_number = models.CharField(
        _('договор поставки №'), max_length=100, blank=True
    )
    contract_date = models.DateField(
        _('дата договора'), null=True, blank=True
    )
    shipment_date = models.DateField(
        _('дата отгрузки с завода'), null=True, blank=True
    )

    consignee = models.CharField(
        _('грузополучатель (конечный потребитель)'), max_length=300, blank=True
    )
    operation_address = models.CharField(
        _('адрес поставки / эксплуатации'), max_length=500, blank=True
    )

    options = models.TextField(
        _('комплектация / доп. опции'), blank=True
    )

    client = models.ForeignKey(
        User, verbose_name=_('клиент'),
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='client_machines'
    )
    service_company = models.ForeignKey(
        User, verbose_name=_('сервисная компания'),
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='service_machines'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('машина')
        verbose_name_plural = _('машины')
        ordering = ['-shipment_date', 'serial_number']
        indexes = [
            models.Index(fields=['serial_number']),
            models.Index(fields=['shipment_date']),
        ]

    def __str__(self):
        return f"{self.serial_number} — {self.model}"

class MaintenanceType(Directory):
    """Вид ТО"""
    class Meta:
        verbose_name = _('вид ТО')
        verbose_name_plural = _('виды ТО')
        ordering = ['name']


class FailureNode(Directory):
    """Узел отказа"""
    class Meta:
        verbose_name = _('узел отказа')
        verbose_name_plural = _('узлы отказа')
        ordering = ['name']


class RecoveryMethod(Directory):
    """Способ восстановления"""
    class Meta:
        verbose_name = _('способ восстановления')
        verbose_name_plural = _('способы восстановления')
        ordering = ['name']


# ────────────────────────────────────────────────
#                   Сущность ТО
# ────────────────────────────────────────────────

class Maintenance(models.Model):
    type = models.ForeignKey(
        MaintenanceType, verbose_name=_('вид ТО'),
        on_delete=models.PROTECT, related_name='maintenances'
    )
    date = models.DateField(_('дата проведения ТО'))
    hours = models.IntegerField(_('наработка, м/час'), default=0)
    order_number = models.CharField(_('№ заказ-наряда'), max_length=100, blank=True)
    order_date = models.DateField(_('дата заказ-наряда'), null=True, blank=True)
    organization = models.ForeignKey(
        User, verbose_name=_('организация, проводившая ТО'),
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='performed_maintenances'
    )
    machine = models.ForeignKey(
        Machine, verbose_name=_('машина'),
        on_delete=models.CASCADE, related_name='maintenances'
    )
    service_company = models.ForeignKey(
        User, verbose_name=_('сервисная компания'),
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='service_maintenances'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('ТО')
        verbose_name_plural = _('ТО')
        ordering = ['-date']  # По умолчанию сортировка по дате проведения (как в ТЗ)

    def __str__(self):
        return f"ТО {self.type} для {self.machine} ({self.date})"


# ────────────────────────────────────────────────
#                   Сущность Рекламация
# ────────────────────────────────────────────────

class Claim(models.Model):
    failure_date = models.DateField(_('дата отказа'))
    hours = models.IntegerField(_('наработка, м/час'), default=0)
    failure_node = models.ForeignKey(
        FailureNode, verbose_name=_('узел отказа'),
        on_delete=models.PROTECT, related_name='claims'
    )
    failure_description = models.TextField(_('описание отказа'), blank=True)
    recovery_method = models.ForeignKey(
        RecoveryMethod, verbose_name=_('способ восстановления'),
        on_delete=models.PROTECT, related_name='claims'
    )
    parts_used = models.TextField(_('используемые запасные части'), blank=True)
    recovery_date = models.DateField(_('дата восстановления'), null=True, blank=True)
    machine = models.ForeignKey(
        Machine, verbose_name=_('машина'),
        on_delete=models.CASCADE, related_name='claims'
    )
    service_company = models.ForeignKey(
        User, verbose_name=_('сервисная компания'),
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='service_claims'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('рекламация')
        verbose_name_plural = _('рекламации')
        ordering = ['-failure_date']  # По умолчанию сортировка по дате отказа (как в ТЗ)

    def __str__(self):
        return f"Рекламация для {self.machine} ({self.failure_date})"

    @property
    def downtime(self):
        """Расчётное поле: время простоя в днях"""
        if self.recovery_date and self.failure_date:
            return (self.recovery_date - self.failure_date).days
        return None