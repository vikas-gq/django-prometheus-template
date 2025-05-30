# ...
import os
import socket

from django.conf import settings

if settings.OTEL_PYTHON_DJANGO_INSTRUMENT:
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.instrumentation.django import DjangoInstrumentor
    from opentelemetry.instrumentation.requests import RequestsInstrumentor

    resource = Resource.create({
        "service.name": settings.OTEL_SERVICE_NAME,
        "env": settings.ENVIRONMENT,
        "host": socket.gethostname(),
        "instance_id": os.getenv("INSTANCE_ID", None),
    })
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

    otlp_exporter = OTLPSpanExporter(endpoint=settings.OTLP_SPAN_EXPORTER_ENDPOINT)
    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)
    # Initialize the instrumentation for requests library
    RequestsInstrumentor().instrument()
    DjangoInstrumentor().instrument()

# ...