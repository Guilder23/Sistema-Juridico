from django.shortcuts import render
from django.db.models import Sum
from apps.clientes.models import Cliente
from apps.procesos.models import ProcesoAsunto
from apps.documentos.models import Documento
from apps.finanzas.models import MovimientoFinanciero
from apps.bitacora.models import BitacoraActividad
from apps.usuarios.google_integration import (
    get_google_account_connected,
    list_google_calendar_events,
    list_google_drive_documents,
)


def index(request):
    total_clientes = Cliente.objects.filter(estado='ACTIVO').count()
    procesos_en_proceso = ProcesoAsunto.objects.filter(estado='EN_PROCESO').count()
    procesos_pendientes = ProcesoAsunto.objects.filter(estado='PENDIENTE').count()
    total_documentos = Documento.objects.count()

    gastos_agg = MovimientoFinanciero.objects.filter(tipo__in=['GASTO_FONDO_CLIENTE', 'GASTO_PROPIO']).aggregate(total=Sum('monto'))
    total_gastos = gastos_agg['total'] or 0

    fondos_agg = MovimientoFinanciero.objects.filter(tipo='FONDO_RECIBIDO').aggregate(total=Sum('monto'))
    total_fondos = fondos_agg['total'] or 0

    reembolsos_pendientes_agg = MovimientoFinanciero.objects.filter(tipo='GASTO_PROPIO', reembolsado=False).aggregate(total=Sum('monto'))
    total_reembolso_pendiente = reembolsos_pendientes_agg['total'] or 0

    ultimos_procesos = ProcesoAsunto.objects.select_related('cliente').order_by('-updated_at')[:5]
    ultimas_actividades = BitacoraActividad.objects.select_related('cliente', 'usuario').order_by('-fecha_actividad', '-created_at')[:6]

    google_connected = get_google_account_connected(request.user)
    google_events = []
    google_documents = []
    google_error = None

    if google_connected:
        try:
            google_events = list_google_calendar_events(request.user, limit=5)
            google_documents = list_google_drive_documents(request.user, limit=5)
        except Exception as exc:  # pragma: no cover - protección para cuenta sin permisos
            google_error = str(exc)

    context = {
        'total_clientes': total_clientes,
        'procesos_en_proceso': procesos_en_proceso,
        'procesos_pendientes': procesos_pendientes,
        'total_documentos': total_documentos,
        'total_gastos': total_gastos,
        'total_fondos': total_fondos,
        'total_reembolso_pendiente': total_reembolso_pendiente,
        'ultimos_procesos': ultimos_procesos,
        'ultimas_actividades': ultimas_actividades,
        'google_connected': google_connected,
        'google_events': google_events,
        'google_documents': google_documents,
        'google_error': google_error,
    }
    return render(request, 'dashboard/dashboard.html', context)
