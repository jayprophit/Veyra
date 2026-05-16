# AI Architecture

## Current State

The active repository does not yet contain a production AI system. It contains planning workstreams and a local-first path for adding them safely.

## Target Components

```text
AI Broker
    model routing
    budget policy
    tool permissions
    audit records

Agent Runtime
    planner
    analyst
    researcher
    reviewer
    human approval gates

Model Lab
    evaluation sets
    fine-tuning
    retrieval experiments
    model training research

Visual Learning
    frame ingestion
    annotation
    multimodal evaluation
    later model training
```

## Model Strategy

Veyra should not start by training a large language model from scratch. The practical sequence is:

1. Run local open models for private inference.
2. Add retrieval, tools, policies, and evaluations around them.
3. Fine-tune smaller specialist models only after collecting licensed data and repeatable benchmarks.
4. Consider from-scratch training only when the dataset, compute budget, evaluation harness, and business reason justify it.

Training a serious LLM from scratch is a research program involving data governance, tokenizer design, distributed training, evaluation, safety testing, and substantial GPU capacity. CPU-only training is not a realistic path for that class of model.

## Non-Negotiable Controls

- No direct unrestricted access from an agent to live trading, fund movement, infrastructure mutation, or destructive data actions.
- Every tool call has policy, identity, budget, and audit metadata.
- Human approval is required for live execution until the platform has strong evidence, legal review, and rollback paths.
- Speculative material is treated as a hypothesis source only. It does not become a trading signal until provenance, tests, and out-of-sample performance support it.

## Near-Term Deliverables

- AI broker interface and policy engine
- Tool registry with allowlists
- Evaluation datasets for finance, code, and multimodal tasks
- Visual-learning ingestion contracts
- Memory boundaries between user data, market data, and research artifacts
