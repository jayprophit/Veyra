# Fine-Tuning Pipeline Documentation

## Overview

The fine-tuning pipeline provides efficient methods for adapting pre-trained models to specific domains and tasks. This enables Veyra to build specialized models without training from scratch.

## Methods

### LoRA (Low-Rank Adaptation)

**Purpose**: Efficient fine-tuning with low-rank matrix decomposition

**Advantages**:
- Reduced memory usage
- Faster training
- Smaller model size
- Easy to deploy
- Can be combined with other methods

**Implementation**:
```python
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, TrainingArguments, Trainer

# Load base model
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf")

# Configure LoRA
lora_config = LoraConfig(
    r=16,  # rank
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

# Apply LoRA
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# Training configuration
training_args = TrainingArguments(
    output_dir="./lora-finetuned",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    warmup_steps=100,
    logging_steps=10,
    save_steps=100,
    fp16=True,
)

# Train
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
)

trainer.train()
```

### QLoRA (Quantized LoRA)

**Purpose**: LoRA with quantization for even lower memory usage

**Advantages**:
- Extremely low memory usage
- Can fine-tune on consumer GPUs
- Maintains performance
- Fast training
- Production-ready

**Implementation**:
```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

# Quantization configuration
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)

# Load model with quantization
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    quantization_config=bnb_config,
    device_map="auto"
)

# Prepare model for k-bit training
model = prepare_model_for_kbit_training(model)

# Configure LoRA
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

# Apply LoRA
model = get_peft_model(model, lora_config)
```

### Adapter Layers

**Purpose**: Add trainable adapter layers to the model

**Advantages**:
- Modular fine-tuning
- Easy to swap adapters
- Small parameter increase
- Good performance
- Flexible

**Implementation**:
```python
from transformers import AdapterType, AutoModelForSequenceClassification

# Load base model
model = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased")

# Add adapter
model.add_adapter("finance", AdapterType.text_task)
model.train_adapter("finance")

# Training
training_args = TrainingArguments(
    output_dir="./adapter-finetuned",
    num_train_epochs=3,
    per_device_train_batch_size=32,
    learning_rate=1e-4,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
)

trainer.train()
```

### Full Fine-Tuning

**Purpose**: Train all model parameters

**Advantages**:
- Maximum performance
- Complete adaptation
- No limitations
- Best for critical models

**Disadvantages**:
- High memory usage
- Slow training
- Large model size
- Requires significant compute

**Implementation**:
```python
from transformers import AutoModelForCausalLM, TrainingArguments, Trainer

# Load base model
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf")

# Training configuration
training_args = TrainingArguments(
    output_dir="./full-finetuned",
    num_train_epochs=3,
    per_device_train_batch_size=8,
    gradient_accumulation_steps=2,
    learning_rate=1e-5,
    warmup_steps=500,
    logging_steps=10,
    save_steps=100,
    fp16=True,
    deepspeed="./ds_config.json",  # Use DeepSpeed for distributed training
)

# Train
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
)

trainer.train()
```

## Pipeline Architecture

```
Fine-Tuning Pipeline
├── Data Preparation
│   ├── Data Loading
│   ├── Data Cleaning
│   ├── Data Formatting
│   ├── Tokenization
│   └── Dataset Splitting
├── Model Preparation
│   ├── Model Loading
│   ├── Quantization (optional)
│   ├── LoRA Configuration
│   ├── Adapter Configuration
│   └── Model Compilation
├── Training
│   ├── Training Loop
│   ├── Gradient Accumulation
│   ├── Mixed Precision
│   ├── Distributed Training
│   └── Checkpointing
├── Evaluation
│   ├── Validation Metrics
│   ├── Test Metrics
│   ├── Performance Analysis
│   └── Error Analysis
└── Export
    ├── Model Export
    ├── Adapter Export
    ├── Quantization
    └── Deployment
```

## Data Preparation

### Data Loading

```python
from datasets import load_dataset

# Load dataset
dataset = load_dataset("your-dataset-name")

# Or load from local files
dataset = load_dataset("csv", data_files="data.csv")
```

### Data Formatting

