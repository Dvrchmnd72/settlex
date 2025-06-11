from django.test import SimpleTestCase, TestCase, RequestFactory
from django.urls import reverse, resolve
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.auth.models import User
from collections import OrderedDict
from types import SimpleNamespace

from django_otp.plugins.otp_totp.models import TOTPDevice


from .views import view_settlement, SettlexTwoFactorSetupView
from .forms import CustomTOTPDeviceForm, WelcomeStepForm


class URLTests(SimpleTestCase):
    """Tests for URL configuration."""

    def test_view_settlement_url(self):
        """The view_settlement URL uses settlement_id as the parameter."""
        url = reverse('settlements_app:view_settlement', kwargs={'settlement_id': 1})
        self.assertEqual(url, '/settlement/1/')
        resolver = resolve('/settlement/1/')
        self.assertEqual(resolver.func, view_settlement)

