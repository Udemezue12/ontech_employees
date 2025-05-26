from rest_framework.response import Response
from rest_framework import status




# def verify_frontend_origin(request, allowed_origin='http://127.0.0.1:7000'):
#     origin = request.META.get('HTTP_ORIGIN')
#     referer = request.META.get('HTTP_REFERER')

#     if (origin and allowed_origin not in origin) or (referer and allowed_origin not in referer):
#         return Response({'detail': 'Access Forbidden'}, status=status.HTTP_403_FORBIDDEN)

#     if not origin and not referer:
#         return Response({'detail': 'Access Forbidden'}, status=status.HTTP_403_FORBIDDEN)

#     return None  # No issues, allow the view to continue
# def verify_frontend_origin(request, allowed_origins=None):
#     if allowed_origins is None:
#         allowed_origins = ['http://127.0.0.1:7000', 'http://localhost:3000', "http://127.0.0.1:8000"]

#     origin = request.META.get('HTTP_ORIGIN')
#     referer = request.META.get('HTTP_REFERER')

#     if (origin and not any(allowed in origin for allowed in allowed_origins)) or \
#        (referer and not any(allowed in referer for allowed in allowed_origins)):
#         return Response({'detail': 'Access Forbidden'}, status=status.HTTP_403_FORBIDDEN)

#     if not origin and not referer:
#         return Response({'detail': 'Access Forbidden'}, status=status.HTTP_403_FORBIDDEN)
