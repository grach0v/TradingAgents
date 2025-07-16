#!/usr/bin/env python3
"""
Simple test to verify the wallet-based trading system works.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from tradingagents.agents.utils.wallet import TradingWallet
from tradingagents.agents.utils.trade_executor import TradeExecutor

def test_wallet_system():
    """Test the wallet and trade execution system."""
    
    print("🧪 Testing Wallet System")
    print("=" * 50)
    
    # Create a wallet
    wallet = TradingWallet()
    
    # Show initial state
    print("💰 Initial Wallet:")
    print(wallet.get_portfolio_summary())
    
    # Test trade executor
    executor = TradeExecutor(wallet)
    
    # Test some trades
    test_trades = [
        "BUY 0.01 BTC",
        "BUY 2 NVDA", 
        "SELL 0.5 ETH",
        "HOLD",
        "BUY 5 SOL"
    ]
    
    print("\n🎯 Testing Trade Execution:")
    print("-" * 40)
    
    for trade in test_trades:
        print(f"\n📊 Trade: {trade}")
        
        # Simulate first
        summary = executor.get_trade_summary(trade, "2024-05-10")
        print(f"Simulation: {summary}")
        
        # Execute if valid
        if "✅" in summary:
            success, message = executor.execute_trade(trade, "2024-05-10")
            if success:
                print(f"✅ Executed: {message}")
            else:
                print(f"❌ Failed: {message}")
        else:
            print("⏭️  Skipping execution")
    
    # Final wallet state
    print("\n💰 Final Wallet:")
    print(wallet.get_portfolio_summary())
    
    print("\n✅ Wallet system test completed!")

if __name__ == "__main__":
    test_wallet_system()
