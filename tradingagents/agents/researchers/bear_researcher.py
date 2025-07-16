from langchain_core.messages import AIMessage
import time
import json


def create_bear_researcher(llm, memory):
    def bear_node(state) -> dict:
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        bear_history = investment_debate_state.get("bear_history", "")

        current_response = investment_debate_state.get("current_response", "")
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]
        company_name = state["company_of_interest"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        # Check if we're analyzing crypto and adjust the prompt accordingly
        is_crypto = company_name.endswith('-USD') or company_name.endswith('-USDT') or company_name in ['BTC', 'ETH', 'ADA', 'SOL', 'AVAX', 'DOT', 'MATIC', 'LINK', 'UNI', 'AAVE']
        
        if is_crypto:
            prompt = f"""You are a Crypto Bear Analyst making the case against investing in this cryptocurrency. Your goal is to present a well-reasoned argument emphasizing risks, challenges, and negative indicators specific to crypto markets.

Key points to focus on for crypto analysis:
- Market Risks: Extreme volatility, regulatory uncertainty, market manipulation, liquidity issues
- Technology Risks: Security vulnerabilities, scalability limitations, competition from newer protocols
- Regulatory Challenges: Government crackdowns, compliance costs, potential bans, tax implications
- Adoption Barriers: User experience issues, energy consumption concerns, institutional hesitancy
- Competitive Threats: Better alternatives, network effects erosion, technological obsolescence
- Macro Factors: Interest rate impacts, economic downturns, risk-off sentiment affecting crypto
- Crypto-Specific Risks: Exchange risks, wallet security, smart contract vulnerabilities, DeFi risks

Resources available:
Market research report: {market_research_report}
Social media sentiment report: {sentiment_report}
Latest crypto and blockchain news: {news_report}
Cryptocurrency fundamentals report: {fundamentals_report}
Conversation history of the debate: {history}
Last bull argument: {current_response}
Reflections from similar crypto situations and lessons learned: {past_memory_str}

Use this information to deliver a compelling bear argument against the cryptocurrency, refute the bull's claims, and engage in a dynamic debate that demonstrates the risks and weaknesses of investing in crypto.
"""
        else:
            prompt = f"""You are a Bear Analyst making the case against investing in the stock. Your goal is to present a well-reasoned argument emphasizing risks, challenges, and negative indicators. Leverage the provided research and data to highlight potential downsides and counter bullish arguments effectively.

Key points to focus on:

- Risks and Challenges: Highlight factors like market saturation, financial instability, or macroeconomic threats that could hinder the stock's performance.
- Competitive Weaknesses: Emphasize vulnerabilities such as weaker market positioning, declining innovation, or threats from competitors.
- Negative Indicators: Use evidence from financial data, market trends, or recent adverse news to support your position.
- Bull Counterpoints: Critically analyze the bull argument with specific data and sound reasoning, exposing weaknesses or over-optimistic assumptions.
- Engagement: Present your argument in a conversational style, directly engaging with the bull analyst's points and debating effectively rather than simply listing facts.

Resources available:

Market research report: {market_research_report}
Social media sentiment report: {sentiment_report}
Latest world affairs news: {news_report}
Company fundamentals report: {fundamentals_report}
Conversation history of the debate: {history}
Last bull argument: {current_response}
Reflections from similar situations and lessons learned: {past_memory_str}
Use this information to deliver a compelling bear argument, refute the bull's claims, and engage in a dynamic debate that demonstrates the risks and weaknesses of investing in the stock. You must also address reflections and learn from lessons and mistakes you made in the past.
"""

        response = llm.invoke(prompt)

        argument = f"Bear Analyst: {response.content}"

        new_investment_debate_state = {
            "history": history + "\n" + argument,
            "bear_history": bear_history + "\n" + argument,
            "bull_history": investment_debate_state.get("bull_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
        }

        return {"investment_debate_state": new_investment_debate_state}

    return bear_node
