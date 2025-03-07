import inspect
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
    ['operation', 'query_text', 'parameters', 'duration','file_name','line_num  ber'],
    registry=REGISTRY
)

def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.time()

def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    duration = time.time() - context._query_start_time
    operation = statement.split()[0].upper()  # e.g., SELECT, INSERT

    file_name = "unknown"
    line_number = "unknown"
    try:
        stack = inspect.stack()
        for frame_info in stack:
            if "helpers/query_helpers" in frame_info.filename:
                file_name = frame_info.filename
                line_number = frame_info.lineno
                break
    except Exception as ex:
        pass

    # Only log slow queries (duration > 1 second)
    if duration > 1.0:
        slow_queries.labels(
            operation=operation,
            query_text=statement,
            parameters=str(parameters),
            duration=f"{duration:.3f}s",
            file_name=file_name,
            line_number=line_number
        ).observe(duration)

    query_duration_seconds.labels(operation=operation).observe(duration)
    django_db_execute_total.labels(operation=operation).inc()

def handle_db_error(context):
    statement = context.statement if context.statement else "UNKNOWN"
    operation = statement.split()[0].upper() if statement else "UNKNOWN"

    error_type = type(context.original_exception).__name__

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