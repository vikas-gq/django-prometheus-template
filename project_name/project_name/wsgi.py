import os
from django.core.wsgi import get_wsgi_application
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Set the default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project_name.settings")

# Check if tracing is enabled based on the environment variable
tracing_enabled = os.getenv("ENABLE_TRACING", "on").lower() == "on"

if tracing_enabled:
    # Initialize OpenTelemetry (Tempo) Tracing
    trace_provider = TracerProvider()
    trace_exporter = OTLPSpanExporter()  # Exports traces to Tempo
    span_processor = BatchSpanProcessor(trace_exporter)
    trace_provider.add_span_processor(span_processor)

    # Instrument Django
    DjangoInstrumentor().instrument()

# Get WSGI application
application = get_wsgi_application()