```python
def format_data_for_finetuning(examples):
    # Format data for instruction tuning
    formatted = []
    for example in examples:
        formatted.append({
            "instruction": example["instruction"],
            "input": example.get("input", ""),
            "output": example["output"]
        })
    return formatted
```

### Tokenization

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
tokenizer.pad_token = tokenizer.eos_token

def tokenize_function(examples):
    return tokenizer(
        examples["text"],
        truncation=True,
        max_length=512,
        padding="max_length"
    )

tokenized_dataset = dataset.map(tokenize_function, batched=True)
```

### Dataset Splitting

```python
# Split dataset
train_test_split = dataset["train"].train_test_split(test_size=0.1)
train_dataset = train_test_split["train"]
eval_dataset = train_test_split["test"]

# Further split for validation
train_val_split = train_dataset.train_test_split(test_size=0.1)
train_dataset = train_val_split["train"]
val_dataset = train_val_split["test"]
```

## Training Configuration

### Hyperparameters

```python
training_args = TrainingArguments(
    output_dir="./output",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    warmup_ratio=0.03,
    weight_decay=0.01,
    logging_steps=10,
    save_steps=100,
    eval_steps=100,
    evaluation_strategy="steps",
    save_strategy="steps",
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    greater_is_better=False,
    fp16=True,
    deepspeed="./ds_config.json",
)
```

### DeepSpeed Configuration

```json
{
  "train_batch_size": 32,
  "gradient_accumulation_steps": 4,
  "optimizer": {
    "type": "AdamW",
    "params": {
      "lr": "2e-4",
      "betas": [0.9, 0.999],
      "eps": "1e-8"
    }
  },
  "scheduler": {
    "type": "WarmupLR",
    "params": {
      "warmup_min_lr": "auto",
      "warmup_max_lr": "2e-4",
      "warmup_num_steps": "auto"
    }
  },
  "fp16": {
    "enabled": "auto"
  },
  "zero_optimization": {
    "stage": 2,
    "offload_optimizer": {
      "device": "cpu"
    },
    "offload_param": {
      "device": "cpu"
    }
  }
}
```

## Evaluation

### Metrics

```python
import numpy as np
from sklearn.metrics import accuracy_score, f1_score

def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)
    
    accuracy = accuracy_score(labels, predictions)
    f1 = f1_score(labels, predictions, average='weighted')
    
    return {
        "accuracy": accuracy,
        "f1": f1
    }
```

### Evaluation Loop

```python
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    compute_metrics=compute_metrics,
)

trainer.train()
```

## Export and Deployment

### Model Export

```python
# Save LoRA adapters
model.save_pretrained("./lora-adapters")

# Merge LoRA adapters with base model
merged_model = model.merge_and_unload()
merged_model.save_pretrained("./merged-model")
```

### Quantization for Deployment

```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig

# Load model
model = AutoModelForCausalLM.from_pretrained("./merged-model")

# Quantize for deployment
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4"
)

quantized_model = AutoModelForCausalLM.from_pretrained(
    "./merged-model",
    quantization_config=quantization_config
)
```

## Configuration

```bash
# .env
FINETUNING_ENABLED=true
FINETUNING_METHOD=lora
FINETUNING_RANK=16
FINETUNING_ALPHA=32
FINETUNING_DROPOUT=0.05

TRAINING_EPOCHS=3
BATCH_SIZE=4
GRADIENT_ACCUMULATION=4
LEARNING_RATE=2e-4
WARMUP_RATIO=0.03

QUANTIZATION_ENABLED=true
QUANTIZATION_BITS=4
DEEPSPEED_ENABLED=true
DEEPSPEED_STAGE=2
```

## Best Practices

1. **Start Small**: Start with smaller models and datasets
2. **Monitor Closely**: Monitor training metrics closely
3. **Validate Thoroughly**: Validate models before deployment
4. **Use LoRA**: Use LoRA for efficiency
5. **Quantize**: Quantize for deployment
6. **Version Everything**: Version models and data
7. **Document**: Document experiments and results
8. **Iterate**: Iterate quickly with experiments

## Future Enhancements

- Automated hyperparameter tuning
- Neural architecture search
- Multi-task learning
- Continual learning
- Federated learning
- Active learning
- Curriculum learning
- Meta-learning
