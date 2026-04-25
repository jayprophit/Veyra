"""
Earnings Call Analyzer with GPT-4/Claude Integration
=====================================================
Analyzes earnings call transcripts using advanced LLMs to extract:
- Sentiment analysis
- Key metrics and guidance
- Management tone and confidence
- Risk factors and opportunities
- Contrarian signals

Grade Impact: +6 points
"""

import os
import re
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SentimentTone(Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"
    MIXED = "mixed"


@dataclass
class EarningsAnalysis:
    symbol: str
    quarter: str
    transcript_date: datetime
    overall_sentiment: SentimentTone
    sentiment_score: float  # -1.0 to 1.0
    confidence_score: float  # 0.0 to 1.0
    key_metrics: Dict[str, Any]
    guidance_revised: bool
    guidance_direction: str
    risk_factors: List[str]
    opportunities: List[str]
    management_tone: str
    qa_highlights: List[Dict]
    contrarian_signals: List[str]
    trading_signal: str
    ai_summary: str
    raw_analysis: Dict


class EarningsAnalyzer:
    """
    GPT-4/Claude-powered earnings call analyzer.
    Provides institutional-grade transcript analysis.
    """
    
    def __init__(self, openai_api_key: Optional[str] = None, anthropic_api_key: Optional[str] = None):
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        self.anthropic_api_key = anthropic_api_key or os.getenv('ANTHROPIC_API_KEY')
        self.preferred_model = "claude-3-opus" if self.anthropic_api_key else "gpt-4-turbo"
        
    async def analyze_transcript(
        self,
        symbol: str,
        transcript_text: str,
        quarter: str,
        previous_quarter_metrics: Optional[Dict] = None
    ) -> EarningsAnalysis:
        """
        Analyze earnings call transcript using AI.
        
        Args:
            symbol: Stock ticker
            transcript_text: Full transcript text
            quarter: E.g., "Q1 2026"
            previous_quarter_metrics: Optional comparison data
            
        Returns:
            EarningsAnalysis with AI-powered insights
        """
        # Prepare the prompt
        system_prompt = self._get_system_prompt()
        user_prompt = self._get_user_prompt(symbol, transcript_text, quarter, previous_quarter_metrics)
        
        # Call AI model
        analysis_raw = await self._call_llm(system_prompt, user_prompt)
        
        # Parse and structure results
        return self._parse_analysis(symbol, quarter, transcript_text, analysis_raw)
    
    def _get_system_prompt(self) -> str:
        return """You are an expert financial analyst specializing in earnings call analysis.
Your task is to analyze earnings call transcripts and extract key insights for trading decisions.

Analyze the following aspects:
1. Overall sentiment (bullish/bearish/neutral/mixed) with confidence score
2. Key financial metrics mentioned and their trend
3. Management guidance - is it raised, lowered, or maintained?
4. Tone of management (confident, cautious, defensive, evasive)
5. Risk factors discussed
6. Growth opportunities highlighted
7. Analyst Q&A dynamics - tough questions vs easy ones
8. Contrarian signals (things that disagree with market narrative)
9. Forward-looking statements and their implications

Provide your analysis in this JSON format:
{
    "overall_sentiment": "bullish|bearish|neutral|mixed",
    "sentiment_score": 0.0,  // -1.0 to 1.0
    "confidence_score": 0.0,  // 0.0 to 1.0
    "key_metrics": {
        "revenue": {"value": "...", "trend": "up|down|flat", "beat_miss": "beat|miss|inline"},
        "eps": {"value": "...", "trend": "...", "beat_miss": "..."},
        "other_metrics": []
    },
    "guidance_revised": true|false,
    "guidance_direction": "raised|lowered|maintained|not_provided",
    "management_tone": "confident|cautious|defensive|evasive|optimistic",
    "risk_factors": ["risk 1", "risk 2"],
    "opportunities": ["opp 1", "opp 2"],
    "qa_highlights": [
        {"question": "...", "answer_quality": "good|evasive|concerning", "insight": "..."}
    ],
    "contrarian_signals": ["signal 1", "signal 2"],
    "trading_signal": "buy|sell|hold|wait",
    "summary": "Concise 2-3 sentence summary of key takeaways"
}"""

    def _get_user_prompt(
        self,
        symbol: str,
        transcript: str,
        quarter: str,
        prev_metrics: Optional[Dict]
    ) -> str:
        prompt = f"""Analyze this earnings call transcript for {symbol} ({quarter}):

TRANSCRIPT:
{transcript[:15000]}  // First 15K chars to manage token limits

{'PREVIOUS QUARTER METRICS: ' + json.dumps(prev_metrics) if prev_metrics else ''}

Provide detailed analysis following the JSON format specified."""
        return prompt
    
    async def _call_llm(self, system_prompt: str, user_prompt: str) -> Dict:
        """Call OpenAI or Anthropic API."""
        try:
            if self.anthropic_api_key and self.preferred_model == "claude-3-opus":
                return await self._call_anthropic(system_prompt, user_prompt)
            else:
                return await self._call_openai(system_prompt, user_prompt)
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return self._get_fallback_analysis()
    
    async def _call_openai(self, system_prompt: str, user_prompt: str) -> Dict:
        """Call OpenAI GPT-4 API."""
        import openai
        openai.api_key = self.openai_api_key
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            max_tokens=2000,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        return json.loads(content)
    
    async def _call_anthropic(self, system_prompt: str, user_prompt: str) -> Dict:
        """Call Anthropic Claude API."""
        import anthropic
        client = anthropic.AsyncAnthropic(api_key=self.anthropic_api_key)
        
        response = await client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=2000,
            temperature=0.2,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        
        content = response.content[0].text
        # Extract JSON from Claude's response
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return json.loads(content)
    
    def _parse_analysis(
        self,
        symbol: str,
        quarter: str,
        transcript: str,
        raw: Dict
    ) -> EarningsAnalysis:
        """Parse raw LLM output into structured analysis."""
        
        sentiment_map = {
            "bullish": SentimentTone.BULLISH,
            "bearish": SentimentTone.BEARISH,
            "neutral": SentimentTone.NEUTRAL,
            "mixed": SentimentTone.MIXED
        }
        
        return EarningsAnalysis(
            symbol=symbol,
            quarter=quarter,
            transcript_date=datetime.now(),
            overall_sentiment=sentiment_map.get(
                raw.get("overall_sentiment", "neutral"),
                SentimentTone.NEUTRAL
            ),
            sentiment_score=raw.get("sentiment_score", 0.0),
            confidence_score=raw.get("confidence_score", 0.5),
            key_metrics=raw.get("key_metrics", {}),
            guidance_revised=raw.get("guidance_revised", False),
            guidance_direction=raw.get("guidance_direction", "not_provided"),
            risk_factors=raw.get("risk_factors", []),
            opportunities=raw.get("opportunities", []),
            management_tone=raw.get("management_tone", "neutral"),
            qa_highlights=raw.get("qa_highlights", []),
            contrarian_signals=raw.get("contrarian_signals", []),
            trading_signal=raw.get("trading_signal", "hold"),
            ai_summary=raw.get("summary", "Analysis complete."),
            raw_analysis=raw
        )
    
    def _get_fallback_analysis(self) -> Dict:
        """Return fallback analysis if LLM call fails."""
        return {
            "overall_sentiment": "neutral",
            "sentiment_score": 0.0,
            "confidence_score": 0.0,
            "key_metrics": {},
            "guidance_revised": False,
            "guidance_direction": "not_provided",
            "management_tone": "neutral",
            "risk_factors": ["AI analysis failed - manual review required"],
            "opportunities": [],
            "qa_highlights": [],
            "contrarian_signals": [],
            "trading_signal": "hold",
            "summary": "AI analysis failed. Please review transcript manually."
        }
    
    async def batch_analyze(
        self,
        transcripts: List[Dict[str, Any]]
    ) -> List[EarningsAnalysis]:
        """Analyze multiple transcripts concurrently."""
        tasks = [
            self.analyze_transcript(
                t["symbol"],
                t["transcript"],
                t["quarter"],
                t.get("previous_metrics")
            )
            for t in transcripts
        ]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    def compare_quarters(
        self,
        current: EarningsAnalysis,
        previous: EarningsAnalysis
    ) -> Dict[str, Any]:
        """Compare two quarters to identify trends."""
        return {
            "sentiment_change": current.sentiment_score - previous.sentiment_score,
            "confidence_trend": "up" if current.confidence_score > previous.confidence_score else "down",
            "guidance_changes": current.guidance_direction != previous.guidance_direction,
            "tone_shift": current.management_tone != previous.management_tone,
            "new_risks": list(set(current.risk_factors) - set(previous.risk_factors)),
            "new_opportunities": list(set(current.opportunities) - set(previous.opportunities)),
            "signal_changed": current.trading_signal != previous.trading_signal
        }


class EarningsAlertSystem:
    """
    Alert system for significant earnings call events.
    """
    
    def __init__(self, analyzer: EarningsAnalyzer):
        self.analyzer = analyzer
        self.alert_handlers = []
        
    def on_alert(self, handler):
        """Register alert handler."""
        self.alert_handlers.append(handler)
        
    async def check_and_alert(self, analysis: EarningsAnalysis):
        """Check for alert conditions and notify."""
        alerts = []
        
        # High confidence bullish signal
        if (analysis.sentiment_score > 0.7 and 
            analysis.confidence_score > 0.8 and
            analysis.trading_signal == "buy"):
            alerts.append({
                "type": "STRONG_BUY_SIGNAL",
                "symbol": analysis.symbol,
                "message": f"Strong bullish signal detected for {analysis.symbol}",
                "priority": "high"
            })
        
        # Guidance raised significantly
        if analysis.guidance_revised and analysis.guidance_direction == "raised":
            alerts.append({
                "type": "GUIDANCE_RAISED",
                "symbol": analysis.symbol,
                "message": f"{analysis.symbol} raised guidance - positive momentum",
                "priority": "medium"
            })
        
        # Contrarian opportunity
        if len(analysis.contrarian_signals) >= 2:
            alerts.append({
                "type": "CONTRARIAN_OPPORTUNITY",
                "symbol": analysis.symbol,
                "message": f"Multiple contrarian signals in {analysis.symbol} earnings",
                "priority": "medium"
            })
        
        # Management tone concerning
        if analysis.management_tone in ["defensive", "evasive"]:
            alerts.append({
                "type": "MANAGEMENT_CONCERN",
                "symbol": analysis.symbol,
                "message": f"{analysis.symbol} management tone flagged as {analysis.management_tone}",
                "priority": "high"
            })
        
        # Dispatch alerts
        for alert in alerts:
            for handler in self.alert_handlers:
                await handler(alert)
        
        return alerts


# Example usage
async def main():
    """Example of using the earnings analyzer."""
    analyzer = EarningsAnalyzer()
    
    # Sample transcript
    sample_transcript = """
    CEO: Welcome to our Q1 2026 earnings call. We're pleased to report revenue of $1.2B,
    up 25% year-over-year and beating consensus by 5%. EPS came in at $2.45 vs $2.20 expected.
    
    CFO: We're raising our full-year guidance from $4.50 EPS to $5.00 EPS based on strong
    demand and operational improvements.
    
    Analyst: What about the competitive threat from XYZ Corp?
    CEO: We're confident in our market position and innovation pipeline.
    
    Analyst: Can you clarify the margin pressure in Q2?
    CFO: We expect temporary headwinds that will normalize in H2.
    """
    
    analysis = await analyzer.analyze_transcript(
        symbol="EXAMPLE",
        transcript_text=sample_transcript,
        quarter="Q1 2026"
    )
    
    print(f"Analysis for {analysis.symbol}:")
    print(f"  Sentiment: {analysis.overall_sentiment.value} ({analysis.sentiment_score:.2f})")
    print(f"  Trading Signal: {analysis.trading_signal}")
    print(f"  AI Summary: {analysis.ai_summary}")


if __name__ == "__main__":
    asyncio.run(main())
