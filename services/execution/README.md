# Execution Service

Private pre-public workstream for broker connectivity and trade execution.

## Build Order

1. Paper-trading ledger
2. Broker sandbox adapters
3. Human-approved live execution
4. Reconciliation, cancel/replace, and recovery flows

## Release Gate

- no autonomous live trades
- every live order has policy approval and an audit receipt
- broker failures are replay-tested
- paper and live modes are impossible to confuse in the UI or API
