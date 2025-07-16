import time
import json


def create_risk_manager(llm, memory):
    def risk_manager_node(state) -> dict:

        company_name = state["company_of_interest"]

        history = state["risk_debate_state"]["history"]
        risk_debate_state = state["risk_debate_state"]
        market_research_report = state["market_report"]
        news_report = state["news_report"]
        fundamentals_report = state["news_report"]
        sentiment_report = state["sentiment_report"]
        trader_plan = state["investment_plan"]
        
        # Get wallet information
        wallet = state["wallet"]
        wallet_context = wallet.get_wallet_context_for_agent(company_name)

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        # Check if we're analyzing crypto and adjust the prompt accordingly
        is_crypto = company_name.endswith('-USD') or company_name.endswith('-USDT') or company_name in ['BTC', 'ETH', 'ADA', 'SOL', 'AVAX', 'DOT', 'MATIC', 'LINK', 'UNI', 'AAVE']
        
        if is_crypto:
            decision_format = f"""
🎯 **REQUIRED DECISION FORMAT:**
Your final decision must specify EXACT QUANTITIES for cryptocurrency trading:
- For BUY: "BUY X.XXXXX {company_name.replace('-USD', '')}" (specify exact amount)
- For SELL: "SELL X.XXXXX {company_name.replace('-USD', '')}" (specify exact amount)
- For HOLD: "HOLD" (maintain current position)

Examples:
- "BUY 0.05 BTC"
- "SELL 0.25 ETH" 
- "BUY 15 SOL"
- "HOLD"

Consider crypto-specific factors:
- High volatility and 24/7 markets
- Position sizing for extreme price swings
- Risk management in unregulated markets
- Portfolio allocation limits for crypto assets
"""
        else:
            decision_format = f"""
🎯 **REQUIRED DECISION FORMAT:**
Your final decision must specify EXACT QUANTITIES for stock trading:
- For BUY: "BUY X {company_name}" (specify exact number of shares)
- For SELL: "SELL X {company_name}" (specify exact number of shares)
- For HOLD: "HOLD" (maintain current position)

Examples:
- "BUY 10 NVDA"
- "SELL 5 AAPL"
- "BUY 25 TSLA"
- "HOLD"

Consider stock-specific factors:
- Position sizing based on account balance
- Risk management and diversification
- Market hours and liquidity considerations
"""

        prompt = f"""As the Risk Management Judge and Debate Facilitator, your goal is to evaluate the debate between three risk analysts—Risky, Neutral, and Safe/Conservative—and determine the best course of action for the trader. Your decision must result in a clear recommendation with EXACT QUANTITIES: Buy (with specific amount), Sell (with specific amount), or Hold. 

{wallet_context}

{decision_format}

Guidelines for Decision-Making:
1. **Analyze Portfolio Context**: Consider current holdings and available cash
2. **Evaluate Risk vs. Reward**: Balance potential gains against portfolio risk
3. **Determine Position Size**: Calculate appropriate quantity based on portfolio allocation
4. **Summarize Key Arguments**: Extract the strongest points from each analyst
5. **Provide Rationale**: Support your recommendation with specific reasoning
6. **Refine the Trader's Plan**: Start with the trader's original plan, **{trader_plan}**, and adjust quantities based on the analysts' insights and wallet constraints

**Learn from Past Mistakes**: Use lessons from **{past_memory_str}** to address prior misjudgments and improve the decision you are making now to make sure you don't make a wrong trading call that loses money.

Deliverables:
- A clear and actionable recommendation with exact quantities
- Detailed reasoning anchored in the debate and portfolio analysis
- Risk assessment and position sizing justification

---

**Analysts Debate History:**  
{history}

---

Focus on actionable insights with specific quantities, continuous improvement, and portfolio-appropriate position sizing. Build on past lessons, critically evaluate all perspectives, and ensure each decision advances better outcomes while managing risk appropriately."""

        response = llm.invoke(prompt)

        new_risk_debate_state = {
            "judge_decision": response.content,
            "history": risk_debate_state["history"],
            "risky_history": risk_debate_state["risky_history"],
            "safe_history": risk_debate_state["safe_history"],
            "neutral_history": risk_debate_state["neutral_history"],
            "latest_speaker": "Judge",
            "current_risky_response": risk_debate_state["current_risky_response"],
            "current_safe_response": risk_debate_state["current_safe_response"],
            "current_neutral_response": risk_debate_state["current_neutral_response"],
            "count": risk_debate_state["count"],
        }

        return {
            "risk_debate_state": new_risk_debate_state,
            "final_trade_decision": response.content,
        }

    return risk_manager_node
