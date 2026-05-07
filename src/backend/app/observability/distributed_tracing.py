"""
Distributed Tracing System
===========================
Enterprise-grade distributed tracing for Financial Master
"""

import asyncio
import uuid
import time
import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from contextlib import asynccontextmanager, contextmanager
import logging
import aiohttp
from functools import wraps

logger = logging.getLogger(__name__)


class SpanKind(Enum):
    SERVER = "server"
    CLIENT = "client"
    PRODUCER = "producer"
    CONSUMER = "consumer"
    INTERNAL = "internal"


class StatusCode(Enum):
    OK = "ok"
    ERROR = "error"
    CANCELLED = "cancelled"


@dataclass
class SpanEvent:
    timestamp: datetime
    name: str
    attributes: Dict[str, Any]


@dataclass
class SpanLink:
    trace_id: str
    span_id: str
    attributes: Dict[str, Any]


@dataclass
class Span:
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    name: str
    kind: SpanKind
    start_time: datetime
    end_time: Optional[datetime]
    status_code: StatusCode
    status_message: str
    attributes: Dict[str, Any]
    events: List[SpanEvent]
    links: List[SpanLink]
    
    @property
    def duration_ms(self) -> Optional[float]:
        """Get span duration in milliseconds"""
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return None


class DistributedTracing:
    """Enterprise distributed tracing with Jaeger/Zipkin compatibility"""
    
    def __init__(self, service_name: str = "financial-master"):
        self.service_name = service_name
        self.spans: Dict[str, Span] = {}
        self.active_spans: Dict[str, Span] = {}
        self.sampling_rate = 0.1  # 10% sampling
        self.max_spans = 10000
        self.exporters = []
        
    def add_exporter(self, exporter: 'SpanExporter'):
        """Add a span exporter"""
        self.exporters.append(exporter)
        
    def start_span(self, name: str, 
                   parent_span: Optional[Span] = None,
                   kind: SpanKind = SpanKind.INTERNAL,
                   attributes: Optional[Dict[str, Any]] = None) -> Span:
        """Start a new span"""
        trace_id = parent_span.trace_id if parent_span else str(uuid.uuid4())
        span_id = str(uuid.uuid4())
        parent_span_id = parent_span.span_id if parent_span else None
        
        span = Span(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            name=name,
            kind=kind,
            start_time=datetime.now(),
            end_time=None,
            status_code=StatusCode.OK,
            status_message="",
            attributes=attributes or {},
            events=[],
            links=[]
        )
        
        self.active_spans[span_id] = span
        return span
        
    def end_span(self, span: Span, 
                 status_code: StatusCode = StatusCode.OK,
                 status_message: str = ""):
        """End a span"""
        span.end_time = datetime.now()
        span.status_code = status_code
        span.status_message = status_message
        
        if span.span_id in self.active_spans:
            del self.active_spans[span.span_id]
            
        self.spans[span.span_id] = span
        
        # Maintain max spans limit
        if len(self.spans) > self.max_spans:
            oldest_span_id = min(self.spans.keys(), 
                                key=lambda k: self.spans[k].end_time or datetime.min)
            del self.spans[oldest_span_id]
            
        # Export span
        asyncio.create_task(self._export_span(span))
        
    def add_event(self, span: Span, name: str, attributes: Optional[Dict[str, Any]] = None):
        """Add an event to a span"""
        event = SpanEvent(
            timestamp=datetime.now(),
            name=name,
            attributes=attributes or {}
        )
        span.events.append(event)
        
    def add_link(self, span: Span, trace_id: str, span_id: str, 
                 attributes: Optional[Dict[str, Any]] = None):
        """Add a link to another span"""
        link = SpanLink(
            trace_id=trace_id,
            span_id=span_id,
            attributes=attributes or {}
        )
        span.links.append(link)
        
    def set_attribute(self, span: Span, key: str, value: Any):
        """Set an attribute on a span"""
        span.attributes[key] = value
        
    async def _export_span(self, span: Span):
        """Export span to all configured exporters"""
        for exporter in self.exporters:
            try:
                await exporter.export(span)
            except Exception as e:
                logger.error(f"Error exporting span to {exporter.__class__.__name__}: {e}")
                
    def get_trace(self, trace_id: str) -> List[Span]:
        """Get all spans for a trace"""
        return [span for span in self.spans.values() if span.trace_id == trace_id]
        
    def get_spans_by_service(self, service_name: str) -> List[Span]:
        """Get spans for a specific service"""
        return [span for span in self.spans.values() 
                if span.attributes.get("service.name") == service_name]
                
    def get_active_spans(self) -> List[Span]:
        """Get all currently active spans"""
        return list(self.active_spans.values())
        
    @asynccontextmanager
    async def trace_async(self, name: str, 
                         kind: SpanKind = SpanKind.INTERNAL,
                         attributes: Optional[Dict[str, Any]] = None):
        """Async context manager for tracing"""
        span = self.start_span(name, kind=kind, attributes=attributes)
        try:
            yield span
            self.end_span(span, StatusCode.OK)
        except Exception as e:
            self.add_event(span, "error", {"exception": str(e)})
            self.end_span(span, StatusCode.ERROR, str(e))
            raise
            
    @contextmanager
    def trace_sync(self, name: str, 
                  kind: SpanKind = SpanKind.INTERNAL,
                  attributes: Optional[Dict[str, Any]] = None):
        """Sync context manager for tracing"""
        span = self.start_span(name, kind=kind, attributes=attributes)
        try:
            yield span
            self.end_span(span, StatusCode.OK)
        except Exception as e:
            self.add_event(span, "error", {"exception": str(e)})
            self.end_span(span, StatusCode.ERROR, str(e))
            raise


