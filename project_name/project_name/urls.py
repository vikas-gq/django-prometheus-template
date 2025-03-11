from django.urls import include, re_path
from opentelemetry.instrumentation.django import DjangoInstrumentor

# Initialize OpenTelemetry for Django (Tempo integration)
DjangoInstrumentor().instrument()

urlpatterns = [
    # ...
    re_path('', include('django_prometheus.urls'))
]