from django.db import models
from django.conf import settings
from apps.clientes.models import Cliente
from apps.procesos.models import ProcesoAsunto

class ReporteGenerado(models.Model):
    TIPO_REPORTE = [
        ('INFORME_GESTION', 'Informe de Gestión General'),
        ('INFORME_FINANCIERO', 'Estado de Cuenta / Gastos'),
        ('INFORME_PROCESOS', 'Resumen de Procesos y Asuntos'),
        ('INFORME_IA', 'Informe Especial Asistido por IA'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='informes_generados')
    proceso = models.ForeignKey(ProcesoAsunto, on_delete=models.SET_NULL, null=True, blank=True, related_name='informes')
    titulo = models.CharField(max_length=255)
    tipo = models.CharField(max_length=40, choices=TIPO_REPORTE, default='INFORME_GESTION')
    periodo_inicio = models.DateField(null=True, blank=True)
    periodo_fin = models.DateField(null=True, blank=True)
    contenido = models.TextField(blank=True, null=True, verbose_name="Contenido / Markdown / Resumen")
    archivo_pdf = models.FileField(upload_to='informes_pdf/%Y/%m/', null=True, blank=True)
    generado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_generacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Informe Generado"
        verbose_name_plural = "Informes Generados"
        ordering = ['-fecha_generacion']

    def __str__(self):
        return f"{self.titulo} - {self.cliente.nombre_razon_social}"