class SpanExporter:
    """Base class for span exporters"""
    
    async def export(self, span: Span):
        """Export a span"""
        try:
            # Mock implementation - would integrate with actual tracing system
            logger.info(f"Exporting span: {span.trace_id}:{span.span_id}")
            
            # In production, would send to Jaeger/Zipkin
            # For now, just log the span data
            span_data = {
                "trace_id": span.trace_id,
                "span_id": span.span_id,
                "operation_name": span.operation_name,
                "start_time": span.start_time,
                "end_time": span.end_time,
                "tags": span.tags,
                "logs": span.logs
            }
            
            # Mock export to file or database
            logger.debug(f"Span data: {span_data}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting span: {e}")
            return False


class JaegerExporter(SpanExporter):
    """Jaeger span exporter"""
    
    def __init__(self, endpoint: str = "http://localhost:14268/api/traces"):
        self.endpoint = endpoint
        
    async def export(self, span: Span):
        """Export span to Jaeger"""
        try:
            jaeger_span = self._convert_to_jaeger_format(span)
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.endpoint,
                    json={"spans": [jaeger_span]},
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status != 200:
                        logger.error(f"Failed to export to Jaeger: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error exporting to Jaeger: {e}")
            
    def _convert_to_jaeger_format(self, span: Span) -> Dict[str, Any]:
        """Convert span to Jaeger format"""
        return {
            "traceID": span.trace_id.replace("-", ""),
            "spanID": span.span_id.replace("-", ""),
            "operationName": span.name,
            "references": [] if not span.parent_span_id else [{
                "refType": "CHILD_OF",
                "traceID": span.trace_id.replace("-", ""),
                "spanID": span.parent_span_id.replace("-", "")
            }],
            "startTime": int(span.start_time.timestamp() * 1000000),  # microseconds
            "duration": int(span.duration_ms or 0) * 1000,  # microseconds
            "tags": [
                {"key": k, "value": str(v)} for k, v in span.attributes.items()
            ] + [
                {"key": "status.code", "value": span.status_code.value},
                {"key": "status.message", "value": span.status_message},
                {"key": "span.kind", "value": span.kind.value}
            ],
            "logs": [
                {
                    "timestamp": int(event.timestamp.timestamp() * 1000000),
                    "fields": [{"key": k, "value": str(v)} for k, v in event.attributes.items()]
                } for event in span.events
            ]
        }


