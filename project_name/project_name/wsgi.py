import os

from django.core.wsgi import get_wsgi_application

from django.conf import settings

if settings.OTEL_ENABLE_TRACING:
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.instrumentation.django import DjangoInstrumentor

    resource = Resource.create({"service.name": settings.OTEL_SERVICE_NAME})
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

    otlp_exporter = OTLPSpanExporter(endpoint=settings.OTLP_SPAN_EXPORTER_ENDPOINT)
    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)

    DjangoInstrumentor().instrument()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_name.settings')

application = get_wsgi_application()