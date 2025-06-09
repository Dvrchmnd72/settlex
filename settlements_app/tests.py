from django.test import SimpleTestCase, TestCase
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.oath import TOTP

from .views import view_settlement
from .forms import ValidationStepForm


class URLTests(SimpleTestCase):
    """Tests for URL configuration."""

    def test_view_settlement_url(self):
        """The view_settlement URL uses settlement_id as the parameter."""
        url = reverse('settlements_app:view_settlement', kwargs={'settlement_id': 1})
        self.assertEqual(url, '/settlement/1/')
        resolver = resolve('/settlement/1/')
        self.assertEqual(resolver.func, view_settlement)


class ValidationStepFormTests(TestCase):
    """Tests for ValidationStepForm token validation."""

    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username="user@example.com", password="pass"
        )

    def _create_device(self):
        return TOTPDevice.objects.create(user=self.user, confirmed=True)

    def test_valid_token(self):
        device = self._create_device()
        totp = TOTP(
            bytes.fromhex(device.key),
            device.step,
            device.t0,
            device.digits,
            device.drift,
        )
        token = str(totp.token()).zfill(device.digits)

        form = ValidationStepForm(user=self.user, device=device, data={"otp_token": token})
        valid = form.is_valid()
        if not valid:
            print("form errors", form.errors)
        self.assertTrue(valid)

    def test_invalid_token(self):
        device = self._create_device()
        form = ValidationStepForm(user=self.user, device=device, data={"otp_token": "000000"})
        self.assertFalse(form.is_valid())