class ZipkinExporter(SpanExporter):
    """Zipkin span exporter"""
    
    def __init__(self, endpoint: str = "http://localhost:9411/api/v2/spans"):
        self.endpoint = endpoint
        
    async def export(self, span: Span):
        """Export span to Zipkin"""
        try:
            zipkin_span = self._convert_to_zipkin_format(span)
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.endpoint,
                    json=[zipkin_span],
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status != 202:
                        logger.error(f"Failed to export to Zipkin: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error exporting to Zipkin: {e}")
            
    def _convert_to_zipkin_format(self, span: Span) -> Dict[str, Any]:
        """Convert span to Zipkin format"""
        return {
            "traceId": span.trace_id.replace("-", ""),
            "id": span.span_id.replace("-", ""),
            "parentId": span.parent_span_id.replace("-", "") if span.parent_span_id else None,
            "name": span.name,
            "timestamp": int(span.start_time.timestamp() * 1000000),  # microseconds
            "duration": int(span.duration_ms or 0) * 1000,  # microseconds
            "localEndpoint": {
                "serviceName": span.attributes.get("service.name", "financial-master")
            },
            "tags": {
                **span.attributes,
                "status.code": span.status_code.value,
                "status.message": span.status_message,
                "span.kind": span.kind.value
            },
            "annotations": [
                {
                    "timestamp": int(event.timestamp.timestamp() * 1000000),
                    "value": event.name
                } for event in span.events
            ]
        }


# Global tracer instance
_tracer = None

def get_tracer() -> DistributedTracing:
    """Get the global tracer instance"""
    global _tracer
    if _tracer is None:
        _tracer = DistributedTracing()
        # Add default exporters if available
        try:
            _tracer.add_exporter(JaegerExporter())
        except Exception:
            pass
        try:
            _tracer.add_exporter(ZipkinExporter())
        except Exception:
            pass
    return _tracer


def trace_async(name: str, kind: SpanKind = SpanKind.INTERNAL, 
               attributes: Optional[Dict[str, Any]] = None):
    """Decorator for async function tracing"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            tracer = get_tracer()
            async with tracer.trace_async(name, kind=kind, attributes=attributes) as span:
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)
                return await func(*args, **kwargs)
        return wrapper
    return decorator


def trace_sync(name: str, kind: SpanKind = SpanKind.INTERNAL,
              attributes: Optional[Dict[str, Any]] = None):
    """Decorator for sync function tracing"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            tracer = get_tracer()
            with tracer.trace_sync(name, kind=kind, attributes=attributes) as span:
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)
                return func(*args, **kwargs)
        return wrapper
    return decorator


# FastAPI integration
async def trace_middleware(request, call_next):
    """FastAPI middleware for tracing"""
    tracer = get_tracer()
    
    # Extract trace context from headers
    trace_id = request.headers.get("X-Trace-ID")
    parent_span_id = request.headers.get("X-Parent-Span-ID")
    
    parent_span = None
    if trace_id and parent_span_id:
        # Create a parent span from context
        parent_span = Span(
            trace_id=trace_id,
            span_id=parent_span_id,
            parent_span_id=None,
            name="incoming-request",
            kind=SpanKind.SERVER,
            start_time=datetime.now(),
            end_time=None,
            status_code=StatusCode.OK,
            status_message="",
            attributes={},
            events=[],
            links=[]
        )
    
    # Start span for this request
    span = tracer.start_span(
        name=f"{request.method} {request.url.path}",
        parent_span=parent_span,
        kind=SpanKind.SERVER,
        attributes={
            "http.method": request.method,
            "http.url": str(request.url),
            "http.host": request.url.hostname,
            "http.scheme": request.url.scheme,
            "service.name": "financial-master"
        }
    )
    
    try:
        response = await call_next(request)
        
        span.set_attribute("http.status_code", response.status_code)
        span.set_attribute("http.response_size", len(response.body) if hasattr(response, 'body') else 0)
        
        if response.status_code >= 400:
            tracer.end_span(span, StatusCode.ERROR, f"HTTP {response.status_code}")
        else:
            tracer.end_span(span, StatusCode.OK)
            
        # Add trace headers to response
        response.headers["X-Trace-ID"] = span.trace_id
        response.headers["X-Span-ID"] = span.span_id
        
        return response
        
    except Exception as e:
        span.set_attribute("error", str(e))
        tracer.end_span(span, StatusCode.ERROR, str(e))
        raise
