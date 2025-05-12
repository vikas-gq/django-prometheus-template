from opentelemetry.trace import get_current_span, format_span_id, format_trace_id
from django.conf import settings

import json
import logging
import os
import socket
from datetime import datetime


class JSONLineFormatter(logging.Formatter):
    def format(self, record):
        # Extract OTEL trace context
        span = get_current_span()
        span_context = span.get_span_context()

        log_record = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "notes":{},
            # "path": record.pathname,
            # "file": record.filename,
            # "module": record.module,
            # "function": record.funcName,
            # "line": record.lineno,
            "message": record.getMessage(),
            # Identifiers
            "service": settings.SERVICE_NAME,
            "env": settings.ENVIRONMENT,
            "host": socket.gethostname(),
            "instance_id": os.getenv("INSTANCE_ID", None),
            # OTEL trace context
            "trace_id": format_trace_id(span_context.trace_id) if span_context and span_context.trace_id else None,
            "span_id": format_span_id(span_context.span_id) if span_context and span_context.span_id else None,
            "trace_flags": span_context.trace_flags if span_context else None,
        }
        return json.dumps(log_record)