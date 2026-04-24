# Financial Master - Free Tier LLM Integration Guide
## Zero-Cost AI with Ollama + Optional Paid Upgrade Path

---

## Executive Summary

| Tier | Cost | Models | Best For |
|------|------|--------|----------|
| **Free (Local)** | £0/month | Ollama (Llama, Qwen, Phi) | Daily operations, summaries, analysis |
| **Budget API** | £5-15/month | GPT-4o-mini, Claude Haiku | Complex reasoning, when local insufficient |
| **Premium** | £20-50/month | GPT-4, Claude Sonnet | Advanced analysis, coding, critical decisions |

**Recommendation:** Start with Free tier, upgrade only when needed.

---

## Free Tier: Ollama Setup

### 1. Installation

**Windows:**
```powershell
# Download from https://ollama.com/download
# Or using winget
winget install Ollama.Ollama
```

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. Pull Financial Models

```bash
# Essential models for Financial Master
ollama pull llama3.2:3b      # Fast summaries, alerts (3B params)
ollama pull llama3.1:8b      # Better reasoning, analysis (8B params)
ollama pull qwen2.5:7b       # Excellent for structured data/JSON
ollama pull phi4             # Microsoft, good math/reasoning
ollama pull codellama        # Code generation for automation

# Verify installation
ollama list
```

### 3. Start Server

```bash
# Windows/Mac: Auto-starts with app
# Linux/manual:
ollama serve

# Verify
curl http://localhost:11434/api/tags
```

### 4. Test in Python

```python
from llm_integration import LLMManager, LLMConfig

# Configure for free tier only
config = LLMConfig(
    primary_provider="ollama",
    fallback_to_paid=False,  # £0 cost guarantee
    ollama_model="llama3.2:3b"
)

llm = LLMManager(config)

# Generate analysis
result = llm.generate(
    "Analyze portfolio risk for 60% stocks, 30% bonds, 10% crypto",
    system="You are a professional risk analyst. Be concise."
)

print(result["text"])
print(f"Cost: £{result['cost_usd']:.4f}")  # Always 0.0000
```

---

## Model Selection Guide

### By Task Type

| Task | Recommended Model | Why |
|------|---------------------|-----|
| **Portfolio Summaries** | llama3.2:3b | Fast, good enough |
| **Tax Analysis** | llama3.1:8b | Better reasoning |
| **JSON/Structured Output** | qwen2.5:7b | Excellent formatting |
| **Math/Calculations** | phi4 | Microsoft training |
| **Code Generation** | codellama | Specialized |
| **Complex Planning** | llama3.1:70b* | Best reasoning |

*Requires 40GB+ VRAM or runs slow on CPU

### By Hardware

| Hardware | Best Models | Speed |
|----------|-------------|-------|
| High-end GPU (RTX 4090) | llama3.1:70b, Mixtral 8x7B | Fast |
| Mid GPU (RTX 3060) | llama3.1:8b, qwen2.5:7b | Fast |
| Low GPU / Apple Silicon | llama3.2:3b, phi4 | Good |
| CPU Only | llama3.2:1b, phi4:mini | Slower |

---

## Optional Paid Upgrades

### When to Upgrade

Upgrade from Free to Paid when:
- Local models too slow for your hardware
- Need advanced reasoning (GPT-4 class)
- Complex multi-step financial planning
- API integrations requiring high accuracy

### Budget Option: GPT-4o-mini

| Metric | Value |
|--------|-------|
| Input | $0.15 per 1M tokens (~£0.12) |
| Output | $0.60 per 1M tokens (~£0.47) |
| Typical Month | £3-8 for moderate usage |
| Quality | Excellent for most tasks |

```python
# Enable paid fallback
config = LLMConfig(
    primary_provider="ollama",
    fallback_to_paid=True,
    openai_api_key="sk-...",
    openai_model="gpt-4o-mini"
)
```

### Claude Haiku (Alternative)

| Metric | Value |
|--------|-------|
| Speed | Very fast |
| Cost | ~$0.25 per 1K queries |
| Strength | Reasoning, instruction following |

---

## Cost Examples

### Scenario: Daily Portfolio Analysis

**Free Tier (Ollama):**
- 50 queries/day × 30 days = 1,500 queries
- Cost: £0.00
- Speed: Depends on hardware
- Works offline: Yes

**Budget Tier (GPT-4o-mini fallback):**
- 80% local (1,200 queries): £0
- 20% API (300 queries): ~£1.50
- Total: ~£1.50/month

### Scenario: Complex Tax Planning

**Free Tier:**
- llama3.1:8b handles most tax queries
- Cost: £0
- Quality: Good for standard cases

