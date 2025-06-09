from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.oath import totp
from Settlex import settings

MIDDLEWARE_NO_ENFORCE = [mw for mw in settings.MIDDLEWARE if mw != 'Settlex.middleware.enforce_2fa.Enforce2FAMiddleware']

@override_settings(MIDDLEWARE=MIDDLEWARE_NO_ENFORCE)
class TwoFactorSetupFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='pass', email='t@example.com')
        self.client.login(username='tester', password='pass')
        self.url = reverse('two_factor_setup')

    def _current_step(self, response):
        return response.context['wizard']['steps'].current

    def test_setup_wizard_flow(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self._current_step(resp), 'welcome')

        resp = self.client.post(self.url, {
            'settlex_two_factor_setup_view-current_step': 'welcome'
        }, follow=True)
        self.assertEqual(self._current_step(resp), 'generator')

        session = self.client.session['settlex_two_factor_setup_view']
        device_id = session['extra_data']['device_id']
        device = TOTPDevice.objects.get(id=device_id)
        token = str(totp(device.bin_key, device.step, device.t0, device.digits, device.drift)).zfill(device.digits)

        resp = self.client.post(self.url, {
            'settlex_two_factor_setup_view-current_step': 'generator',
            'generator-token': token,
        }, follow=True)
        self.assertEqual(self._current_step(resp), 'validation')

        resp = self.client.post(self.url, {
            'settlex_two_factor_setup_view-current_step': 'validation',
            'validation-token': token,
        }, follow=True)
        self.assertRedirects(resp, reverse('two_factor:setup_complete'))
        device.refresh_from_db()
        self.assertTrue(device.confirmed)
