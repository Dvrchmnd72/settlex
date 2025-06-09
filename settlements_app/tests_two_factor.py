from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from django_otp.plugins.otp_totp.models import TOTPDevice
from Settlex import settings

MIDDLEWARE_NO_ENFORCE = [mw for mw in settings.MIDDLEWARE if mw != 'Settlex.middleware.enforce_2fa.Enforce2FAMiddleware']



class MiddlewareIntegrationTests(TestCase):
    """Ensure Enforce2FAMiddleware sees the new device."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="mwtester", password="pass", email="mw@test.com"
        )
        TOTPDevice.objects.create(user=self.user, confirmed=True, name="default")
        self.client.login(username="mwtester", password="pass")

    def test_middleware_recognizes_setup_device(self):
        from two_factor.utils import default_device

        device = default_device(self.user)
        self.assertIsNotNone(device)
        resp = self.client.get(reverse("settlements_app:home"))
        self.assertEqual(resp.status_code, 302)
        self.assertNotIn('two_factor', resp.url)


