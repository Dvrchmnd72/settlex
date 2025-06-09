from django.test import SimpleTestCase, TestCase, RequestFactory
from django.urls import reverse, resolve
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.auth.models import User
from collections import OrderedDict
from types import SimpleNamespace

from .views import view_settlement, SettlexTwoFactorSetupView
from .forms import CustomTOTPDeviceForm, ValidationStepForm, WelcomeStepForm


class URLTests(SimpleTestCase):
    """Tests for URL configuration."""

    def test_view_settlement_url(self):
        """The view_settlement URL uses settlement_id as the parameter."""
        url = reverse('settlements_app:view_settlement', kwargs={'settlement_id': 1})
        self.assertEqual(url, '/settlement/1/')
        resolver = resolve('/settlement/1/')
        self.assertEqual(resolver.func, view_settlement)


class TwoFactorSetupViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.session = SessionStore()
        self.session.create()
        self.user = User.objects.create_user('tester', password='pass')

    def _init_view(self):
        request = self.factory.get('/two_factor/setup/')
        request.session = self.session
        request.user = self.user
        view = SettlexTwoFactorSetupView()
        view.form_list = OrderedDict(view.form_list)
        view.setup(request)
        view.storage = SimpleNamespace(validated_step_data={}, extra_data={}, data={})
        view.condition_dict = {}
        return view

    def test_custom_form_list(self):
        view = self._init_view()
        form_list = view.get_form_list()
        self.assertIs(form_list['generator'], CustomTOTPDeviceForm)
        self.assertIs(form_list['validation'], ValidationStepForm)

    def test_get_form_welcome(self):
        view = self._init_view()
        form = view.get_form('welcome')
        self.assertIsInstance(form, WelcomeStepForm)

    def test_get_form_generator(self):
        view = self._init_view()
        form = view.get_form('generator')
        self.assertIsInstance(form, CustomTOTPDeviceForm)
