from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import BitacoraActividad
from apps.clientes.models import Cliente
from apps.procesos.models import ProcesoAsunto

def index(request):
    actividades = BitacoraActividad.objects.select_related('cliente', 'proceso', 'usuario').all()
    clientes = Cliente.objects.filter(estado='ACTIVO')
    procesos = ProcesoAsunto.objects.all()

    cliente_id = request.GET.get('cliente_id')
    if cliente_id:
        actividades = actividades.filter(cliente_id=cliente_id)

    return render(request, 'bitacora/bitacora.html', {
        'actividades': actividades,
        'clientes': clientes,
        'procesos': procesos,
        'cliente_id': cliente_id,
    })

def crear(request):
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente_id')
        proceso_id = request.POST.get('proceso_id') or None
        tipo = request.POST.get('tipo', 'OTRO')
        titulo = request.POST.get('titulo', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        fecha_actividad = request.POST.get('fecha_actividad')

        if not cliente_id or not titulo or not fecha_actividad:
            messages.error(request, 'Cliente, título y fecha del suceso son requeridos.')
            return redirect('bitacora:index')

        cliente = get_object_or_404(Cliente, id=cliente_id)
        proceso = ProcesoAsunto.objects.filter(id=proceso_id).first() if proceso_id else None

        BitacoraActividad.objects.create(
            cliente=cliente,
            proceso=proceso,
            tipo=tipo,
            titulo=titulo,
            descripcion=descripcion,
            fecha_actividad=fecha_actividad,
            usuario=request.user if request.user.is_authenticated else None
        )
        messages.success(request, 'Actividad registrada en la línea de tiempo de la bitácora.')
    return redirect('bitacora:index')

def eliminar(request, id):
    act = get_object_or_404(BitacoraActividad, id=id)
    if request.method == 'POST':
        act.delete()
        messages.success(request, 'Entrada de bitácora eliminada.')
    return redirect('bitacora:index')
