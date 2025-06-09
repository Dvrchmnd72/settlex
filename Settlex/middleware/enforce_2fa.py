from django.shortcuts import redirect
from django.urls import reverse
from two_factor.utils import default_device


class Enforce2FAMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_staff:
            if not default_device(request.user):
                safe_paths = [
                    # The login view for the application lives within the
                    # ``settlements_app`` namespace.
                    reverse('settlements_app:login'),
                    # Allow access to the 2FA setup wizard itself.
                    reverse('settlements_app:two_factor_setup'),
                    # Users should always be able to log out.
                    reverse('settlements_app:logout'),
                ]
                if not any(request.path.startswith(path) for path in safe_paths):
                    return redirect('settlements_app:two_factor_setup')

        return self.get_response(request)