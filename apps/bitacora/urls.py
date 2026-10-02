from django.urls import path
from . import views

app_name = 'bitacora'

urlpatterns = [
    path('', views.index, name='index'),
    path('crear/', views.crear, name='crear'),
    path('eliminar/<int:id>/', views.eliminar, name='eliminar'),
]
