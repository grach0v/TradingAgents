#!/usr/bin/env python3
"""
Example script showing the new wallet-based trading functionality.
"""

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.agents.utils.wallet import TradingWallet
from tradingagents.agents.utils.trade_executor import TradeExecutor

def main():
    print("🚀 TradingAgents Wallet Integration Demo")
    print("=" * 60)
    
    # Create a custom config
    config = DEFAULT_CONFIG.copy()
    config["llm_provider"] = "google"
    config["deep_think_llm"] = "gemini-2.0-flash"
    config["quick_think_llm"] = "gemini-2.0-flash"
    config["max_debate_rounds"] = 1
    config["online_tools"] = True
    
    # Initialize the trading system
    ta = TradingAgentsGraph(debug=False, config=config)
    
    # Show initial wallet state
    print("\n💰 Initial Wallet State:")
    print("-" * 40)
    wallet = TradingWallet()
    print(wallet.get_portfolio_summary())
    
    # Run analysis for different assets
    test_assets = ["BTC-USD", "NVDA", "ETH-USD"]
    
    for asset in test_assets:
        print(f"\n🔍 Analyzing {asset}...")
        print("-" * 40)
        
        try:
            # Run the analysis
            final_state, result = ta.propagate(asset, "2024-05-10")
            
            # Display results
            print(f"📊 Decision: {result['decision']}")
            print(f"💫 Trade Status: {'✅ Executed' if result['trade_executed'] else '❌ Failed'}")
            print(f"📝 Message: {result['trade_message']}")
            
            # Show updated wallet
            print("\n💰 Updated Wallet:")
            print(result['wallet_summary'])
            
        except Exception as e:
            print(f"❌ Error analyzing {asset}: {str(e)}")
    
    print("\n🎯 Demo Complete!")
    print("=" * 60)
    
    # Show wallet management commands
    print("\n📋 Wallet Management Commands:")
    print("  python wallet_manager.py status           - Check wallet status")
    print("  python wallet_manager.py reset            - Reset wallet")
    print("  python wallet_manager.py add-cash 10000   - Add cash")
    print("  python wallet_manager.py simulate 'BUY 0.1 BTC'  - Simulate trade")

if __name__ == "__main__":
    main()
