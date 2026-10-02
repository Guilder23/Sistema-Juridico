from django.db import models
from django.conf import settings
from apps.clientes.models import Cliente
from apps.procesos.models import ProcesoAsunto
from apps.finanzas.models import MovimientoFinanciero

class Comprobante(models.Model):
    TIPO_CHOICES = [
        ('FACTURA', 'Factura'),
        ('RECIBO', 'Recibo'),
        ('TICKET', 'Ticket / Vale'),
        ('BOLETA_DEPOSITO', 'Boleta de Depósito'),
        ('COMPROBANTE_TRANSFERENCIA', 'Comprobante de Transferencia / QR'),
        ('OTRO', 'Otro'),
    ]

    ESTADO_VALIDACION_CHOICES = [
        ('PENDIENTE', 'Pendiente de Revisión'),
        ('VERIFICADO', 'Verificado / Aprobado'),
        ('RECHAZADO', 'Rechazado'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='comprobantes', verbose_name="Cliente")
    proceso = models.ForeignKey(ProcesoAsunto, on_delete=models.SET_NULL, null=True, blank=True, related_name='comprobantes', verbose_name="Proceso / Asunto")
    movimiento_financiero = models.OneToOneField(
        MovimientoFinanciero,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='comprobante',
        verbose_name="Movimiento Financiero Asociado"
    )
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES, default='FACTURA')
    numero_comprobante = models.CharField(max_length=100, blank=True, null=True, verbose_name="Número de Factura / Recibo")
    proveedor_emisor = models.CharField(max_length=255, blank=True, null=True, verbose_name="Proveedor / Razón Social Emisor")
    nit_emisor = models.CharField(max_length=50, blank=True, null=True, verbose_name="NIT / CI Emisor")
    monto = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Monto (Bs)")
    fecha_emision = models.DateField(null=True, blank=True, verbose_name="Fecha de Emisión")
    concepto = models.CharField(max_length=255, blank=True, null=True, verbose_name="Concepto / Detalle")
    imagen = models.ImageField(upload_to='comprobantes/%Y/%m/', verbose_name="Imagen / Fotografía")
    
    # Datos de OCR / IA
    ocr_procesado = models.BooleanField(default=False)
    datos_extraidos_ia = models.JSONField(blank=True, null=True, verbose_name="Datos Extraídos por IA / OCR")
    estado_validacion = models.CharField(max_length=20, choices=ESTADO_VALIDACION_CHOICES, default='PENDIENTE')
    
    subido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='comprobantes_subidos'
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Comprobante"
        verbose_name_plural = "Comprobantes"
        ordering = ['-fecha_registro']

    def __str__(self):
        return f"{self.get_tipo_display()} #{self.numero_comprobante or 'S/N'} - Bs {self.monto} ({self.cliente.nombre_razon_social})"
