from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Cliente

def index(request):
    query = request.GET.get('q', '').strip()
    clientes = Cliente.objects.all()
    if query:
        clientes = clientes.filter(nombre_razon_social__icontains=query) | clientes.filter(ci_nit__icontains=query)
    
    return render(request, 'clientes/clientes.html', {
        'clientes': clientes,
        'query': query
    })

def crear(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre_razon_social', '').strip()
        ci_nit = request.POST.get('ci_nit', '').strip()
        tipo_cliente = request.POST.get('tipo_cliente', 'EMPRESA')
        empresa_relacionada = request.POST.get('empresa_relacionada', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        correo = request.POST.get('correo', '').strip()
        direccion = request.POST.get('direccion', '').strip()
        observaciones = request.POST.get('observaciones', '').strip()

        if not nombre or not ci_nit:
            messages.error(request, 'El nombre/razón social y el CI/NIT son obligatorios.')
            return redirect('clientes:index')

        Cliente.objects.create(
            nombre_razon_social=nombre,
            ci_nit=ci_nit,
            tipo_cliente=tipo_cliente,
            empresa_relacionada=empresa_relacionada,
            telefono=telefono,
            correo=correo,
            direccion=direccion,
            observaciones=observaciones,
            estado='ACTIVO'
        )
        messages.success(request, f'Cliente "{nombre}" registrado correctamente.')
    return redirect('clientes:index')

def editar(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    if request.method == 'POST':
        cliente.nombre_razon_social = request.POST.get('nombre_razon_social', cliente.nombre_razon_social).strip()
        cliente.ci_nit = request.POST.get('ci_nit', cliente.ci_nit).strip()
        cliente.tipo_cliente = request.POST.get('tipo_cliente', cliente.tipo_cliente)
        cliente.empresa_relacionada = request.POST.get('empresa_relacionada', cliente.empresa_relacionada).strip()
        cliente.telefono = request.POST.get('telefono', cliente.telefono).strip()
        cliente.correo = request.POST.get('correo', cliente.correo).strip()
        cliente.direccion = request.POST.get('direccion', cliente.direccion).strip()
        cliente.estado = request.POST.get('estado', cliente.estado)
        cliente.observaciones = request.POST.get('observaciones', cliente.observaciones).strip()
        cliente.save()
        messages.success(request, f'Cliente "{cliente.nombre_razon_social}" actualizado correctamente.')
    return redirect('clientes:index')

def eliminar(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    if request.method == 'POST':
        nombre = cliente.nombre_razon_social
        cliente.delete()
        messages.success(request, f'Cliente "{nombre}" eliminado con éxito.')
    return redirect('clientes:index')

def detalle(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    procesos = cliente.procesos.all()
    documentos = cliente.documentos.all()
    movimientos = cliente.movimientos_financieros.all()
    comprobantes = cliente.comprobantes.all()
    actividades = cliente.actividades.all()
    
    return render(request, 'clientes/detalle.html', {
        'cliente': cliente,
        'procesos': procesos,
        'documentos': documentos,
        'movimientos': movimientos,
        'comprobantes': comprobantes,
        'actividades': actividades
    })
