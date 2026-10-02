from django.db import models

class Cliente(models.Model):
    TIPO_CLIENTE_CHOICES = [
        ('EMPRESA', 'Empresa / Persona Jurídica'),
        ('INDIVIDUAL', 'Persona Natural / Individual'),
    ]

    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
        ('SUSPENDIDO', 'Suspendido'),
    ]

    nombre_razon_social = models.CharField(max_length=255, verbose_name="Nombre o Razón Social")
    ci_nit = models.CharField(max_length=50, verbose_name="CI / NIT", db_index=True)
    tipo_cliente = models.CharField(max_length=20, choices=TIPO_CLIENTE_CHOICES, default='EMPRESA')
    empresa_relacionada = models.CharField(max_length=255, blank=True, null=True, verbose_name="Empresa Relacionada")
    telefono = models.CharField(max_length=50, blank=True, null=True, verbose_name="Teléfono / Celular")
    correo = models.EmailField(blank=True, null=True, verbose_name="Correo Electrónico")
    direccion = models.TextField(blank=True, null=True, verbose_name="Dirección")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='ACTIVO')
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones")
    fecha_registro = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['-fecha_registro']

    def __str__(self):
        return f"{self.nombre_razon_social} ({self.ci_nit})"
