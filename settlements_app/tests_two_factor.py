from django.test import TestCase, RequestFactory, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from Settlex import settings
from settlements_app.views import SettlexTwoFactorSetupView

MIDDLEWARE_NO_ENFORCE = [mw for mw in settings.MIDDLEWARE if mw != 'Settlex.middleware.enforce_2fa.Enforce2FAMiddleware']

@override_settings(MIDDLEWARE=MIDDLEWARE_NO_ENFORCE)
class TwoFactorSetupFlowTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='tester', password='pass')

    def test_done_redirects_to_dashboard(self):
        view = SettlexTwoFactorSetupView()
        request = self.factory.post(reverse('settlements_app:two_factor_setup'))
        request.user = self.user
        response = view.done([])
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('settlements_app:my_settlements'))
