# Model Strategy

## Practical Ladder

1. **Use existing open models locally** for inference and private experiments.
2. **Add retrieval and tool use** so the system earns capability from data and software, not only model size.
3. **Fine-tune specialists** when evaluation data proves a gap.
4. **Train adapters or small domain models** when latency, privacy, or cost justify them.
5. **Train from scratch** only after the first four stages prove insufficient.

## Why Not Start With A New LLM

A from-scratch LLM requires:

- licensed corpora
- tokenizer design
- distributed GPU training
- evaluation suites
- safety testing
- serving infrastructure
- repeated retraining

That is not a one-off feature and is not realistic on CPU-only hardware for a useful general model. The early moat for Veyra is more likely to come from clean financial data, replayable workflows, asset knowledge, and strict execution policy.

## Veyra Target

The private pre-public target should be:

- local open-model inference
- domain retrieval
- specialist evaluators
- multimodal ingestion
- policy-governed tool use
- reproducible benchmark reports

The model lab can later decide whether a proprietary model is justified by evidence rather than aspiration.
