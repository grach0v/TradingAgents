# TradingAgents/graph/signal_processing.py

from langchain_openai import ChatOpenAI


class SignalProcessor:
    """Processes trading signals to extract actionable decisions."""

    def __init__(self, quick_thinking_llm: ChatOpenAI):
        """Initialize with an LLM for processing."""
        self.quick_thinking_llm = quick_thinking_llm

    def process_signal(self, full_signal: str) -> str:
        """
        Process a full trading signal to extract the core decision with quantities.

        Args:
            full_signal: Complete trading signal text

        Returns:
            Extracted decision (e.g., "BUY 0.05 BTC", "SELL 10 NVDA", "HOLD")
        """
        messages = [
            (
                "system",
                """You are an efficient assistant designed to analyze trading decisions from financial reports. Your task is to extract the investment decision with exact quantities when specified.

Extract the decision in one of these formats:
- "BUY X.XXX SYMBOL" (for purchases with specific amounts)
- "SELL X.XXX SYMBOL" (for sales with specific amounts)  
- "HOLD" (for maintaining current position)

Examples:
- "BUY 0.05 BTC"
- "SELL 10 NVDA"
- "BUY 25 TSLA"
- "HOLD"

If no specific quantity is mentioned, extract just the action (BUY, SELL, or HOLD). Provide only the extracted decision as your output, without adding any additional text or information.""",
            ),
            ("human", full_signal),
        ]

        return self.quick_thinking_llm.invoke(messages).content
