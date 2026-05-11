"""
Veyra - Free Tier LLM Integration
=============================================
Zero-cost LLM operations using Ollama + local models
Optional: Paid tier fallback (OpenAI, Anthropic)

Features:
- Ollama local inference (completely free)
- Hugging Face Transformers (local)
- Llama.cpp (quantized models, low resource)
- Optional: OpenAI/Anthropic as premium fallback
- Model switching based on task complexity
- Caching for repeated queries

Cost: £0 (Free Tier) | Optional: £10-50/month (Paid Tier)
"""

import os
import json
import time
import hashlib
from typing import Optional, Dict, List, Any, Literal
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import sqlite3

# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class LLMConfig:
    """Configuration for LLM providers with free tier priority"""
    # Primary: Free Local Options
    primary_provider: Literal["ollama", "llamacpp", "huggingface"] = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"  # 3B params, fast, good for analysis
    ollama_fallback_model: str = "llama3.1:8b"  # More powerful for complex tasks
    
    # Secondary: Free tier HuggingFace
    hf_model: str = "microsoft/DialoGPT-medium"  # Free, small, good for chat
    hf_use_local: bool = True  # Always use local, not API
    
    # Tertiary: Llama.cpp (for very low resource)
    llamacpp_model_path: str = "./models/llama-3-8b-q4.gguf"
    llamacpp_n_threads: int = 4
    
    # Premium Fallback (optional, set to None for free tier)
    openai_api_key: Optional[str] = None  # os.getenv("OPENAI_API_KEY")
    openai_model: str = "gpt-4o-mini"  # Cheapest OpenAI model
    anthropic_api_key: Optional[str] = None  # os.getenv("ANTHROPIC_API_KEY")
    anthropic_model: str = "claude-3-haiku-20240307"  # Cheapest Claude
    
    # Behavior
    use_cache: bool = True
    cache_ttl_hours: int = 24
    max_retries: int = 3
    timeout_seconds: int = 30
    fallback_to_paid: bool = False  # Set True to enable paid fallback
    
    # Task routing
    simple_tasks_local: bool = True  # Simple queries use local models
    complex_tasks_paid: bool = False  # Complex tasks use paid (if enabled)


# ============================================================================
# RESPONSE CACHE (SQLite-backed)
# ============================================================================

