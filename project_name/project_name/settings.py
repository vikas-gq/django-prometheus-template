import os


INSTALLED_APPS = [
    # ...
    'django_prometheus'
    # ...
]


MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    # ...
    'django_prometheus.middleware.PrometheusAfterMiddleware',
    'project_name.middlewares.MetricsBasicAuthMiddleware'
]


METRICS_USERNAME = os.getenv(
    key='METRICS_USERNAME', default='project_name'
)


METRICS_PASSWORD = os.getenv(
    key='METRICS_PASSWORD', default=''
)
