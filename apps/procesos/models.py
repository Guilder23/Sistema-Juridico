from django.db import models
from django.conf import settings
from apps.clientes.models import Cliente

class ProcesoAsunto(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_PROCESO', 'En proceso'),
        ('ESPERANDO_DOCUMENTACION', 'Esperando documentación'),
        ('ESPERANDO_CLIENTE', 'Esperando cliente'),
        ('FINALIZADO', 'Finalizado'),
        ('CANCELADO', 'Cancelado'),
    ]

    PRIORIDAD_CHOICES = [
        ('BAJA', 'Baja'),
        ('MEDIA', 'Media'),
        ('ALTA', 'Alta'),
        ('URGENTE', 'Urgente'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='procesos', verbose_name="Cliente")
    titulo = models.CharField(max_length=255, verbose_name="Título del asunto / proceso")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción detallada")
    estado = models.CharField(max_length=30, choices=ESTADO_CHOICES, default='EN_PROCESO')
    prioridad = models.CharField(max_length=20, choices=PRIORIDAD_CHOICES, default='MEDIA')
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='procesos_asignados',
        verbose_name="Responsable"
    )
    fecha_inicio = models.DateField(null=True, blank=True, verbose_name="Fecha de inicio")
    fecha_limite = models.DateField(null=True, blank=True, verbose_name="Fecha límite")
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Proceso / Asunto"
        verbose_name_plural = "Procesos y Asuntos"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.titulo} - {self.cliente.nombre_razon_social} ({self.get_estado_display()})"