class LLMCache:
    """SQLite-backed cache for LLM responses to reduce API calls"""
    
    def __init__(self, cache_path: str = "./data/llm_cache.db"):
        self.cache_path = cache_path
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite cache table"""
        conn = sqlite3.connect(self.cache_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS llm_cache (
                query_hash TEXT PRIMARY KEY,
                provider TEXT,
                model TEXT,
                prompt TEXT,
                response TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ttl_hours INTEGER DEFAULT 24
            )
        """)
        conn.commit()
        conn.close()
    
    def get(self, prompt: str, provider: str, model: str) -> Optional[str]:
        """Get cached response if valid"""
        query_hash = hashlib.sha256(f"{provider}:{model}:{prompt}".encode()).hexdigest()
        
        conn = sqlite3.connect(self.cache_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT response, created_at, ttl_hours FROM llm_cache 
            WHERE query_hash = ?
        """, (query_hash,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            response, created_at, ttl_hours = result
            created = datetime.fromisoformat(created_at)
            if datetime.now() - created < timedelta(hours=ttl_hours):
                return response
        return None
    
    def set(self, prompt: str, provider: str, model: str, response: str, ttl_hours: int = 24):
        """Cache a response"""
        query_hash = hashlib.sha256(f"{provider}:{model}:{prompt}".encode()).hexdigest()
        
        conn = sqlite3.connect(self.cache_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO llm_cache 
            (query_hash, provider, model, prompt, response, ttl_hours)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (query_hash, provider, model, prompt, response, ttl_hours))
        conn.commit()
        conn.close()


# ============================================================================
# OLLAMA PROVIDER (Free, Local)
# ============================================================================

class OllamaProvider:
    """
    Ollama provider for completely free local inference.
    
    Setup:
        1. Install Ollama: https://ollama.com/download
        2. Pull models: ollama pull llama3.2:3b
        3. Start server: ollama serve
    
    Models for Financial Analysis:
        - llama3.2:3b (fast, good for summaries)
        - llama3.1:8b (better reasoning)
        - qwen2.5:7b (excellent for structured data)
        - phi4 (Microsoft, good for math)
        - codellama (for code generation)
    """
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.base_url = config.ollama_base_url
        self.available = self._check_availability()
    
    def _check_availability(self) -> bool:
        """Check if Ollama server is running"""
        try:
            import requests
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def list_models(self) -> List[str]:
        """List available local models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [m["name"] for m in data.get("models", [])]
        except Exception as e:
            print(f"Error listing models: {e}")
        return []
    
    def generate(
        self, 
        prompt: str, 
        model: Optional[str] = None,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """Generate text using Ollama"""
        import requests
        
        model = model or self.config.ollama_model
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }
        
        if system:
            payload["system"] = system
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.config.timeout_seconds
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "success": True,
                "text": data.get("response", ""),
                "model": model,
                "provider": "ollama",
                "tokens": data.get("eval_count", 0),
                "duration_ms": data.get("total_duration", 0) / 1e6,
                "cost_usd": 0.0  # Free!
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "provider": "ollama"
            }
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """Chat completion using Ollama"""
        
        model = model or self.config.ollama_model
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.config.timeout_seconds
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "success": True,
                "text": data["message"].get("content", ""),
                "model": model,
                "provider": "ollama",
                "cost_usd": 0.0
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "provider": "ollama"
            }


# ============================================================================
# HUGGING FACE LOCAL PROVIDER (Free)
# ============================================================================

