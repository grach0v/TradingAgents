from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# Create a custom config
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "google"  # Use a different model
config["backend_url"] = "https://generativelanguage.googleapis.com/v1"  # Use a different backend
config["deep_think_llm"] = "gemini-2.0-flash"  # Use a different model
config["quick_think_llm"] = "gemini-2.0-flash"  # Use a different model
config["max_debate_rounds"] = 1  # Increase debate rounds
config["online_tools"] = True  # Increase debate rounds

# Initialize with custom config
ta = TradingAgentsGraph(debug=True, config=config)

# Forward propagate with new wallet-based trading
print("🚀 Starting Trading Analysis with Wallet Integration...\n")

final_state, result = ta.propagate("NVDA", "2024-05-10")

print("\n" + "="*60)
print("📊 TRADING RESULTS")
print("="*60)
print(f"Decision: {result['decision']}")
print(f"Trade Status: {'✅ Executed' if result['trade_executed'] else '❌ Failed'}")
print(f"Message: {result['trade_message']}")
print("\n" + result['wallet_summary'])
print("\n" + "="*60)
print("📈 FULL ANALYSIS")
print("="*60)
print(result['full_analysis'])

# Memorize mistakes and reflect
# ta.reflect_and_remember(1000) # parameter is the position returns
