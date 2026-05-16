# AI Broker Service

Private pre-public workstream for model routing and AI policy enforcement.

## Purpose

- Route requests across local and hosted models
- Enforce budgets, rate limits, and tool permissions
- Validate prompts and structured outputs
- Centralize model-request logging

## Dependencies

- canonical auth and audit identity
- memory service for approved retrieval paths
- agent service for bounded tool execution

## Release Gate

- provider abstraction works locally first
- cost ceilings and fallback behavior are tested
- unsafe tool requests are rejected by policy
- model outputs are validated before use by downstream services
