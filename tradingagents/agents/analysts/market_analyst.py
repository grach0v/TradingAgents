from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from ..utils.crypto_utils import get_crypto_aware_system_message, get_crypto_aware_analyst_message


def create_market_analyst(llm, toolkit):

    def market_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        if toolkit.config["online_tools"]:
            tools = [
                toolkit.get_YFin_data_online,
                toolkit.get_stockstats_indicators_report_online,
            ]
        else:
            tools = [
                toolkit.get_YFin_data,
                toolkit.get_stockstats_indicators_report,
            ]

        # Check if we're analyzing crypto and adjust the system message accordingly
        crypto_specific_message = get_crypto_aware_analyst_message(ticker, "market")
        
        if crypto_specific_message:
            # Use crypto-specific message
            system_message = crypto_specific_message + """
Your role is to select the **most relevant indicators** for cryptocurrency trading from the following list. Choose up to **8 indicators** that work well in 24/7 volatile crypto markets:

Moving Averages (Important for crypto trend identification):
- close_50_sma: 50 SMA: Medium-term trend for crypto markets. Usage: Key support/resistance in volatile crypto moves.
- close_200_sma: 200 SMA: Long-term crypto trend benchmark. Usage: Bull/bear market identification.
- close_10_ema: 10 EMA: Responsive to quick crypto price movements. Usage: Entry/exit signals in fast moves.

MACD (Essential for crypto momentum):
- macd: MACD: Momentum changes in volatile crypto markets. Usage: Trend change signals.
- macds: MACD Signal: Crossover signals for crypto trades. Usage: Entry/exit timing.
- macdh: MACD Histogram: Momentum strength in crypto. Usage: Divergence spotting.

Momentum Indicators (Critical for crypto):
- rsi: RSI: Overbought/oversold in crypto (often extreme). Usage: Reversal signals with caution.

Volatility Indicators (Crucial for crypto):
- boll: Bollinger Middle: Dynamic crypto price benchmark. Usage: Trend baseline.
- boll_ub: Upper Bollinger: Crypto breakout signals. Usage: Resistance levels.
- boll_lb: Lower Bollinger: Crypto support levels. Usage: Oversold conditions.
- atr: ATR: Crypto volatility measurement. Usage: Position sizing and stop-loss.

Volume Indicators (Key for crypto validation):
- vwma: Volume weighted average for crypto liquidity. Usage: Trend confirmation.

Focus on crypto-specific patterns, 24/7 market dynamics, and high-volatility considerations. Call get_YFin_data first, then analyze indicators. Provide detailed crypto market analysis."""
        else:
            # Use original stock-focused message
            system_message = (
                """You are a trading assistant tasked with analyzing financial markets. Your role is to select the **most relevant indicators** for a given market condition or trading strategy from the following list. The goal is to choose up to **8 indicators** that provide complementary insights without redundancy. Categories and each category's indicators are:

Moving Averages:
- close_50_sma: 50 SMA: A medium-term trend indicator. Usage: Identify trend direction and serve as dynamic support/resistance. Tips: It lags price; combine with faster indicators for timely signals.
- close_200_sma: 200 SMA: A long-term trend benchmark. Usage: Confirm overall market trend and identify golden/death cross setups. Tips: It reacts slowly; best for strategic trend confirmation rather than frequent trading entries.
- close_10_ema: 10 EMA: A responsive short-term average. Usage: Capture quick shifts in momentum and potential entry points. Tips: Prone to noise in choppy markets; use alongside longer averages for filtering false signals.

MACD Related:
- macd: MACD: Computes momentum via differences of EMAs. Usage: Look for crossovers and divergence as signals of trend changes. Tips: Confirm with other indicators in low-volatility or sideways markets.
- macds: MACD Signal: An EMA smoothing of the MACD line. Usage: Use crossovers with the MACD line to trigger trades. Tips: Should be part of a broader strategy to avoid false positives.
- macdh: MACD Histogram: Shows the gap between the MACD line and its signal. Usage: Visualize momentum strength and spot divergence early. Tips: Can be volatile; complement with additional filters in fast-moving markets.

Momentum Indicators:
- rsi: RSI: Measures momentum to flag overbought/oversold conditions. Usage: Apply 70/30 thresholds and watch for divergence to signal reversals. Tips: In strong trends, RSI may remain extreme; always cross-check with trend analysis.

Volatility Indicators:
- boll: Bollinger Middle: A 20 SMA serving as the basis for Bollinger Bands. Usage: Acts as a dynamic benchmark for price movement. Tips: Combine with the upper and lower bands to effectively spot breakouts or reversals.
- boll_ub: Bollinger Upper Band: Typically 2 standard deviations above the middle line. Usage: Signals potential overbought conditions and breakout zones. Tips: Confirm signals with other tools; prices may ride the band in strong trends.
- boll_lb: Bollinger Lower Band: Typically 2 standard deviations below the middle line. Usage: Indicates potential oversold conditions. Tips: Use additional analysis to avoid false reversal signals.
- atr: ATR: Averages true range to measure volatility. Usage: Set stop-loss levels and adjust position sizes based on current market volatility. Tips: It's a reactive measure, so use it as part of a broader risk management strategy.

Volume-Based Indicators:
- vwma: VWMA: A moving average weighted by volume. Usage: Confirm trends by integrating price action with volume data. Tips: Watch for skewed results from volume spikes; use in combination with other volume analyses.

- Select indicators that provide diverse and complementary information. Avoid redundancy (e.g., do not select both rsi and stochrsi). Also briefly explain why they are suitable for the given market context. When you tool call, please use the exact name of the indicators provided above as they are defined parameters, otherwise your call will fail. Please make sure to call get_YFin_data first to retrieve the CSV that is needed to generate indicators. Write a very detailed and nuanced report of the trends you observe. Do not simply state the trends are mixed, provide detailed and finegrained analysis and insights that may help traders make decisions."""
            )
        
        system_message += """ Make sure to append a Markdown table at the end of the report to organize key points in the report, organized and easy to read."""

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant, collaborating with other assistants."
                    " Use the provided tools to progress towards answering the question."
                    " If you are unable to fully answer, that's OK; another assistant with different tools"
                    " will help where you left off. Execute what you can to make progress."
                    " If you or any other assistant has the FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** or deliverable,"
                    " prefix your response with FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** so the team knows to stop."
                    " You have access to the following tools: {tool_names}.\n{system_message}"
                    "For your reference, the current date is {current_date}. The company we want to look at is {ticker}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

        chain = prompt | llm.bind_tools(tools)

        result = chain.invoke(state["messages"])

        report = ""

        if len(result.tool_calls) == 0:
            report = result.content
       
        return {
            "messages": [result],
            "market_report": report,
        }

    return market_analyst_node
