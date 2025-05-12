import os

from project_name.project_name.utils.log_formatter import JSONLineFormatter

INSTALLED_APPS = [
    # ...
    'django_prometheus',
    "opentelemetry.instrumentation.django",
    # ...
]


MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    # ...
    'django_prometheus.middleware.PrometheusAfterMiddleware',
    'project_name.middlewares.MetricsBasicAuthMiddleware'
]


LOGGING = {
    # ...
    "formatters": {
        "file": {
                     "()": JSONLineFormatter,
                },
    },
    # ...
}


ENVIRONMENT = os.getenv(key="ENVIRONMENT", default="env")
SERVICE_NAME = os.getenv(key="SERVICE", default="project_name")



METRICS_USERNAME = os.getenv(
    key='METRICS_USERNAME', default='project_name'
)


METRICS_PASSWORD = os.getenv(
    key='METRICS_PASSWORD', default=''
)

OTLP_SPAN_EXPORTER_ENDPOINT = os.getenv(
    key='OTLP_SPAN_EXPORTER_ENDPOINT', default='http://localhost:4318/v1/traces'
)

OTEL_SERVICE_NAME = SERVICE_NAME

OTEL_ENABLE_TRACING = os.getenv(
    key='OTEL_ENABLE_TRACING', default='NO'
)

OTEL_PYTHON_DJANGO_INSTRUMENT =  OTEL_ENABLE_TRACING.upper() == "YES"
