from django.db import models
from django.conf import settings
from apps.clientes.models import Cliente
from apps.procesos.models import ProcesoAsunto

class PlanPago(models.Model):
    ESTADO_PLAN_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_CURSO', 'En Curso / Pagando'),
        ('COMPLETADO', 'Completado'),
        ('CANCELADO', 'Cancelado'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='planes_pago', verbose_name="Cliente")
    proceso = models.ForeignKey(ProcesoAsunto, on_delete=models.SET_NULL, null=True, blank=True, related_name='planes_pago', verbose_name="Asunto / Proceso")
    titulo = models.CharField(max_length=255, verbose_name="Título del Honorario / Plan")
    monto_total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Monto Total (Bs)")
    numero_cuotas = models.IntegerField(default=1, verbose_name="Número de Cuotas")
    fecha_inicio = models.DateField(verbose_name="Fecha de Inicio")
    estado = models.CharField(max_length=20, choices=ESTADO_PLAN_CHOICES, default='EN_CURSO')
    observaciones = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Plan de Pago"
        verbose_name_plural = "Planes de Pago en Cuotas"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.titulo} - {self.cliente.nombre_razon_social} (Bs {self.monto_total})"

    @property
    def monto_pagado(self):
        return sum(c.monto_pagado for c in self.cuotas.filter(estado='PAGADA'))

    @property
    def saldo_pendiente(self):
        return self.monto_total - self.monto_pagado


class CuotaPago(models.Model):
    ESTADO_CUOTA_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('PAGADA', 'Pagada'),
        ('VENCIDA', 'Vencida'),
    ]

    plan = models.ForeignKey(PlanPago, on_delete=models.CASCADE, related_name='cuotas', verbose_name="Plan de Pago")
    numero_cuota = models.IntegerField(verbose_name="Número de Cuota")
    monto_esperado = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Monto de la Cuota (Bs)")
    monto_pagado = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Monto Efectivamente Pagado (Bs)")
    fecha_vencimiento = models.DateField(verbose_name="Fecha de Vencimiento")
    fecha_pago = models.DateField(null=True, blank=True, verbose_name="Fecha de Pago Real")
    estado = models.CharField(max_length=20, choices=ESTADO_CUOTA_CHOICES, default='PENDIENTE')
    comprobante_o_ref = models.CharField(max_length=100, blank=True, null=True, verbose_name="Referencia / N° Recibo")
    registrado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cuota de Pago"
        verbose_name_plural = "Cuotas de Pago"
        ordering = ['plan', 'numero_cuota']

    def __str__(self):
        return f"Cuota #{self.numero_cuota} de {self.plan.titulo} - Bs {self.monto_esperado} ({self.get_estado_display()})"


class MovimientoFinanciero(models.Model):
    TIPO_CHOICES = [
        ('FONDO_RECIBIDO', 'Fondo Recibido del Cliente'),
        ('PAGO_CUOTA_HONORARIO', 'Pago de Cuota / Honorario'),
        ('GASTO_FONDO_CLIENTE', 'Gasto con Fondo del Cliente'),
        ('GASTO_PROPIO', 'Gasto Propio (Pendiente Reembolso)'),
        ('REEMBOLSO_RECIBIDO', 'Reembolso Recibido'),
        ('DEVOLUCION_SALDO', 'Devolución de Saldo al Cliente'),
    ]

    METODO_PAGO_CHOICES = [
        ('EFECTIVO', 'Efectivo'),
        ('TRANSFERENCIA', 'Transferencia Bancaria'),
        ('QR', 'Pago QR / Móvil'),
        ('TARJETA', 'Tarjeta'),
        ('OTRO', 'Otro'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='movimientos_financieros', verbose_name="Cliente")
    proceso = models.ForeignKey(ProcesoAsunto, on_delete=models.SET_NULL, null=True, blank=True, related_name='movimientos_financieros', verbose_name="Proceso / Asunto")
    cuota = models.ForeignKey(CuotaPago, on_delete=models.SET_NULL, null=True, blank=True, related_name='movimientos', verbose_name="Cuota Vinculada")
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES, verbose_name="Tipo de Movimiento")
    concepto = models.CharField(max_length=255, verbose_name="Concepto / Razón del gasto o ingreso")
    monto = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Monto (Bs)")
    moneda = models.CharField(max_length=10, default='BOB', verbose_name="Moneda")
    fecha = models.DateField(verbose_name="Fecha")
    metodo_pago = models.CharField(max_length=30, choices=METODO_PAGO_CHOICES, default='EFECTIVO')
    pagado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pagos_realizados',
        verbose_name="Pagado / Registrado por"
    )
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones / Detalle")
    reembolsado = models.BooleanField(default=False, verbose_name="¿Reembolsado?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Movimiento Financiero"
        verbose_name_plural = "Movimientos Financieros"
        ordering = ['-fecha', '-created_at']

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.concepto} (Bs {self.monto}) - {self.cliente.nombre_razon_social}"
