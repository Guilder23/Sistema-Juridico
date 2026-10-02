from django.conf import settings
from django.test import SimpleTestCase


class GoogleAuthConfigTest(SimpleTestCase):
    def test_google_oauth_configuration_exists(self):
        self.assertIn('allauth', settings.INSTALLED_APPS)
        self.assertIn('allauth.socialaccount.providers.google', settings.INSTALLED_APPS)
        self.assertIn('allauth.account.auth_backends.AuthenticationBackend', settings.AUTHENTICATION_BACKENDS)
        self.assertEqual(settings.SITE_ID, 1)
        self.assertIn('https://www.googleapis.com/auth/calendar', settings.GOOGLE_SCOPES)
        self.assertIn('https://www.googleapis.com/auth/drive', settings.GOOGLE_SCOPES)
        self.assertIn('https://www.googleapis.com/auth/documents', settings.GOOGLE_SCOPES)
        self.assertEqual(settings.SOCIALACCOUNT_PROVIDERS['google']['AUTH_PARAMS']['access_type'], 'offline')
