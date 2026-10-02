from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Comprobante
from apps.clientes.models import Cliente
from apps.procesos.models import ProcesoAsunto
from apps.finanzas.models import MovimientoFinanciero

def index(request):
    comprobantes = Comprobante.objects.select_related('cliente', 'proceso', 'movimiento_financiero', 'subido_por').all()
    clientes = Cliente.objects.filter(estado='ACTIVO')
    procesos = ProcesoAsunto.objects.all()

    return render(request, 'comprobantes/comprobantes.html', {
        'comprobantes': comprobantes,
        'clientes': clientes,
        'procesos': procesos,
    })

def subir(request):
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente_id')
        proceso_id = request.POST.get('proceso_id') or None
        tipo = request.POST.get('tipo', 'FACTURA')
        numero = request.POST.get('numero_comprobante', '').strip()
        proveedor = request.POST.get('proveedor_emisor', '').strip()
        nit_emisor = request.POST.get('nit_emisor', '').strip()
        monto = request.POST.get('monto', 0)
        fecha_emision = request.POST.get('fecha_emision') or None
        concepto = request.POST.get('concepto', '').strip()
        imagen = request.FILES.get('imagen')
        registrar_gasto = request.POST.get('registrar_gasto') == 'on'

        if not cliente_id or not monto or not imagen:
            messages.error(request, 'Cliente, monto e imagen/fotografía son obligatorios.')
            return redirect('comprobantes:index')

        cliente = get_object_or_404(Cliente, id=cliente_id)
        proceso = ProcesoAsunto.objects.filter(id=proceso_id).first() if proceso_id else None

        movimiento = None
        if registrar_gasto and fecha_emision:
            movimiento = MovimientoFinanciero.objects.create(
                cliente=cliente,
                proceso=proceso,
                tipo='GASTO_PROPIO',
                concepto=f"{tipo}: {proveedor or concepto or 'Gasto registrado con comprobante'}",
                monto=monto,
                fecha=fecha_emision,
                pagado_por=request.user if request.user.is_authenticated else None
            )

        Comprobante.objects.create(
            cliente=cliente,
            proceso=proceso,
            movimiento_financiero=movimiento,
            tipo=tipo,
            numero_comprobante=numero,
            proveedor_emisor=proveedor,
            nit_emisor=nit_emisor,
            monto=monto,
            fecha_emision=fecha_emision,
            concepto=concepto,
            imagen=imagen,
            subido_por=request.user if request.user.is_authenticated else None,
            estado_validacion='VERIFICADO'
        )
        messages.success(request, 'Comprobante y fotografía guardados exitosamente.')
    return redirect('comprobantes:index')

def eliminar(request, id):
    comp = get_object_or_404(Comprobante, id=id)
    if request.method == 'POST':
        comp.delete()
        messages.success(request, 'Comprobante eliminado con éxito.')
    return redirect('comprobantes:index')
