from django.urls import path
from . import views

app_name = 'ia_asistente'

urlpatterns = [
    path('', views.index, name='index'),
    path('consultar/', views.consultar_rag, name='consultar_rag'),
    path('expediente/<int:cliente_id>/', views.generar_expediente_documental_ia, name='expediente_ia'),
]
