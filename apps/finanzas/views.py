from datetime import date, timedelta
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum
from .models import MovimientoFinanciero, PlanPago, CuotaPago
from apps.clientes.models import Cliente
from apps.procesos.models import ProcesoAsunto

def index(request):
    movimientos = MovimientoFinanciero.objects.select_related('cliente', 'proceso', 'pagado_por', 'cuota').all()
    planes_pago = PlanPago.objects.select_related('cliente', 'proceso').prefetch_related('cuotas').all()
    clientes = Cliente.objects.filter(estado='ACTIVO')
    procesos = ProcesoAsunto.objects.all()

    cliente_id = request.GET.get('cliente_id')
    if cliente_id:
        movimientos = movimientos.filter(cliente_id=cliente_id)
        planes_pago = planes_pago.filter(cliente_id=cliente_id)

    tipo_filtro = request.GET.get('tipo')
    if tipo_filtro:
        movimientos = movimientos.filter(tipo=tipo_filtro)

    # Métricas
    fondos = movimientos.filter(tipo='FONDO_RECIBIDO').aggregate(Sum('monto'))['monto__sum'] or 0
    honorarios_cobrados = movimientos.filter(tipo='PAGO_CUOTA_HONORARIO').aggregate(Sum('monto'))['monto__sum'] or 0
    gastos_cliente = movimientos.filter(tipo='GASTO_FONDO_CLIENTE').aggregate(Sum('monto'))['monto__sum'] or 0
    pendientes_reembolso = movimientos.filter(tipo='GASTO_PROPIO', reembolsado=False).aggregate(Sum('monto'))['monto__sum'] or 0
    saldo_fondo_cliente = fondos - gastos_cliente

    return render(request, 'finanzas/finanzas.html', {
        'movimientos': movimientos,
        'planes_pago': planes_pago,
        'clientes': clientes,
        'procesos': procesos,
        'cliente_id': cliente_id,
        'tipo_filtro': tipo_filtro,
        'fondos': fondos,
        'honorarios_cobrados': honorarios_cobrados,
        'gastos_cliente': gastos_cliente,
        'pendientes_reembolso': pendientes_reembolso,
        'saldo_fondo_cliente': saldo_fondo_cliente
    })

def crear_plan_cuotas(request):
    """Crea un plan de pago y genera automáticamente las cuotas individuales"""
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente_id')
        proceso_id = request.POST.get('proceso_id') or None
        titulo = request.POST.get('titulo', '').strip()
        monto_total = Decimal(request.POST.get('monto_total', 0))
        numero_cuotas = int(request.POST.get('numero_cuotas', 1))
        fecha_inicio_str = request.POST.get('fecha_inicio')
        intervalo_dias = int(request.POST.get('intervalo_dias', 30))
        observaciones = request.POST.get('observaciones', '').strip()

        if not cliente_id or not titulo or monto_total <= 0 or numero_cuotas <= 0 or not fecha_inicio_str:
            messages.error(request, 'Datos incompletos para crear el plan de cuotas.')
            return redirect('finanzas:index')

        cliente = get_object_or_404(Cliente, id=cliente_id)
        proceso = ProcesoAsunto.objects.filter(id=proceso_id).first() if proceso_id else None
        fecha_inicio = date.fromisoformat(fecha_inicio_str)

        plan = PlanPago.objects.create(
            cliente=cliente,
            proceso=proceso,
            titulo=titulo,
            monto_total=monto_total,
            numero_cuotas=numero_cuotas,
            fecha_inicio=fecha_inicio,
            observaciones=observaciones
        )

        monto_por_cuota = round(monto_total / Decimal(numero_cuotas), 2)
        diferencia = monto_total - (monto_por_cuota * Decimal(numero_cuotas))

        for i in range(1, numero_cuotas + 1):
            monto_cuota = monto_por_cuota
            if i == numero_cuotas:
                monto_cuota += diferencia  # Ajustar cualquier céntimo restante en la última cuota

            vencimiento = fecha_inicio + timedelta(days=(i - 1) * intervalo_dias)
            CuotaPago.objects.create(
                plan=plan,
                numero_cuota=i,
                monto_esperado=monto_cuota,
                fecha_vencimiento=vencimiento,
                estado='PENDIENTE'
            )

        messages.success(request, f'Plan de {numero_cuotas} cuotas creado exitosamente para {cliente.nombre_razon_social}.')
    return redirect('finanzas:index')

