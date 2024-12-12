# Project Structure Changes

This document summarizes the changes required in the project structure.

Note: mention of `project_name` is dynamic. This has to be replaced with proper repository name
## Files to Update
These files already exist and need to be updated. Contents to be added are included below:

### `requirements.txt`
```python
# ...
django-prometheus==2.3.1
```

### `.env.example`
```python
# ...

METRICS_USERNAME=project_name
METRICS_PASSWORD=''

# ...
```

### `project_name/settings.py`
```python
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
```

### `project_name/urls.py`
```python
from django.urls import include, re_path

urlpatterns = [
    # ...
    re_path('', include('django_prometheus.urls'))
}
```

### `project_name/utils/db_config.py`
```python

# ...
from project_name.project_name.utils.metrics import setup_db_metrics

# ...

def db_connect_v1(db_type):
    # ...
    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        echo=False
    )
    setup_db_metrics(engine)
    # ...
```

## Files to Add
These files need to be created. Suggested contents are included below:

### `project_name/middlewares.py`
```python
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
```

### `project_name/utils/metrics.py`
```python
import time

from prometheus_client import Counter, REGISTRY, Histogram, Summary
from sqlalchemy import event

# Counter for total DB errors
db_errors_total = Counter(
    'sqlalchemy_db_errors_total',
    'Total number of database errors',
    ['operation', 'error_type'],
    registry=REGISTRY
)

# Counter for total DB executions
django_db_execute_total = Counter(
    'django_db_execute_total',
    'Total number of database executions',
    ['operation'],  # Labels can include operation types like SELECT, INSERT, etc.
    registry=REGISTRY  # Registering with the default registry to integrate with django-prometheus
)

# Histogram for query durations
query_duration_seconds = Histogram(
    'sqlalchemy_query_duration_seconds',
    'Duration of database queries in seconds',
    ['operation'],
    buckets=[0.001, 0.01, 0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0],
    registry=REGISTRY
)

# Metric for detailed query logging (only for queries taking >1s)
slow_queries = Summary(
    'sqlalchemy_slow_query_details',
    'Details of SQL queries taking more than 1 second',
    ['operation', 'query_text', 'parameters', 'duration'],
    registry=REGISTRY
)

def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.time()

def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    duration = time.time() - context._query_start_time
    operation = statement.split()[0].upper()  # e.g., SELECT, INSERT

    # Only log slow queries (duration > 1 second)
    if duration > 1.0:
        slow_queries.labels(
            operation=operation,
            query_text=statement,
            parameters=str(parameters),
            duration=f"{duration:.3f}s"
        ).observe(duration)

    query_duration_seconds.labels(operation=operation).observe(duration)
    django_db_execute_total.labels(operation=operation).inc()

def handle_db_error(conn, cursor, statement, parameters, context, exception):
    operation = statement.split()[0].upper()
    error_type = type(exception).__name__
    db_errors_total.labels(operation=operation, error_type=error_type).inc()

def setup_db_metrics(engine):
    event.listen(engine, "before_cursor_execute", before_cursor_execute)
    event.listen(engine, "after_cursor_execute", after_cursor_execute)
    event.listen(engine, "handle_error", handle_db_error)

# Define counters for cache hits and total cache queries
cache_hits_total = Counter(
    'custom_cache_get_hits_total',
    'Total number of cache hits',
    ['backend']
)

cache_get_total = Counter(
    'custom_cache_get_total',
    'Total number of cache get requests',
    ['backend']
)
```

### `project_name/utils/cache_config.py`

#### If caching implementation doesn't exist, copy this file as is and change `service: str = "project_name"` based on your service name.

```python
import json
import redis
from typing import Any, Union

from project_name.utils.metrics import cache_get_total, cache_hits_total


class ElastiCacheUtility:
    def __init__(self, config: dict, env: str = "dev",
                 service: str = "project_name"): # TODO: change the service default value to project_name
        self.expiry_time = config.get("default_expiry_time")
        self.env = env
        self.service = service
        self.cluster_endpoint = config.get('cluster_endpoint')
        self.port = config.get('port')
        self.client = redis.StrictRedis(host=self.cluster_endpoint, port=self.port, decode_responses=True)

    def construct_key(self, unique_method_identifier: str, unique_identifier_key: str) -> str:
        return f"_GQ_{self.env}_{self.service}_{unique_method_identifier}_{unique_identifier_key}_".upper()

    def set(self, unique_method_identifier: str, unique_identifier_key: str, value: Any,
            expiry_time: int = None) -> bool:
        try:
            if not expiry_time:
                expiry_time = self.expiry_time
            key = self.construct_key(unique_method_identifier, unique_identifier_key)
            value_str = json.dumps(value)
            self.client.set(key, value_str)
            self.client.expire(key, expiry_time)
            return True
        except Exception as e:
            print(f"Error setting cache: {e}")
            return False

    def get(self, unique_method_identifier: str, unique_identifier_key: str) -> Union[None, Any]:
        try:
            key = self.construct_key(unique_method_identifier, unique_identifier_key)
            cache_get_total.labels(backend="redis").inc()  # Increment total cache gets
            value_str = self.client.get(key)
            if value_str is not None:
                cache_hits_total.labels(backend="redis").inc()  # Increment cache hits
            return json.loads(value_str) if value_str else None
        except Exception as e:
            print(f"Error getting cache: {e}")
            return None

    def delete(self, unique_method_identifier: str, unique_identifier_key: str) -> bool:
        try:
            key = self.construct_key(unique_method_identifier, unique_identifier_key)
            self.client.delete(key)
            return True
        except Exception as e:
            print(f"Error deleting cache: {e}")
            return False
```

