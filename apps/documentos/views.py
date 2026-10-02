from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Documento
from .utils import extraer_texto_archivo
from apps.clientes.models import Cliente
from apps.procesos.models import ProcesoAsunto

def index(request):
    documentos = Documento.objects.select_related('cliente', 'proceso', 'categoria', 'subido_por').all()
    clientes = Cliente.objects.filter(estado='ACTIVO')
    procesos = ProcesoAsunto.objects.all()
    
    tipo_filtro = request.GET.get('tipo')
    if tipo_filtro:
        documentos = documentos.filter(tipo=tipo_filtro)

    cliente_id = request.GET.get('cliente_id')
    if cliente_id:
        documentos = documentos.filter(cliente_id=cliente_id)

    return render(request, 'documentos/documentos.html', {
        'documentos': documentos,
        'clientes': clientes,
        'procesos': procesos,
        'tipo_filtro': tipo_filtro,
        'cliente_id': cliente_id,
    })

def subir(request):
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente_id')
        proceso_id = request.POST.get('proceso_id') or None
        titulo = request.POST.get('titulo', '').strip()
        tipo = request.POST.get('tipo', 'OTRO')
        archivo = request.FILES.get('archivo')
        fecha_documento = request.POST.get('fecha_documento') or None
        descripcion = request.POST.get('descripcion', '').strip()

        if not cliente_id or not titulo or not archivo:
            messages.error(request, 'Cliente, título y archivo son campos requeridos.')
            return redirect('documentos:index')

        cliente = get_object_or_404(Cliente, id=cliente_id)
        proceso = ProcesoAsunto.objects.filter(id=proceso_id).first() if proceso_id else None

        doc = Documento.objects.create(
            cliente=cliente,
            proceso=proceso,
            titulo=titulo,
            tipo=tipo,
            archivo=archivo,
            fecha_documento=fecha_documento,
            descripcion=descripcion,
            subido_por=request.user if request.user.is_authenticated else None
        )

        # Extraer texto del documento
        if doc.archivo:
            try:
                texto_leido = extraer_texto_archivo(doc.archivo.path)
                if texto_leido:
                    doc.texto_extraido = texto_leido
                    doc.save()
            except Exception as e:
                print(f"Error al extraer texto: {e}")

        messages.success(request, f'Documento "{titulo}" subido, indexado y clasificado exitosamente.')
    return redirect('documentos:index')

def eliminar(request, id):
    doc = get_object_or_404(Documento, id=id)
    if request.method == 'POST':
        nombre = doc.titulo
        doc.delete()
        messages.success(request, f'Documento "{nombre}" eliminado.')
    return redirect('documentos:index')
