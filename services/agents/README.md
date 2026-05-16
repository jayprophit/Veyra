# Agents Service

Private pre-public workstream for AI agents.

## Purpose

- Coordinate bounded financial assistants
- Route tasks through policy checks
- Require human approval for sensitive actions
- Emit audit records for every tool call and decision

## Initial Scope

1. Market research agent
2. Portfolio analysis agent
3. Alert triage agent
4. Operations assistant for internal maintenance

## Release Gate

This service is not public-release ready until agents have:

- explicit tool allowlists
- deterministic policy checks
- human approval for trades, data deletion, and infrastructure actions
- replayable audit logs
- evaluation tests for refusal, escalation, and failure handling
