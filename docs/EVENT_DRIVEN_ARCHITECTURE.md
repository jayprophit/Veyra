# Event-Driven Architecture Documentation

## Overview

Veyra uses an event-driven architecture to decouple components and enable asynchronous communication. This architecture supports scalability, resilience, and loose coupling between services.

## Architecture

```
┌─────────────┐
│   Producer  │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ Event Bus   │
│ (Message    │
│  Queue)     │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│  Consumer   │
└─────────────┘
```

## Components

### Event Bus

**Message Queue**
- Redis (initial)
- RabbitMQ (future)
- Kafka (future)
- NATS (future)

**Event Router**
- Topic-based routing
- Pattern matching
- Content-based routing
- Load balancing

**Event Store**
- Immutable event log
- Event replay
- Audit trail
- Event sourcing

### Event Types

**Market Events**
```typescript
interface MarketEvent {
  type: 'market_price_update' | 'market_volume_update' | 'market_news'
  symbol: string
  data: any
  timestamp: Date
}
```

**Trading Events**
```typescript
interface TradingEvent {
  type: 'order_placed' | 'order_filled' | 'order_cancelled' | 'position_opened' | 'position_closed'
  orderId: string
  data: any
  timestamp: Date
}
```

**Agent Events**
```typescript
interface AgentEvent {
  type: 'agent_started' | 'agent_completed' | 'agent_failed' | 'agent_communication'
  agentId: string
  data: any
  timestamp: Date
}
```

**System Events**
```typescript
interface SystemEvent {
  type: 'service_started' | 'service_stopped' | 'error_occurred' | 'alert_triggered'
  service: string
  data: any
  timestamp: Date
}
```

### Event Schema

**Base Event**
```typescript
interface Event {
  id: string
  type: string
  source: string
  data: any
  metadata: Record<string, any>
  timestamp: Date
  correlationId?: string
  causationId?: string
}
```

## Event Flow

### Publishing Events

```typescript
async function publishEvent(event: Event) {
  await eventBus.publish(event.type, event)
}
```

### Subscribing to Events

```typescript
async function subscribeToEvents(
  eventType: string,
  handler: (event: Event) => Promise<void>
) {
  await eventBus.subscribe(eventType, handler)
}
```

### Event Processing

```typescript
async function processEvent(event: Event) {
  try {
    await handleEvent(event)
    await acknowledgeEvent(event.id)
  } catch (error) {
    await handleError(event, error)
  }
}
```

## Event Patterns

### Publish-Subscribe

```typescript
// Publisher
await eventBus.publish('market.price_update', {
  symbol: 'AAPL',
  price: 150.00,
  timestamp: new Date()
})

// Subscribers
eventBus.subscribe('market.price_update', handlePriceUpdate)
eventBus.subscribe('market.price_update', updateDashboard)
eventBus.subscribe('market.price_update', triggerAlerts)
```

### Request-Response

```typescript
// Request
const response = await eventBus.request('trading.execute_order', {
  symbol: 'AAPL',
  quantity: 100,
  side: 'buy'
})

// Response handler
eventBus.respond('trading.execute_order', handleOrderExecution)
```

### Event Sourcing

```typescript
// Store events
await eventStore.append({
  type: 'order_placed',
  data: { orderId, symbol, quantity, side },
  timestamp: new Date()
})

// Replay events
const events = await eventStore.replay(orderId)
const state = rebuildState(events)
```

### CQRS (Command Query Responsibility Segregation)

```typescript
// Command
await eventBus.publish('commands.place_order', {
  orderId,
  symbol,
  quantity,
  side
})

// Query
const order = await queryService.getOrder(orderId)
```

## Message Queue Implementation

### Redis (Initial)

```typescript
class RedisEventBus {
  async publish(topic: string, event: Event) {
    await redis.publish(topic, JSON.stringify(event))
  }
  
  async subscribe(topic: string, handler: Function) {
    const subscriber = redis.duplicate()
    await subscriber.subscribe(topic)
    subscriber.on('message', (channel, message) => {
      handler(JSON.parse(message))
    })
  }
}
```

### RabbitMQ (Future)

```typescript
class RabbitMQEventBus {
  async publish(topic: string, event: Event) {
    await channel.publish(exchange, topic, Buffer.from(JSON.stringify(event)))
  }
  
  async subscribe(topic: string, handler: Function) {
    await channel.assertQueue(queue, { durable: true })
    await channel.bindQueue(queue, exchange, topic)
    await channel.consume(queue, (msg) => {
      handler(JSON.parse(msg.content.toString()))
    })
  }
}
```

## Event Store

### Implementation

```typescript
class EventStore {
  async append(event: Event) {
    await db.insert('events', {
      id: event.id,
      type: event.type,
      data: JSON.stringify(event.data),
      timestamp: event.timestamp,
      correlationId: event.correlationId,
      causationId: event.causationId
    })
  }
  
  async replay(aggregateId: string): Promise<Event[]> {
    return await db.query('events')
      .where('aggregateId', aggregateId)
      .orderBy('timestamp')
  }
}
```

## Event Correlation

### Correlation ID

```typescript
const correlationId = generateUUID()

// Pass correlation ID through event chain
const event1 = { ...data, correlationId }
const event2 = { ...data, correlationId, causationId: event1.id }
```

### Event Tracing

```typescript
async function traceEvent(correlationId: string) {
  const events = await eventStore.findByCorrelationId(correlationId)
  return buildEventChain(events)
}
```

## Error Handling

### Dead Letter Queue

```typescript
async function handleFailedEvent(event: Event, error: Error) {
  await deadLetterQueue.add({
    event,
    error: error.message,
    timestamp: new Date(),
    retryCount: 0
  })
}
```

### Retry Logic

```typescript
async function retryFailedEvent(deadLetterEvent: DeadLetterEvent) {
  if (deadLetterEvent.retryCount < maxRetries) {
    await eventBus.publish(deadLetterEvent.event.type, deadLetterEvent.event)
  } else {
    await alertService.notify(deadLetterEvent)
  }
}
```

## Configuration

```bash
# .env
EVENT_BUS_TYPE=redis
REDIS_HOST=localhost
REDIS_PORT=6379

EVENT_STORE_ENABLED=true
EVENT_STORE_TYPE=postgresql
EVENT_STORE_RETENTION_DAYS=365

DEAD_LETTER_QUEUE_ENABLED=true
MAX_RETRIES=3
RETRY_DELAY_MS=1000
```

## Best Practices

1. **Event Naming**: Use descriptive event names
2. **Event Versioning**: Version event schemas
3. **Idempotency**: Make event handlers idempotent
4. **Error Handling**: Handle errors gracefully
5. **Monitoring**: Monitor event flow
6. **Testing**: Test event handlers
7. **Documentation**: Document event schemas
8. **Security**: Secure event bus access

## Future Enhancements

- Event schema registry
- Event validation
- Event transformation
- Event aggregation
- Complex event processing
- Stream processing
- Event-driven microservices
- Event mesh