def pagar_cuota(request, cuota_id):
    """Registra el cobro de una cuota de honorario"""
    cuota = get_object_or_404(CuotaPago, id=cuota_id)
    if request.method == 'POST':
        monto_pagado = Decimal(request.POST.get('monto_pagado', cuota.monto_esperado))
        fecha_pago_str = request.POST.get('fecha_pago') or date.today().isoformat()
        metodo_pago = request.POST.get('metodo_pago', 'TRANSFERENCIA')
        comprobante_ref = request.POST.get('comprobante_ref', '').strip()

        cuota.monto_pagado = monto_pagado
        cuota.fecha_pago = date.fromisoformat(fecha_pago_str)
        cuota.comprobante_o_ref = comprobante_ref
        cuota.estado = 'PAGADA'
        cuota.registrado_por = request.user if request.user.is_authenticated else None
        cuota.save()

        # Registrar el movimiento financiero
        MovimientoFinanciero.objects.create(
            cliente=cuota.plan.cliente,
            proceso=cuota.plan.proceso,
            cuota=cuota,
            tipo='PAGO_CUOTA_HONORARIO',
            concepto=f"Cobro Cuota #{cuota.numero_cuota}/{cuota.plan.numero_cuotas} - {cuota.plan.titulo} (Ref: {comprobante_ref or 'S/R'})",
            monto=monto_pagado,
            fecha=cuota.fecha_pago,
            metodo_pago=metodo_pago,
            pagado_por=request.user if request.user.is_authenticated else None
        )

        # Verificar si se completó el plan
        if cuota.plan.saldo_pendiente <= 0:
            cuota.plan.estado = 'COMPLETADO'
            cuota.plan.save()

        messages.success(request, f'Cuota #{cuota.numero_cuota} cobrada por Bs {monto_pagado}.')
    return redirect('finanzas:index')

def crear(request):
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente_id')
        proceso_id = request.POST.get('proceso_id') or None
        tipo = request.POST.get('tipo', 'GASTO_PROPIO')
        concepto = request.POST.get('concepto', '').strip()
        monto = request.POST.get('monto', 0)
        fecha = request.POST.get('fecha')
        metodo_pago = request.POST.get('metodo_pago', 'EFECTIVO')
        observaciones = request.POST.get('observaciones', '').strip()

        if not cliente_id or not concepto or not monto or not fecha:
            messages.error(request, 'Complete los campos obligatorios.')
            return redirect('finanzas:index')

        cliente = get_object_or_404(Cliente, id=cliente_id)
        proceso = ProcesoAsunto.objects.filter(id=proceso_id).first() if proceso_id else None

        MovimientoFinanciero.objects.create(
            cliente=cliente,
            proceso=proceso,
            tipo=tipo,
            concepto=concepto,
            monto=monto,
            fecha=fecha,
            metodo_pago=metodo_pago,
            pagado_por=request.user if request.user.is_authenticated else None,
            observaciones=observaciones
        )
        messages.success(request, f'Movimiento por Bs {monto} registrado.')
    return redirect('finanzas:index')

def marcar_reembolsado(request, id):
    mov = get_object_or_404(MovimientoFinanciero, id=id)
    if request.method == 'POST':
        mov.reembolsado = not mov.reembolsado
        mov.save()
        messages.success(request, f'Reembolso actualizado para "{mov.concepto}".')
    return redirect('finanzas:index')

def eliminar(request, id):
    mov = get_object_or_404(MovimientoFinanciero, id=id)
    if request.method == 'POST':
        mov.delete()
        messages.success(request, 'Movimiento eliminado.')
    return redirect('finanzas:index')
