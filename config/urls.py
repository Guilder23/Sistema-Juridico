from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('dashboard:index')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('usuarios/', include('apps.usuarios.urls')),
    path('clientes/', include('apps.clientes.urls')),
    path('procesos/', include('apps.procesos.urls')),
    path('documentos/', include('apps.documentos.urls')),
    path('finanzas/', include('apps.finanzas.urls')),
    path('comprobantes/', include('apps.comprobantes.urls')),
    path('bitacora/', include('apps.bitacora.urls')),
    path('reportes/', include('apps.reportes.urls')),
    path('ia/', include('apps.ia_asistente.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
