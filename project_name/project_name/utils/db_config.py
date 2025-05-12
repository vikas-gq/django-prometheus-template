

# ...
import os

from project_name.utils.metrics import setup_db_metrics

OTEL_ENABLE_TRACING = os.getenv(
    key='OTEL_ENABLE_TRACING', default='NO'
)

OTEL_ENABLE_TRACING = OTEL_ENABLE_TRACING.upper() == "YES"


# ...


def db_mongo_connect_v1(db_type):
    # ...
    if OTEL_ENABLE_TRACING:
        from opentelemetry.instrumentation.pymongo import PymongoInstrumentor
        PymongoInstrumentor().instrument(client=engine)
    # ...

def db_connect_v1(db_type):
    # ...
    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        echo=False
    )

    if OTEL_ENABLE_TRACING:
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
        SQLAlchemyInstrumentor().instrument(engine=engine)

    setup_db_metrics(engine)
    # ...
