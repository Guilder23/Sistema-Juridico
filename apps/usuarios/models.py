from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    ROLES = [
        ('ADMINISTRADOR', 'Administrador'),
        ('GESTOR', 'Gestor'),
        ('CONSULTA', 'Consulta'),
    ]
    
    rol = models.CharField(max_length=20, choices=ROLES, default='GESTOR')
    telefono = models.CharField(max_length=25, blank=True, null=True)
    cargo = models.CharField(max_length=100, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_rol_display()})"