class HuggingFaceLocalProvider:
    """
    Local Hugging Face Transformers (no API key needed for local models).
    Good for specialized financial models.
    
    Models:
        - microsoft/DialoGPT-medium (chat)
        - facebook/bart-large-cnn (summarization)
        - ProsusAI/finbert (financial sentiment)
    """
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.model = None
        self.tokenizer = None
        self._load_model()
    
    def _load_model(self):
        """Lazy load the model"""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            
            model_name = self.config.hf_model
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype="auto",
                device_map="auto"
            )
            print(f"✓ Loaded HuggingFace model: {model_name}")
        except ImportError:
            print("⚠ transformers not installed. Run: pip install transformers torch")
        except Exception as e:
            print(f"⚠ Error loading HF model: {e}")
    
    def generate(self, prompt: str, max_tokens: int = 100) -> Dict[str, Any]:
        """Generate using local HF model"""
        if not self.model or not self.tokenizer:
            return {"success": False, "error": "Model not loaded"}
        
        try:
            import torch
            
            inputs = self.tokenizer(prompt, return_tensors="pt")
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    do_sample=True,
                    temperature=0.7
                )
            
            text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            return {
                "success": True,
                "text": text,
                "provider": "huggingface_local",
                "cost_usd": 0.0
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


# ============================================================================
# PAID FALLBACK PROVIDERS (Optional)
# ============================================================================

class OpenAIProvider:
    """OpenAI API - Premium tier (optional)"""
    
    def __init__(self, api_key: Optional[str], model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        self.available = api_key is not None
    
    def generate(self, prompt: str, max_tokens: int = 1000) -> Dict[str, Any]:
        if not self.available:
            return {"success": False, "error": "OpenAI API key not configured"}
        
        try:
            import openai
            openai.api_key = self.api_key
            
            response = openai.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            
            return {
                "success": True,
                "text": response.choices[0].message.content,
                "provider": "openai",
                "model": self.model,
                "cost_usd": self._estimate_cost(response.usage)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _estimate_cost(self, usage) -> float:
        """Estimate cost in USD"""
        # GPT-4o-mini pricing (as of 2024)
        input_cost = usage.prompt_tokens * 0.00000015  # $0.15 per 1M tokens
        output_cost = usage.completion_tokens * 0.0000006  # $0.60 per 1M tokens
        return input_cost + output_cost


class AnthropicProvider:
    """Anthropic Claude API - Premium tier (optional)"""
    
    def __init__(self, api_key: Optional[str], model: str = "claude-3-haiku-20240307"):
        self.api_key = api_key
        self.model = model
        self.available = api_key is not None
    
    def generate(self, prompt: str, max_tokens: int = 1000) -> Dict[str, Any]:
        if not self.available:
            return {"success": False, "error": "Anthropic API key not configured"}
        
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            
            response = client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return {
                "success": True,
                "text": response.content[0].text,
                "provider": "anthropic",
                "model": self.model,
                "cost_usd": 0.0  # Calculate based on usage
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


# ============================================================================
# MAIN LLM MANAGER
# ============================================================================

class LLMManager:
    """
    Central manager for all LLM providers with intelligent routing.
    
    Priority:
    1. Check cache
    2. Try Ollama (free, local)
    3. Try HuggingFace local
    4. Fallback to paid (if enabled)
    
    Usage:
        config = LLMConfig(primary_provider="ollama")
        llm = LLMManager(config)
        
        # Simple query
        result = llm.generate("Summarize this portfolio data...")
        
        # Chat
        result = llm.chat([
            {"role": "system", "content": "You are a financial advisor"},
            {"role": "user", "content": "Should I buy Tesla?"}
        ])
    """
    
    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig()
        self.cache = LLMCache() if self.config.use_cache else None
        
        # Initialize providers
        self.ollama = OllamaProvider(self.config)
        self.hf = HuggingFaceLocalProvider(self.config)
        self.openai = OpenAIProvider(self.config.openai_api_key, self.config.openai_model)
        self.anthropic = AnthropicProvider(self.config.anthropic_api_key, self.config.anthropic_model)
        
        print(f"✓ LLM Manager initialized")
        print(f"  - Ollama: {'Available' if self.ollama.available else 'Not available'}")
        print(f"  - HuggingFace: {'Loaded' if self.hf.model else 'Not loaded'}")
        print(f"  - OpenAI: {'Configured' if self.openai.available else 'Not configured'}")
        print(f"  - Cache: {'Enabled' if self.cache else 'Disabled'}")
    
    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        use_cache: bool = True,
        force_provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate text with automatic provider selection.
        
        Args:
            prompt: The text prompt
            system: System prompt (for chat models)
            temperature: Randomness (0.0-1.0)
            max_tokens: Maximum tokens to generate
            use_cache: Whether to use response cache
            force_provider: Force specific provider ("ollama", "openai", etc.)
        """
        # Check cache
        if use_cache and self.cache and not force_provider:
            cached = self.cache.get(prompt, "any", "any")
            if cached:
                return {
                    "success": True,
                    "text": cached,
                    "cached": True,
                    "cost_usd": 0.0
                }
        
        # Try providers in order
        providers_to_try = self._get_provider_order(force_provider)
        
        last_error = None
        for provider_name in providers_to_try:
            result = self._try_provider(
                provider_name, prompt, system, temperature, max_tokens
            )
            
            if result.get("success"):
                # Cache successful response
                if self.cache and use_cache:
                    self.cache.set(
                        prompt, 
                        result.get("provider", "unknown"),
                        result.get("model", "unknown"),
                        result["text"],
                        self.config.cache_ttl_hours
                    )
                return result
            else:
                last_error = result.get("error")
                print(f"⚠ {provider_name} failed: {last_error}")
        
        # All providers failed
        return {
            "success": False,
            "error": f"All providers failed. Last error: {last_error}",
            "providers_tried": providers_to_try
        }
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        force_provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """Chat completion with message history"""
        # Convert to prompt for non-chat providers
        prompt = self._messages_to_prompt(messages)
        
        # Try providers
        providers_to_try = self._get_provider_order(force_provider)
        
        for provider_name in providers_to_try:
            if provider_name == "ollama" and self.ollama.available:
                return self.ollama.chat(messages, temperature=temperature, max_tokens=max_tokens)
            elif provider_name == "openai" and self.openai.available:
                try:
                    import openai
                    openai.api_key = self.config.openai_api_key
                    response = openai.chat.completions.create(
                        model=self.config.openai_model,
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=temperature
                    )
                    return {
                        "success": True,
                        "text": response.choices[0].message.content,
                        "provider": "openai",
                        "model": self.config.openai_model
                    }
                except Exception as e:
                    print(f"⚠ OpenAI chat failed: {e}")
            # Fallback to generate
            else:
                return self.generate(prompt, temperature=temperature, max_tokens=max_tokens)
        
        return {"success": False, "error": "No providers available"}
    
    def _get_provider_order(self, force_provider: Optional[str] = None) -> List[str]:
        """Determine provider order based on config"""
        if force_provider:
            return [force_provider]
        
        order = []
        
        # Primary: Ollama (free)
        if self.ollama.available:
            order.append("ollama")
        
        # Secondary: HuggingFace (free)
        if self.hf.model:
            order.append("huggingface")
        
        # Tertiary: Paid (if enabled)
        if self.config.fallback_to_paid:
            if self.openai.available:
                order.append("openai")
            if self.anthropic.available:
                order.append("anthropic")
        
        return order
    
    def _try_provider(
        self,
        provider: str,
        prompt: str,
        system: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """Try a specific provider"""
        if provider == "ollama":
            return self.ollama.generate(prompt, system, temperature, max_tokens)
        elif provider == "huggingface":
            return self.hf.generate(prompt, max_tokens)
        elif provider == "openai":
            full_prompt = f"{system}\n\n{prompt}" if system else prompt
            return self.openai.generate(full_prompt, max_tokens)
        elif provider == "anthropic":
            full_prompt = f"{system}\n\n{prompt}" if system else prompt
            return self.anthropic.generate(full_prompt, max_tokens)
        else:
            return {"success": False, "error": f"Unknown provider: {provider}"}
    
    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert chat messages to single prompt"""
        parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                parts.append(f"System: {content}")
            elif role == "assistant":
                parts.append(f"Assistant: {content}")
            else:
                parts.append(f"User: {content}")
        return "\n\n".join(parts) + "\n\nAssistant:"
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of all providers"""
        return {
            "ollama": {
                "available": self.ollama.available,
                "models": self.ollama.list_models() if self.ollama.available else [],
                "default_model": self.config.ollama_model
            },
            "huggingface": {
                "available": self.hf.model is not None,
                "model": self.config.hf_model
            },
            "openai": {
                "available": self.openai.available,
                "model": self.config.openai_model
            },
            "anthropic": {
                "available": self.anthropic.available,
                "model": self.config.anthropic_model
            },
            "config": {
                "fallback_to_paid": self.config.fallback_to_paid,
                "cache_enabled": self.cache is not None,
                "primary_provider": self.config.primary_provider
            }
        }


# ============================================================================
# FINANCIAL AGENT TEMPLATES
# ============================================================================

class FinancialLLMAgents:
    """
    Pre-built LLM prompts for Veyra agents.
    Uses local models (Ollama) by default.
    """
    
    def __init__(self, llm_manager: LLMManager):
        self.llm = llm_manager
    
    def analyze_portfolio(self, portfolio_data: Dict) -> Dict[str, Any]:
        """Agent 5: Portfolio analysis using LLM"""
        system = """You are a professional portfolio analyst. Analyze the portfolio data and provide:
1. Risk assessment
2. Diversification analysis  
3. Rebalancing recommendations
4. Tax optimization suggestions
Be concise, use bullet points, and include specific numbers."""
        
        prompt = f"""Analyze this portfolio:
{json.dumps(portfolio_data, indent=2)}

Provide your analysis in structured format."""
        
        return self.llm.generate(prompt, system=system, temperature=0.3)
    
    def tax_optimization(self, holdings: List[Dict], cgt_allowance: float) -> Dict[str, Any]:
        """Agent 3: Tax optimization recommendations"""
        system = """You are a UK tax specialist focused on CGT optimization. 
Provide specific tax-loss harvesting recommendations and Bed & ISA suggestions.
Consider wash sale rules (30-day rule)."""
        
        prompt = f"""CGT Allowance Remaining: £{cgt_allowance:,.2f}

Holdings:
{json.dumps(holdings, indent=2)}

What tax optimization actions should I take? List specific trades with amounts."""
        
        return self.llm.generate(prompt, system=system, temperature=0.2)
    
    def retirement_projection(
        self,
        current_age: int,
        target_age: int,
        current_savings: float,
        monthly_contribution: float,
        expected_return: float
    ) -> Dict[str, Any]:
        """Agent 2 & 6: Retirement and FIRE projections"""
        system = """You are a retirement planning expert. Calculate projections and provide:
1. Monte Carlo simulation results (best/average/worst case)
2. Probability of reaching goal
3. Required adjustments if off-track
Use conservative estimates."""
        
        years = target_age - current_age
        prompt = f"""Retirement Analysis:
- Current age: {current_age}
- Target retirement: {target_age} ({years} years)
- Current savings: £{current_savings:,.2f}
- Monthly contribution: £{monthly_contribution:,.2f}
- Expected return: {expected_return}%

Run a Monte Carlo simulation (1000 iterations) and provide the 10th, 50th, and 90th percentile outcomes.

Also calculate:
1. Safe Withdrawal Rate (4% rule)
2. FIRE number needed
3. Years to reach FI"""
        
        return self.llm.generate(prompt, system=system, temperature=0.3, max_tokens=2000)
    
    def sentiment_analysis(self, news_headlines: List[str]) -> Dict[str, Any]:
        """Agent 7: Market sentiment analysis"""
        system = """Analyze market sentiment from news headlines.
Score from -1.0 (very bearish) to +1.0 (very bullish).
Identify key themes and risks."""
        
        prompt = f"""News Headlines:
{chr(10).join(f"- {h}" for h in news_headlines)}

Provide:
1. Overall sentiment score (-1.0 to +1.0)
2. Key themes
3. Risk level (low/medium/high)
4. Market outlook (1 sentence)"""
        
        return self.llm.generate(prompt, system=system, temperature=0.4)
    
    def risk_assessment(self, portfolio: Dict, market_conditions: Dict) -> Dict[str, Any]:
        """Agent 4: Risk manager analysis"""
        system = """You are a risk management specialist. Assess portfolio risk considering:
1. Volatility metrics
2. Drawdown potential
3. Correlation risks
4. Black swan scenarios
Provide specific risk scores and hedging recommendations."""
        
        prompt = f"""Portfolio Risk Assessment:

Portfolio:
{json.dumps(portfolio, indent=2)}

Market Conditions:
{json.dumps(market_conditions, indent=2)}

Calculate:
1. Overall risk score (1-10)
2. Value at Risk (VaR) 95%
3. Maximum expected drawdown
4. Recommended hedging strategies"""
        
        return self.llm.generate(prompt, system=system, temperature=0.2)
    
    def natural_language_query(self, query: str, portfolio_context: Dict) -> Dict[str, Any]:
        """Natural language interface to portfolio data"""
        system = """You are a helpful financial assistant. Answer questions about the user's portfolio.
Use the provided context. If you don't know, say so."""
        
        prompt = f"""Context:
{json.dumps(portfolio_context, indent=2)}

User Question: {query}

Answer concisely and accurately."""
        
        return self.llm.generate(prompt, system=system, temperature=0.5)


# ============================================================================
# SETUP AND INSTALLATION HELPERS
# ============================================================================

def setup_ollama():
    """Print setup instructions for Ollama"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                    OLLAMA SETUP INSTRUCTIONS                      ║
╠══════════════════════════════════════════════════════════════════╣
║ 1. INSTALL OLLAMA                                                ║
║    Windows: Download from https://ollama.com/download            ║
║    macOS:   brew install ollama                                  ║
║    Linux:   curl -fsSL https://ollama.com/install.sh | sh       ║
║                                                                  ║
║ 2. PULL FINANCIAL MODELS (run these in terminal)                 ║
║    ollama pull llama3.2:3b     # Fast, good summaries          ║
║    ollama pull llama3.1:8b     # Better reasoning               ║
║    ollama pull qwen2.5:7b      # Great for structured data       ║
║    ollama pull phi4            # Microsoft, good math           ║
║                                                                  ║
║ 3. START OLLAMA SERVER                                           ║
║    ollama serve                                                  ║
║    (Or let it auto-start on Windows/Mac)                         ║
║                                                                  ║
║ 4. VERIFY INSTALLATION                                           ║
║    ollama list                                                   ║
║    ollama run llama3.2:3b                                        ║
║                                                                  ║
║  COST: £0 (completely free, runs locally)                       ║
╚══════════════════════════════════════════════════════════════════╝
    """)


def print_model_comparison():
    """Print comparison of free vs paid models"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                 LLM OPTIONS COMPARISON                            ║
╠══════════════════════════════════════════════════════════════════╣
║ FREE TIER (Local)                    PAID TIER (API)              ║
╠════════════════════════════════════╦═════════════════════════════╣
║ Ollama (Local)                     ║ OpenAI GPT-4o-mini         ║
║ - llama3.2:3b (3B params)          ║ - $0.15/1M input tokens    ║
║ - llama3.1:8b (8B params)          ║ - $0.60/1M output tokens   ║
║ - qwen2.5:7b (7B params)           ║ - Very high quality        ║
║ - phi4 (Microsoft)                 ║                            ║
║                                    ║ Anthropic Claude Haiku     ║
║ COST: £0                           ║ - Fast, good reasoning     ║
║ SPEED: Fast (local GPU/CPU)        ║ - ~$0.25/1K tokens         ║
║ PRIVACY: 100% (local)              ║                            ║
║ INTERNET: Not needed               ║                            ║
╠════════════════════════════════════╩═════════════════════════════╣
║ RECOMMENDATION: Start with Ollama (free), upgrade if needed       ║
╚══════════════════════════════════════════════════════════════════╝
    """)


# ============================================================================
# MAIN / TEST
# ============================================================================

if __name__ == "__main__":
    setup_ollama()
    print_model_comparison()
    
    # Test initialization
    print("\n🔧 Testing LLM Manager initialization...")
    config = LLMConfig(
        primary_provider="ollama",
        fallback_to_paid=False,
        use_cache=True
    )
    
    llm = LLMManager(config)
    status = llm.get_status()
    
    print("\n📊 Status:")
    print(json.dumps(status, indent=2))
    
    # Test generation if Ollama available
    if llm.ollama.available:
        print("\n🧪 Testing Ollama generation...")
        result = llm.generate(
            "What is the 4% rule in retirement planning?",
            max_tokens=200
        )
        if result["success"]:
            print(f"✓ Response: {result['text'][:200]}...")
            print(f"  Model: {result.get('model')}")
            print(f"  Cost: £{result.get('cost_usd', 0):.4f}")
        else:
            print(f"✗ Error: {result.get('error')}")
    else:
        print("\n⚠ Ollama not available. Install and run 'ollama serve' to test.")
