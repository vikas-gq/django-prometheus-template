from django.http import HttpResponse
from django.conf import settings
import base64

class MetricsBasicAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only enforce authentication on the /metrics path
        if request.path == "/metrics":
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return self.unauthorized_response()

            # Decode and verify credentials
            try:
                auth_type, credentials = auth_header.split(' ')
                if auth_type.lower() != 'basic':
                    return self.unauthorized_response()

                decoded_creds = base64.b64decode(credentials).decode('utf-8')
                username, password = decoded_creds.split(':', 1)

                # Check against predefined username/password
                if username != settings.METRICS_USERNAME or password != settings.METRICS_PASSWORD:
                    return self.unauthorized_response()

            except Exception:
                return self.unauthorized_response()

        return self.get_response(request)

    def unauthorized_response(self):
        response = HttpResponse("Unauthorized", status=401)
        response['WWW-Authenticate'] = 'Basic realm="Metrics"'
        return response
    
