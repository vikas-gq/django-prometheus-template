import os


INSTALLED_APPS = [
    # ...
    'django_prometheus'
    'opentelemetry.instrumentation.django',
    # ...
]


MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'opentelemetry.instrumentation.django.middleware.OpenTelemetryMiddleware',
    # ...
    'django_prometheus.middleware.PrometheusAfterMiddleware',
    'project_name.middlewares.MetricsBasicAuthMiddleware'
]

OTEL_EXPORTER_OTLP_ENDPOINT = os.getenv(
    key='OTEL_EXPORTER_OTLP_ENDPOINT', default='http://localhost:4317'
)

OTEL_SERVICE_NAME = os.getenv(
    key='OTEL_SERVICE_NAME', default='project_name'
)


METRICS_USERNAME = os.getenv(
    key='METRICS_USERNAME', default='project_name'
)


METRICS_PASSWORD = os.getenv(
    key='METRICS_PASSWORD', default=''
)
