from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from .models import ReporteGenerado
from apps.clientes.models import Cliente
from apps.procesos.models import ProcesoAsunto
from apps.finanzas.models import MovimientoFinanciero
from apps.bitacora.models import BitacoraActividad

def index(request):
    reportes = ReporteGenerado.objects.select_related('cliente', 'proceso', 'generado_por').all()
    clientes = Cliente.objects.filter(estado='ACTIVO')
    procesos = ProcesoAsunto.objects.all()

    return render(request, 'reportes/reportes.html', {
        'reportes': reportes,
        'clientes': clientes,
        'procesos': procesos,
    })

def generar(request):
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente_id')
        proceso_id = request.POST.get('proceso_id') or None
        tipo = request.POST.get('tipo', 'INFORME_GESTION')
        titulo = request.POST.get('titulo', '').strip()
        periodo_inicio = request.POST.get('periodo_inicio') or None
        periodo_fin = request.POST.get('periodo_fin') or None

        if not cliente_id or not titulo:
            messages.error(request, 'Cliente y título del informe son obligatorios.')
            return redirect('reportes:index')

        cliente = get_object_or_404(Cliente, id=cliente_id)
        proceso = ProcesoAsunto.objects.filter(id=proceso_id).first() if proceso_id else None

        # Compilar contenido del informe automáticamente
        contenido = f"""# INFORME DE GESTIÓN & SEGUIMIENTO
Cliente: {cliente.nombre_razon_social} (NIT/CI: {cliente.ci_nit})
Tipo de Informe: {tipo}
Período: {periodo_inicio or 'Inicio'} a {periodo_fin or 'Actual'}

1. PROCESOS Y ASUNTOS:
Total registrados: {cliente.procesos.count()}

2. FONDOS Y GASTOS:
Fondos recibidos del cliente: Bs {sum([m.monto for m in cliente.movimientos_financieros.filter(tipo='FONDO_RECIBIDO')])}
Gastos ejecutados con fondos de cliente: Bs {sum([m.monto for m in cliente.movimientos_financieros.filter(tipo='GASTO_FONDO_CLIENTE')])}
Gastos con fondos propios (por reembolsar): Bs {sum([m.monto for m in cliente.movimientos_financieros.filter(tipo='GASTO_PROPIO', reembolsado=False)])}

3. BITÁCORA DE ACTIVIDADES:
Últimas actividades registradas: {cliente.actividades.count()} sucesos cronológicos.
"""

        ReporteGenerado.objects.create(
            cliente=cliente,
            proceso=proceso,
            titulo=titulo,
            tipo=tipo,
            periodo_inicio=periodo_inicio,
            periodo_fin=periodo_fin,
            contenido=contenido,
            generado_por=request.user if request.user.is_authenticated else None
        )
        messages.success(request, f'Informe "{titulo}" compilado exitosamente.')
    return redirect('reportes:index')

def descargar_pdf_print(request, id):
    reporte = get_object_or_404(ReporteGenerado, id=id)
    return render(request, 'reportes/pdf_template.html', {'reporte': reporte})

def eliminar(request, id):
    rep = get_object_or_404(ReporteGenerado, id=id)
    if request.method == 'POST':
        rep.delete()
        messages.success(request, 'Informe eliminado.')
    return redirect('reportes:index')
