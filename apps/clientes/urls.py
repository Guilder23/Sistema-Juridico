from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    path('', views.index, name='index'),
    path('crear/', views.crear, name='crear'),
    path('editar/<int:id>/', views.editar, name='editar'),
    path('eliminar/<int:id>/', views.eliminar, name='eliminar'),
    path('<int:id>/', views.detalle, name='detalle'),
]
