from django.db import models
from django.conf import settings
from apps.clientes.models import Cliente
from apps.procesos.models import ProcesoAsunto

class BitacoraActividad(models.Model):
    TIPO_ACTIVIDAD_CHOICES = [
        ('DOCUMENTO_RECIBIDO', 'Documentación Recibida'),
        ('SOLICITUD_PRESENTADA', 'Solicitud Presentada'),
        ('PAGO_REALIZADO', 'Pago / Gasto Realizado'),
        ('RESPUESTA_RECIBIDA', 'Respuesta / Notificación Recibida'),
        ('DOCUMENTO_SOLICITADO', 'Documentación Solicitada al Cliente'),
        ('REUNION', 'Reunión / Llamada'),
        ('CAMBIO_ESTADO', 'Cambio de Estado de Asunto'),
        ('OTRO', 'Otra Actividad / Nota'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='actividades', verbose_name="Cliente")
    proceso = models.ForeignKey(ProcesoAsunto, on_delete=models.SET_NULL, null=True, blank=True, related_name='actividades', verbose_name="Proceso / Asunto")
    tipo = models.CharField(max_length=40, choices=TIPO_ACTIVIDAD_CHOICES, default='OTRO')
    titulo = models.CharField(max_length=255, verbose_name="Título o Resumen de Actividad")
    descripcion = models.TextField(verbose_name="Descripción detallada de lo ocurrido")
    fecha_actividad = models.DateField(verbose_name="Fecha del suceso")
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actividades_registradas',
        verbose_name="Registrado por"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Bitácora / Actividad"
        verbose_name_plural = "Bitácora de Actividades"
        ordering = ['-fecha_actividad', '-created_at']

    def __str__(self):
        return f"[{self.fecha_actividad}] {self.titulo} - {self.cliente.nombre_razon_social}"
