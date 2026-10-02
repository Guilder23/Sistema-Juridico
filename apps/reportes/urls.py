from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('', views.index, name='index'),
    path('generar/', views.generar, name='generar'),
    path('imprimir/<int:id>/', views.descargar_pdf_print, name='imprimir'),
    path('eliminar/<int:id>/', views.eliminar, name='eliminar'),
]
