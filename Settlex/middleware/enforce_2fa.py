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
                    reverse('two_factor_login'),
                    reverse('two_factor_setup'),
                    reverse('settlements_app:logout'),  # Ensure 'settlements_app:logout' is used
                ]
                if not any(request.path.startswith(path) for path in safe_paths):
                    return redirect('two_factor_setup')

        return self.get_response(request)
