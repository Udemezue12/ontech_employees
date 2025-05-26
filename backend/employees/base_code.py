import base64
from rest_framework import status
from django.http import HttpResponse
from .logger import logger


def base64url_encode(data) -> str:
    try:
        """
        Encode bytes or base64/hex string into base64url (no padding).
        """
        if isinstance(data, str):
            try:
                data = base64.b64decode(data)
            except Exception:
                try:
                    data = bytes.fromhex(data)
                except Exception:
                    raise ValueError(
                        "Data must be a base64 or hex string, or bytes.")
        return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')
    except Exception as e:
        logger.error(f"Error: {e}")
        return HttpResponse({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
