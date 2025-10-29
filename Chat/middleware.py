from django.shortcuts import redirect
from django.urls import reverse

class LoginRequiredMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        allowed_paths = [
            reverse('login'),
            reverse('admin:index'),
            '/static/',
            '/media/',
            '/signup/'
        ]

        if not request.user.is_authenticated:
            path = request.path_info
            if not any(path.startswith(ap) for ap in allowed_paths):
                return redirect('login')

        response = self.get_response(request)
        return response
