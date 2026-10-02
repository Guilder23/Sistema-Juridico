import os
import json
from datetime import date, datetime
from decimal import Decimal
from django.shortcuts import render
from django.http import JsonResponse
from groq import Groq
from apps.clientes.models import Cliente
from apps.procesos.models import ProcesoAsunto
from apps.finanzas.models import MovimientoFinanciero, PlanPago
from apps.bitacora.models import BitacoraActividad
from apps.documentos.models import Documento

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def get_groq_client():
    groq_api_key = os.getenv('GROQ_API_KEY')
    if not groq_api_key:
        return None
    return Groq(api_key=groq_api_key)

def index(request):
    clientes = Cliente.objects.filter(estado='ACTIVO')
    cliente_seleccionado_id = request.GET.get('cliente_id')
    cliente_seleccionado = None
    if cliente_seleccionado_id:
        cliente_seleccionado = Cliente.objects.filter(id=cliente_seleccionado_id).first()

    return render(request, 'ia_asistente/ia_asistente.html', {
        'clientes': clientes,
        'cliente_seleccionado': cliente_seleccionado,
    })

def consultar_rag(request):
    """Chatbot General o Específico con Groq openai/gpt-oss-20b leyendo contenido real de documentos"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            pregunta = data.get('pregunta', '').strip()
            cliente_id = data.get('cliente_id')

            if not pregunta:
                return JsonResponse({'error': 'La consulta no puede estar vacía'}, status=400)

            client = get_groq_client()
            if not client:
                return JsonResponse({'error': 'GROQ_API_KEY no configurada'}, status=500)

            contexto_sistema = (
                "Eres el Asistente Jurídico y Documental Inteligente de LexDocs IA. "
                "Tienes acceso al texto real de los documentos subidos (contratos, informes, memoriales), cuotas, finanzas y bitácora. "
                "Responde de manera ejecutiva, clara y en español. NO uses emojis bajo ninguna circunstancia. Usa Markdown limpio con listas y negritas."
            )

            contexto_datos = ""

            if cliente_id:
                cliente = Cliente.objects.filter(id=cliente_id).first()
                if cliente:
                    procesos = list(cliente.procesos.values('titulo', 'estado', 'prioridad', 'fecha_limite', 'descripcion'))
                    
                    # Documentos con su texto real extraído
                    documentos = []
                    for d in cliente.documentos.all():
                        documentos.append({
                            'titulo': d.titulo,
                            'tipo': d.get_tipo_display(),
                            'extension': d.extension,
                            'fecha_documento': d.fecha_documento,
                            'descripcion': d.descripcion,
                            'contenido_textual_del_archivo': (d.texto_extraido[:3500] + '...') if d.texto_extraido and len(d.texto_extraido) > 3500 else (d.texto_extraido or 'Documento sin texto legible')
                        })

                    movimientos = list(cliente.movimientos_financieros.values('tipo', 'concepto', 'monto', 'fecha', 'reembolsado', 'metodo_pago'))
                    
                    planes_pago = []
                    for pl in cliente.planes_pago.all():
                        cuotas_info = list(pl.cuotas.values('numero_cuota', 'monto_esperado', 'monto_pagado', 'estado', 'fecha_vencimiento', 'fecha_pago'))
                        planes_pago.append({
                            'titulo': pl.titulo,
                            'monto_total': float(pl.monto_total),
                            'numero_cuotas': pl.numero_cuotas,
                            'estado': pl.estado,
                            'cuotas': cuotas_info
                        })
                    actividades = list(cliente.actividades.values('fecha_actividad', 'tipo', 'titulo', 'descripcion')[:20])

                    contexto_datos = f"""
EXPEDIENTE EXCLUSIVO DEL CLIENTE:
- Nombre / Razón Social: {cliente.nombre_razon_social} (NIT/CI: {cliente.ci_nit})
- Tipo: {cliente.get_tipo_cliente_display()} | Estado: {cliente.get_estado_display()}

PLANES DE PAGO EN CUOTAS:
{json.dumps(planes_pago, indent=2, ensure_ascii=False, cls=CustomJSONEncoder)}

ASUNTOS Y PROCESOS:
{json.dumps(procesos, indent=2, ensure_ascii=False, cls=CustomJSONEncoder)}

DOCUMENTOS Y CONTENIDO REAL DE ARCHIVOS SUBIDOS:
{json.dumps(documentos, indent=2, ensure_ascii=False, cls=CustomJSONEncoder)}

MOVIMIENTOS FINANCIEROS Y GASTOS:
{json.dumps(movimientos, indent=2, ensure_ascii=False, cls=CustomJSONEncoder)}

