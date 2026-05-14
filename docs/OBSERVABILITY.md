# Observability Documentation

## Overview

Veyra uses OpenTelemetry for comprehensive observability across all services. This includes metrics, traces, and logs for monitoring and debugging.

## Components

### Metrics

**Prometheus** - Metrics collection and storage
- System metrics (CPU, memory, disk, network)
- Application metrics (request count, latency, error rate)
- Business metrics (trades, portfolio value, active users)

### Tracing

**OpenTelemetry** - Distributed tracing
- Request tracing across services
- Performance analysis
- Dependency mapping
- Latency optimization

### Logging

**Structured Logging** - Centralized log aggregation
- JSON-formatted logs
- Log levels (debug, info, warn, error)
- Correlation IDs for request tracing
- Log retention policies

### Alerting

**Prometheus Alertmanager** - Alert management
- Custom alert rules
- Notification channels (email, Slack, PagerDuty)
- Incident response workflows
- Alert escalation policies

## Setup

### Local Development

```bash
# Start Prometheus
docker run -p 9090:9090 prom/prometheus

# Start Grafana
docker run -p 3000:3000 grafana/grafana

# Start Jaeger (for tracing)
docker run -p 14268:14268 -p 16686:16686 jaegertracing/all-in-one
```

### Production

See [infrastructure/](../infrastructure/) for production deployment configurations.

## Metrics

### System Metrics

- CPU usage
- Memory usage
- Disk I/O
- Network traffic
- Container health

### Application Metrics

- Request rate
- Request latency (p50, p95, p99)
- Error rate
- Active connections
- Queue depth

### Business Metrics

- Trades per minute
- Portfolio value
- Active users
- API key usage
- Data source latency

## Tracing

### Trace Format

Traces follow the OpenTelemetry standard with:

- Trace ID - Unique identifier for the entire trace
- Span ID - Unique identifier for each operation
- Parent Span ID - Links spans to their parent
- Attributes - Key-value pairs for metadata
- Events - Timestamped events within spans
- Links - Links to other traces

### Instrumentation

Automatic instrumentation is enabled for:

- HTTP requests
- Database queries
- WebSocket connections
- External API calls

Custom instrumentation:

```typescript
import { trace } from '@opentelemetry/api'

const tracer = trace.getTracer('veyra-service')

const span = tracer.startSpan('custom-operation', {
  attributes: {
    'operation.type': 'calculation',
    'operation.complexity': 'high'
  }
})

try {
  // Your code here
  span.setStatus({ code: SpanStatusCode.OK })
} catch (error) {
  span.recordException(error)
  span.setStatus({ code: SpanStatusCode.ERROR, message: error.message })
  throw error
} finally {
  span.end()
}
```

## Logging

### Log Format

```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "info",
  "message": "Request received",
  "trace_id": "abc123",
  "span_id": "def456",
  "service": "api-gateway",
  "context": {
    "user_id": "user123",
    "request_id": "req456"
  }
}
```

### Log Levels

- **debug** - Detailed debugging information
- **info** - General informational messages
- **warn** - Warning messages for potential issues
- **error** - Error messages for failures
- **fatal** - Critical errors requiring immediate attention

### Structured Logging

```typescript
import { logger } from '@veyra/shared-utils'

logger.info('User logged in', {
  user_id: 'user123',
  ip_address: '192.168.1.1',
  timestamp: new Date().toISOString()
})
```

## Dashboards

### Grafana Dashboards

Pre-configured dashboards include:

- **System Overview** - CPU, memory, disk, network metrics
- **API Performance** - Request rate, latency, error rate
- **Business Metrics** - Trades, portfolio value, active users
- **Database Performance** - Query latency, connection pool
- **Cache Performance** - Hit rate, memory usage, eviction rate

### Custom Dashboards

Create custom dashboards in Grafana using the Prometheus data source.

## Alerting

### Alert Rules

Example alert rules:

```yaml
groups:
  - name: veyra_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors/second"

      - alert: HighLatency
        expr: histogram_quantile(0.95, http_request_duration_seconds) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High latency detected"
          description: "P95 latency is {{ $value }} seconds"
```

### Notification Channels

Configure notification channels in Alertmanager:

- Email
- Slack
- PagerDuty
- Microsoft Teams
- Webhooks

## Performance Monitoring

### Key Performance Indicators (KPIs)

- **API Latency** - P95 < 100ms
- **Error Rate** - < 0.1%
- **Throughput** - > 1000 requests/second
- **Availability** - > 99.9%

### Performance Budgets

Define performance budgets for:

- API response times
- Page load times
- Database query times
- External API call times

## Troubleshooting

### Common Issues

**High Latency**
1. Check traces to identify slow operations
2. Review database query performance
3. Check for external API delays
4. Review system resource usage

**High Error Rate**
1. Check error logs for patterns
2. Review recent deployments
3. Check external service status
4. Review rate limiting configuration

**Memory Leaks**
1. Monitor memory usage over time
2. Check for unbounded caches
3. Review connection pool settings
4. Check for event listener leaks

## Best Practices

1. **Instrument Early** - Add observability from the start
2. **Use Structured Logging** - Include context in all logs
3. **Set Meaningful Alerts** - Alert on actionable issues
4. **Review Regularly** - Monitor dashboards and alerts
5. **Optimize Continuously** - Use observability data for improvements

## Resources

- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
