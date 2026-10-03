from django.conf import settings
from django.test import SimpleTestCase, TestCase
from allauth.socialaccount.models import SocialAccount, SocialToken
from apps.usuarios.google_integration import get_google_account_connected, persist_google_social_token
from apps.usuarios.models import Usuario


class GoogleAuthConfigTest(SimpleTestCase):
    def test_google_oauth_configuration_exists(self):
        self.assertIn('allauth', settings.INSTALLED_APPS)
        self.assertIn('allauth.socialaccount.providers.google', settings.INSTALLED_APPS)
        self.assertIn('allauth.account.auth_backends.AuthenticationBackend', settings.AUTHENTICATION_BACKENDS)
        self.assertEqual(settings.SITE_ID, 1)
        self.assertIn('https://www.googleapis.com/auth/calendar', settings.GOOGLE_SCOPES)
        self.assertIn('https://www.googleapis.com/auth/drive', settings.GOOGLE_SCOPES)
        self.assertIn('https://www.googleapis.com/auth/documents', settings.GOOGLE_SCOPES)
        self.assertTrue(settings.SOCIALACCOUNT_STORE_TOKENS)
        self.assertEqual(settings.SOCIALACCOUNT_PROVIDERS['google']['AUTH_PARAMS']['access_type'], 'offline')


class GoogleConnectionStatusTest(TestCase):
    def test_google_account_connected_requires_valid_token(self):
        user = Usuario.objects.create_user(username='googleuser', password='secret123')

        sa = SocialAccount.objects.create(user=user, provider='google', uid='google-user-1')
        self.assertFalse(get_google_account_connected(user))

        SocialToken.objects.create(account=sa, token='token-123', token_secret='')
        self.assertTrue(get_google_account_connected(user))

    def test_persist_google_social_token_creates_a_valid_token(self):
        user = Usuario.objects.create_user(username='googletokenuser', password='secret123')
        sa = SocialAccount.objects.create(user=user, provider='google', uid='google-token-user')

        class FakeToken:
            token = 'access-token-123'
            token_secret = 'refresh-token-456'
            expires_at = None

        persist_google_social_token(sa, FakeToken())

        self.assertTrue(SocialToken.objects.filter(account=sa, token='access-token-123').exists())
