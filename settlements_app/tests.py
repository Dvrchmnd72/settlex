from django.test import SimpleTestCase, TestCase
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model
from django_otp.plugins.otp_totp.models import TOTPDevice

from .forms import CustomTOTPDeviceForm
from .views import view_settlement


class URLTests(SimpleTestCase):
    """Tests for URL configuration."""

    def test_view_settlement_url(self):
        """The view_settlement URL uses settlement_id as the parameter."""
        url = reverse('settlements_app:view_settlement', kwargs={'settlement_id': 1})
        self.assertEqual(url, '/settlement/1/')
        resolver = resolve('/settlement/1/')
        self.assertEqual(resolver.func, view_settlement)


class CustomTOTPDeviceFormTests(TestCase):
    """Ensure the TOTP setup form handles unexpected kwargs gracefully."""

    def test_init_drops_unexpected_kwargs(self):
        User = get_user_model()
        user = User.objects.create_user(username="tester", password="pass")
        device = TOTPDevice.objects.create(user=user, confirmed=False)

        try:
            form = CustomTOTPDeviceForm(
                data={},
                user=user,
                key=device.key,
                device=device,
                unexpected="ignored",
            )
            form.is_valid()
        except TypeError as exc:
            self.fail(f"TypeError raised: {exc}")