**Budget Tier:**
- Complex optimization → GPT-4o-mini
- 50 complex queries/month: ~£2
- Total: ~£2/month

---

## Advanced: Fine-Tuning Local Models

### Option 1: Ollama Modelfiles

Create specialized financial advisors:

```dockerfile
# File: financial_advisor.modelfile
FROM llama3.1:8b

SYSTEM """You are a UK financial advisor specializing in:
- ISA and SIPP optimization
- CGT tax planning
- Portfolio rebalancing
- FIRE calculations

Always provide specific numbers and cite UK tax rules.
Be conservative in estimates."""

PARAMETER temperature 0.3
PARAMETER top_p 0.9
```

```bash
# Create custom model
ollama create financial-advisor -f financial_advisor.modelfile

# Use it
ollama run financial-advisor
```

### Option 2: LoRA Adapters (Advanced)

Fine-tune with your portfolio data:

```python
# Using unsloth for efficient fine-tuning
# Requires: pip install unsloth

from unsloth import FastLanguageModel
import torch

# Load base model
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/llama-3-8b-bnb-4bit",
    max_seq_length=2048,
    dtype=torch.bfloat16,
)

# Add LoRA adapters
model = FastLanguageModel.get_peft_model(
    model,
    r=16,  # LoRA rank
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_alpha=16,
    use_gradient_checkpointing="unsloth",
)

# Train on your financial Q&A data
# ... training code ...

# Save adapter
model.save_pretrained("./models/financial_lora")
```

### Option 3: RAG (Retrieval-Augmented Generation)

Use your documents without fine-tuning:

```python
# Store financial docs in vector DB
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings

# Create embeddings using local model
embeddings = OllamaEmbeddings(model="nomic-embed-text")

# Store documents
vectorstore = Chroma.from_documents(
    documents=financial_docs,
    embedding=embeddings,
    persist_directory="./data/vectorstore"
)

# Query with context
retriever = vectorstore.as_retriever()
relevant_docs = retriever.get_relevant_documents("tax loss harvesting")

# Generate with context
context = "\n".join([d.page_content for d in relevant_docs])
prompt = f"Context: {context}\n\nQuestion: {query}"
result = llm.generate(prompt)
```

---

## Hardware Recommendations

### Minimum (CPU Only)
- 16GB RAM
- Works with: llama3.2:1b, phi4:mini
- Speed: 5-10 tokens/sec
- Cost: £0

### Recommended (GPU)
- RTX 3060 12GB or Apple M1/M2
- Works with: llama3.1:8b, qwen2.5:7b
- Speed: 30-50 tokens/sec
- Cost: £0

### Optimal (High-end)
- RTX 4090 24GB or Apple M3 Max
- Works with: llama3.1:70b, Mixtral
- Speed: 20-40 tokens/sec (larger models)
- Cost: £0

---

## Troubleshooting

### Ollama Not Responding

```bash
# Check if running
curl http://localhost:11434/api/tags

# Restart
# Windows: Close tray icon, reopen
# Linux/macOS:
killall ollama
ollama serve

# Check logs
# Windows: %LOCALAPPDATA%\Ollama\logs
# macOS: ~/.ollama/logs
# Linux: /var/log/ollama
```

### Out of Memory

```bash
# Use smaller model
ollama pull llama3.2:1b

# Or quantized version
ollama pull llama3.1:8b-q4_0

# Limit context in Python
result = llm.generate(prompt, max_tokens=500)
```

### Slow Performance

```bash
# Check GPU usage
ollama ps

# Pull GPU-optimized model
ollama pull llama3.1:8b-q8_0  # Higher quality, GPU

# Use CPU offloading if needed
# In Ollama modelfile:
PARAMETER num_gpu 20  # Layers on GPU
```

---

## Integration Checklist

- [ ] Install Ollama
- [ ] Pull llama3.2:3b and llama3.1:8b
- [ ] Start Ollama server
- [ ] Test Python integration
- [ ] Verify caching works
- [ ] Test all 8 Financial Master agents
- [ ] Document which tasks use which models
- [ ] Set up fallback (optional)

---

## Summary: Free Tier Benefits

✅ **£0 cost** - Runs entirely locally  
✅ **100% private** - No data leaves your machine  
✅ **Works offline** - No internet required  
✅ **Unlimited queries** - No rate limits  
✅ **Customizable** - Fine-tune for your needs  
✅ **Optional upgrade** - Add API keys anytime  

**Bottom Line:** Start free with Ollama, upgrade to paid APIs only when you need GPT-4-level reasoning.
