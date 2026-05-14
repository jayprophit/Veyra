import { NodeSDK } from '@opentelemetry/sdk-node'
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node'
import { Resource } from '@opentelemetry/resources'
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions'
import { JaegerExporter } from '@opentelemetry/exporter-trace-jaeger'
import { PrometheusExporter } from '@opentelemetry/exporter-prometheus'
import { BatchSpanProcessor } from '@opentelemetry/sdk-trace-base'
import { MeterProvider } from '@opentelemetry/sdk-metrics'

// Initialize OpenTelemetry SDK
const sdk = new NodeSDK({
  resource: new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: 'veyra-api-gateway',
    [SemanticResourceAttributes.SERVICE_VERSION]: process.env.SERVICE_VERSION || '1.0.0',
    [SemanticResourceAttributes.DEPLOYMENT_ENVIRONMENT]: process.env.NODE_ENV || 'development',
  }),
  instrumentations: [getNodeAutoInstrumentations()],
  traceExporter: new JaegerExporter({
    endpoint: process.env.JAEGER_ENDPOINT || 'http://localhost:14268/api/traces',
  }),
  metricReader: new PrometheusExporter({
    port: process.env.METRICS_PORT || 9464,
  }),
})

// Initialize SDK
sdk.start()

// Export metrics provider for custom metrics
export const meterProvider = new MeterProvider()

export default sdk