BITÁCORA / HISTORIAL:
{json.dumps(actividades, indent=2, ensure_ascii=False, cls=CustomJSONEncoder)}
"""
            else:
                total_clientes = Cliente.objects.count()
                clientes_resumen = list(Cliente.objects.values('id', 'nombre_razon_social', 'ci_nit', 'estado')[:20])
                procesos_activos = list(ProcesoAsunto.objects.filter(estado__in=['EN_PROCESO', 'PENDIENTE']).values('titulo', 'cliente__nombre_razon_social', 'estado', 'prioridad'))
                
                contexto_datos = f"""
PANORAMA GENERAL DEL SISTEMA:
- Total Clientes: {total_clientes}
- Clientes Registrados: {json.dumps(clientes_resumen, ensure_ascii=False)}
- Asuntos Activos Globales: {json.dumps(procesos_activos, ensure_ascii=False)}
"""

            mensajes = [
                {"role": "system", "content": contexto_sistema},
                {"role": "system", "content": f"Contexto disponible:\n{contexto_datos}"},
                {"role": "user", "content": pregunta}
            ]

            chat_completion = client.chat.completions.create(
                messages=mensajes,
                model="openai/gpt-oss-20b",
                temperature=0.3,
            )

            return JsonResponse({
                'respuesta': chat_completion.choices[0].message.content,
                'cliente': cliente.nombre_razon_social if cliente_id and cliente else 'General'
            })

        except Exception as e:
            return JsonResponse({'error': f"Error en Groq: {str(e)}"}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)


def generar_expediente_documental_ia(request, cliente_id):
    """La IA compila un expediente formal analizando el CONTENIDO REAL de los documentos del cliente."""
    if request.method == 'POST':
        try:
            cliente = Cliente.objects.filter(id=cliente_id).first()
            if not cliente:
                return JsonResponse({'error': 'Cliente no encontrado'}, status=404)

            client = get_groq_client()
            if not client:
                return JsonResponse({'error': 'GROQ_API_KEY no configurada'}, status=500)

            # Extraer documentos con su contenido real
            documentos = []
            for d in cliente.documentos.all():
                documentos.append({
                    'titulo': d.titulo,
                    'tipo': d.get_tipo_display(),
                    'extension': d.extension,
                    'fecha_documento': d.fecha_documento,
                    'descripcion': d.descripcion,
                    'texto_completo_del_documento': d.texto_extraido or 'Sin contenido legible'
                })

            procesos = list(cliente.procesos.values('titulo', 'estado', 'prioridad', 'fecha_inicio', 'fecha_limite', 'descripcion'))
            actividades = list(cliente.actividades.values('fecha_actividad', 'tipo', 'titulo', 'descripcion'))

            prompt_expediente = f"""
Actúa como un Auditor Legal Senior. Genera un EXPEDIENTE JURÍDICO Y DOCUMENTAL COMPLETO Y FORMAL para el cliente {cliente.nombre_razon_social} (NIT/CI: {cliente.ci_nit}).

Analiza a fondo el CONTENIDO REAL de los siguientes documentos subidos:

DOCUMENTOS EN CUSTODIA Y SU CONTENIDO INTERNO ({len(documentos)} archivos):
{json.dumps(documentos, indent=2, ensure_ascii=False, cls=CustomJSONEncoder)}

PROCESOS Y ASUNTOS ASOCIADOS:
{json.dumps(procesos, indent=2, ensure_ascii=False, cls=CustomJSONEncoder)}

BITÁCORA / LÍNEA DE TIEMPO:
{json.dumps(actividades, indent=2, ensure_ascii=False, cls=CustomJSONEncoder)}

Estructura requerida:
1. PERFIL E IDENTIFICACIÓN DEL CLIENTE
2. RESUMEN EJECUTIVO Y ESTADO DE SUS ASUNTOS
3. INVENTARIO Y ANÁLISIS DE CONTENIDO DE CADA DOCUMENTO (Menciona cláusulas, acuerdos, partes o datos clave encontrados dentro de los textos)
4. LÍNEA CRONOLÓGICA DE ACTUACIONES
5. DICTAMEN DE REGULARIZACIÓN Y DOCUMENTACIÓN FALTANTE

Reglas:
- NO uses emojis.
- Redacción jurídica rigurosa en Markdown.
"""

            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Eres un auditor legal y redactor de expedientes jurídicos y documentales en español."},
                    {"role": "user", "content": prompt_expediente}
                ],
                model="openai/gpt-oss-20b",
                temperature=0.2,
            )

            expediente_generado = chat_completion.choices[0].message.content

            return JsonResponse({
                'expediente': expediente_generado,
                'cliente': cliente.nombre_razon_social,
                'total_documentos': len(documentos)
            })

        except Exception as e:
            return JsonResponse({'error': f"Error al generar expediente con IA: {str(e)}"}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)
