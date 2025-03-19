from django.shortcuts import redirect
from django.conf import settings

class LoginRequiredMiddleware:
    """Middleware to protect certain pages from unauthorized access."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        protected_paths = ['/dashboard/', '/profile/']  # Add your protected URLs here
        if request.path in protected_paths and not request.user.is_authenticated:
            return redirect(settings.LOGIN_URL)
        return self.get_response(request)
