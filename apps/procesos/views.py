from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import ProcesoAsunto
from apps.clientes.models import Cliente
from apps.usuarios.models import Usuario

def index(request):
    procesos = ProcesoAsunto.objects.select_related('cliente', 'responsable').all()
    clientes = Cliente.objects.filter(estado='ACTIVO')
    usuarios = Usuario.objects.filter(is_active=True)
    
    estado_filtro = request.GET.get('estado')
    if estado_filtro:
        procesos = procesos.filter(estado=estado_filtro)

    return render(request, 'procesos/procesos.html', {
        'procesos': procesos,
        'clientes': clientes,
        'usuarios': usuarios,
        'estado_filtro': estado_filtro
    })

def crear(request):
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente_id')
        titulo = request.POST.get('titulo', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        estado = request.POST.get('estado', 'EN_PROCESO')
        prioridad = request.POST.get('prioridad', 'MEDIA')
        responsable_id = request.POST.get('responsable_id') or None
        fecha_inicio = request.POST.get('fecha_inicio') or None
        fecha_limite = request.POST.get('fecha_limite') or None
        observaciones = request.POST.get('observaciones', '').strip()

        if not cliente_id or not titulo:
            messages.error(request, 'El cliente y el título son obligatorios.')
            return redirect('procesos:index')

        cliente = get_object_or_404(Cliente, id=cliente_id)
        responsable = Usuario.objects.filter(id=responsable_id).first() if responsable_id else None

        ProcesoAsunto.objects.create(
            cliente=cliente,
            titulo=titulo,
            descripcion=descripcion,
            estado=estado,
            prioridad=prioridad,
            responsable=responsable,
            fecha_inicio=fecha_inicio,
            fecha_limite=fecha_limite,
            observaciones=observaciones
        )
        messages.success(request, f'Proceso "{titulo}" creado exitosamente.')
    return redirect('procesos:index')

def editar(request, id):
    proceso = get_object_or_404(ProcesoAsunto, id=id)
    if request.method == 'POST':
        proceso.titulo = request.POST.get('titulo', proceso.titulo).strip()
        proceso.descripcion = request.POST.get('descripcion', proceso.descripcion).strip()
        proceso.estado = request.POST.get('estado', proceso.estado)
        proceso.prioridad = request.POST.get('prioridad', proceso.prioridad)
        
        responsable_id = request.POST.get('responsable_id')
        proceso.responsable = Usuario.objects.filter(id=responsable_id).first() if responsable_id else None
        
        proceso.fecha_inicio = request.POST.get('fecha_inicio') or None
        proceso.fecha_limite = request.POST.get('fecha_limite') or None
        proceso.observaciones = request.POST.get('observaciones', proceso.observaciones).strip()
        proceso.save()
        messages.success(request, f'Proceso "{proceso.titulo}" actualizado.')
    return redirect('procesos:index')

def eliminar(request, id):
    proceso = get_object_or_404(ProcesoAsunto, id=id)
    if request.method == 'POST':
        titulo = proceso.titulo
        proceso.delete()
        messages.success(request, f'Proceso "{titulo}" eliminado.')
    return redirect('procesos:index')
