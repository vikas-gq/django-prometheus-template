import os
from opentelemetry import trace
from django.conf import settings

def trace_span(span_name=None):
    """
    A decorator that creates a tracing span around a function using OpenTelemetry.
    
    Tracing is enabled/disabled based on the ENABLE_TRACING environment variable.
    
    Args:
        span_name (str, optional): The name of the span to create. 
                                  If None, will use the function name.
    
    Returns:
        decorator: A function decorator.
    """
    tracing_enabled = settings.OTEL_ENABLE_TRACING

    # Check if we're being called as @trace_span (without args)
    if callable(span_name):
        func = span_name
        span_name = func.__name__

        def wrapper(*args, **kwargs):
            if not tracing_enabled:
                return func(*args, **kwargs)  # Skip tracing
            
            tracer = trace.get_tracer(__name__)
            with tracer.start_as_current_span(span_name) as span:
                try:
                    span.set_attribute("function.args", str(args))
                    result = func(*args, **kwargs)
                    span.set_attribute("function.return_value", str(result))
                    return result
                except Exception as e:
                    span.record_exception(e)
                    raise

        return wrapper

    # Regular case: @trace_span("name")
    def decorator(func):
        actual_span_name = span_name or func.__name__

        def wrapper(*args, **kwargs):
            if not tracing_enabled:
                return func(*args, **kwargs)  # Skip tracing
            
            tracer = trace.get_tracer(__name__)
            with tracer.start_as_current_span(actual_span_name) as span:
                try:
                    span.set_attribute("function.args", str(args))
                    result = func(*args, **kwargs)
                    span.set_attribute("function.return_value", str(result))
                    return result
                except Exception as e:
                    span.record_exception(e)
                    raise

        return wrapper

    return decorator