import functools
import time
import json


from ..utils.crypto_utils import get_crypto_aware_system_message


def create_trader(llm, memory):
    def trader_node(state, name):
        company_name = state["company_of_interest"]
        investment_plan = state["investment_plan"]
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        if past_memories:
            for i, rec in enumerate(past_memories, 1):
                past_memory_str += rec["recommendation"] + "\n\n"
        else:
            past_memory_str = "No past memories found."

        context = {
            "role": "user",
            "content": f"Based on a comprehensive analysis by a team of analysts, here is an investment plan tailored for {company_name}. This plan incorporates insights from current technical market trends, macroeconomic indicators, and social media sentiment. Use this plan as a foundation for evaluating your next trading decision.\n\nProposed Investment Plan: {investment_plan}\n\nLeverage these insights to make an informed and strategic decision.",
        }

        # Check if we're analyzing crypto and adjust the system message accordingly
        is_crypto = company_name.endswith('-USD') or company_name.endswith('-USDT') or company_name in ['BTC', 'ETH', 'ADA', 'SOL', 'AVAX', 'DOT', 'MATIC', 'LINK', 'UNI', 'AAVE']
        
        if is_crypto:
            system_content = f"""You are a cryptocurrency trading agent analyzing market data to make investment decisions. Based on your analysis, provide a specific recommendation to buy, sell, or hold. 

Consider crypto-specific factors like:
- 24/7 market dynamics and volatility patterns
- Regulatory risks and compliance considerations
- On-chain metrics and network health
- Community sentiment and social media influence
- DeFi/NFT ecosystem integration
- Institutional adoption trends
- Technical analysis in high-volatility environment
- Risk management for crypto's extreme price swings

End with a firm decision and always conclude your response with 'FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL**' to confirm your cryptocurrency trading recommendation. Learn from past crypto trading experiences: {past_memory_str}"""
        else:
            system_content = f"""You are a trading agent analyzing market data to make investment decisions. Based on your analysis, provide a specific recommendation to buy, sell, or hold. End with a firm decision and always conclude your response with 'FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL**' to confirm your recommendation. Do not forget to utilize lessons from past decisions to learn from your mistakes. Here is some reflections from similar situations you traded in and the lessons learned: {past_memory_str}"""

        messages = [
            {
                "role": "system",
                "content": system_content,
            },
            context,
        ]

        result = llm.invoke(messages)

        return {
            "messages": [result],
            "trader_investment_plan": result.content,
            "sender": name,
        }

    return functools.partial(trader_node, name="Trader")
