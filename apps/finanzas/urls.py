from django.urls import path
from . import views

app_name = 'finanzas'

urlpatterns = [
    path('', views.index, name='index'),
    path('crear/', views.crear, name='crear'),
    path('plan/crear/', views.crear_plan_cuotas, name='crear_plan'),
    path('cuota/pagar/<int:cuota_id>/', views.pagar_cuota, name='pagar_cuota'),
    path('reembolsar/<int:id>/', views.marcar_reembolsado, name='reembolsar'),
    path('eliminar/<int:id>/', views.eliminar, name='eliminar'),
]
