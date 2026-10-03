from django.apps import AppConfig
from allauth.socialaccount.signals import social_account_added


def ensure_google_token(sender, request, sociallogin, **kwargs):
    from .google_integration import persist_google_social_token

    if sociallogin.account.provider != 'google':
        return

    persist_google_social_token(sociallogin.account, getattr(sociallogin, 'token', None))


class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.usuarios'
    label = 'usuarios'

    def ready(self):
        social_account_added.connect(ensure_google_token, dispatch_uid='usuarios_google_token_persist')

