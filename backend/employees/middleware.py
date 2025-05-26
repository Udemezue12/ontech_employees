from django.utils.deprecation import MiddlewareMixin
from django.utils.cache import add_never_cache_headers
from django.http import JsonResponse
from django.conf import settings


class CheckFrontendAccessMiddleware:
    """
    Middleware to allow API access only from the frontend.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Allowed frontend origin (can be the same as the domain in production)
        allowed_frontend_url = 'https://yourdomain.com'  # Use your production domain

        # Get the Origin and Referer headers
        origin = request.META.get('HTTP_ORIGIN')
        referer = request.META.get('HTTP_REFERER')

        # Check if the request is coming from the frontend app
        if (origin and allowed_frontend_url not in origin) and (referer and allowed_frontend_url not in referer):
            # Block direct access to the API
            return JsonResponse({'detail': 'Access Forbidden'}, status=403)

        response = self.get_response(request)
        return response


class NoCacheMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        add_never_cache_headers(response)
        return response
