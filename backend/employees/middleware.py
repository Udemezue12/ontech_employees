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
       
        allowed_frontend_url = 'https://yourdomain.com'  

       
        origin = request.META.get('HTTP_ORIGIN')
        referer = request.META.get('HTTP_REFERER')

      
        if (origin and allowed_frontend_url not in origin) and (referer and allowed_frontend_url not in referer):
           
            return JsonResponse({'detail': 'Access Forbidden'}, status=403)

        response = self.get_response(request)
        return response


class NoCacheMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        add_never_cache_headers(response)
        return response
