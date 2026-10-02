from django.db import models
from django.conf import settings
from apps.clientes.models import Cliente
from apps.procesos.models import ProcesoAsunto

class CategoriaDocumento(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Categoría de Documento"
        verbose_name_plural = "Categorías de Documentos"

    def __str__(self):
        return self.nombre

class Documento(models.Model):
    TIPO_CHOICES = [
        ('CONTRATO', 'Contrato'),
        ('COMPROBANTE', 'Comprobante'),
        ('INFORME', 'Informe'),
        ('ESCANEO', 'Escaneo'),
        ('FOTOGRAFIA', 'Fotografía'),
        ('NOTA', 'Nota'),
        ('LEGAL', 'Documento Legal / Trámite'),
        ('OTRO', 'Otro'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='documentos', verbose_name="Cliente")
    proceso = models.ForeignKey(ProcesoAsunto, on_delete=models.SET_NULL, null=True, blank=True, related_name='documentos', verbose_name="Proceso / Asunto")
    categoria = models.ForeignKey(CategoriaDocumento, on_delete=models.SET_NULL, null=True, blank=True, related_name='documentos')
    titulo = models.CharField(max_length=255, verbose_name="Título / Nombre del documento")
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES, default='OTRO')
    archivo = models.FileField(upload_to='documentos/%Y/%m/', verbose_name="Archivo")
    extension = models.CharField(max_length=20, blank=True, null=True)
    tamano_bytes = models.BigIntegerField(default=0)
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción / Notas")
    texto_extraido = models.TextField(blank=True, null=True, verbose_name="Texto Extraído del Archivo")
    fecha_documento = models.DateField(null=True, blank=True, verbose_name="Fecha del Documento")
    subido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documentos_subidos',
        verbose_name="Subido por"
    )
    fecha_subida = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"
        ordering = ['-fecha_subida']

    def __str__(self):
        return f"{self.titulo} ({self.cliente.nombre_razon_social})"

    def save(self, *args, **kwargs):
        if self.archivo:
            import os
            self.extension = os.path.splitext(self.archivo.name)[1].lower()
            try:
                self.tamano_bytes = self.archivo.size
            except Exception:
                pass
        super().save(*args, **kwargs)
