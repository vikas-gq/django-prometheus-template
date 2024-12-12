
# ...
from project_name.utils.metrics import setup_db_metrics

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
