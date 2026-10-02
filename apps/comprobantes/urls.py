from django.urls import path
from . import views

app_name = 'comprobantes'

urlpatterns = [
    path('', views.index, name='index'),
    path('subir/', views.subir, name='subir'),
    path('eliminar/<int:id>/', views.eliminar, name='eliminar'),
]
