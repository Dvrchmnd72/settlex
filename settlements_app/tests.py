from django.test import SimpleTestCase
from django.urls import reverse, resolve

from .views import view_settlement


class URLTests(SimpleTestCase):
    """Tests for URL configuration."""

    def test_view_settlement_url(self):
        """The view_settlement URL uses settlement_id as the parameter."""
        url = reverse('settlements_app:view_settlement', kwargs={'settlement_id': 1})
        self.assertEqual(url, '/settlement/1/')
        resolver = resolve('/settlement/1/')
        self.assertEqual(resolver.func, view_settlement)
