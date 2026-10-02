from django.db import models
from django.conf import settings
from apps.clientes.models import Cliente

class ConversacionIA(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chats_ia')
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True, related_name='consultas_ia')
    titulo = models.CharField(max_length=255, default='Nueva consulta')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Conversación IA"
        verbose_name_plural = "Conversaciones IA"
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.titulo} ({self.usuario.username})"

class MensajeIA(models.Model):
    ROL_CHOICES = [
        ('user', 'Usuario'),
        ('assistant', 'Asistente IA'),
        ('system', 'Sistema'),
    ]

    conversacion = models.ForeignKey(ConversacionIA, on_delete=models.CASCADE, related_name='mensajes')
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='user')
    contenido = models.TextField()
    contexto_utilizado = models.JSONField(blank=True, null=True, verbose_name="Contexto RAG usado")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mensaje IA"
        verbose_name_plural = "Mensajes IA"
        ordering = ['created_at']

    def __str__(self):
        return f"[{self.rol}] {self.contenido[:40]}..."
