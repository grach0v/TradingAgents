#!/usr/bin/env python3
"""
Wallet management utility for TradingAgents.
"""

import sys
import json
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from tradingagents.agents.utils.wallet import TradingWallet


def main():
    """Main wallet management interface."""
    wallet = TradingWallet()
    
    if len(sys.argv) < 2:
        print_usage()
        return
    
    command = sys.argv[1].lower()
    
    if command == "status":
        print("💰 WALLET STATUS")
        print("=" * 50)
        print(wallet.get_portfolio_summary())
        
    elif command == "reset":
        initial_cash = 50000.0
        initial_crypto = {
            "BTC": 0.1,
            "ETH": 1.0,
            "SOL": 10.0,
            "NVDA": 5.0
        }
        
        if len(sys.argv) >= 3:
            initial_cash = float(sys.argv[2])
        
        wallet.reset_wallet(initial_cash, initial_crypto)
        print(f"🔄 Wallet reset successfully!")
        print(f"💰 Initial cash: ${initial_cash:,.2f}")
        print("📊 Initial holdings:")
        for symbol, amount in initial_crypto.items():
            if symbol in ['BTC', 'ETH', 'SOL']:
                print(f"  • {symbol}: {amount:.6f}")
            else:
                print(f"  • {symbol}: {amount:.2f} shares")
                
    elif command == "add-cash":
        if len(sys.argv) < 3:
            print("❌ Usage: python wallet_manager.py add-cash <amount>")
            return
        
        amount = float(sys.argv[2])
        wallet.state.cash_usd += amount
        wallet.save_wallet()
        print(f"✅ Added ${amount:,.2f} to wallet")
        print(f"💰 New cash balance: ${wallet.state.cash_usd:,.2f}")
        
    elif command == "add-crypto":
        if len(sys.argv) < 4:
            print("❌ Usage: python wallet_manager.py add-crypto <symbol> <amount>")
            return
        
        symbol = sys.argv[2].upper()
        amount = float(sys.argv[3])
        
        current = wallet.state.crypto_holdings.get(symbol, 0.0)
        wallet.state.crypto_holdings[symbol] = current + amount
        wallet.save_wallet()
        
        print(f"✅ Added {amount:.6f} {symbol} to wallet")
        print(f"📊 New {symbol} balance: {wallet.state.crypto_holdings[symbol]:.6f}")
        
    elif command == "simulate":
        if len(sys.argv) < 3:
            print("❌ Usage: python wallet_manager.py simulate '<decision>'")
            print("Examples:")
            print("  python wallet_manager.py simulate 'BUY 0.05 BTC'")
            print("  python wallet_manager.py simulate 'SELL 10 NVDA'")
            return
        
        decision = sys.argv[2]
        from tradingagents.agents.utils.trade_executor import TradeExecutor
        
        executor = TradeExecutor(wallet)
        summary = executor.get_trade_summary(decision, "2024-05-10")
        
        print("🎯 TRADE SIMULATION")
        print("=" * 50)
        print(f"Decision: {decision}")
        print(f"Result: {summary}")
        
    elif command == "backup":
        backup_file = "wallet_backup.json"
        with open(backup_file, 'w') as f:
            json.dump(wallet.state.to_dict(), f, indent=2)
        print(f"💾 Wallet backed up to {backup_file}")
        
    elif command == "restore":
        if len(sys.argv) < 3:
            print("❌ Usage: python wallet_manager.py restore <backup_file>")
            return
        
        backup_file = sys.argv[2]
        if not Path(backup_file).exists():
            print(f"❌ Backup file {backup_file} not found")
            return
        
        with open(backup_file, 'r') as f:
            data = json.load(f)
        
        wallet.state = wallet.state.from_dict(data)
        wallet.save_wallet()
        print(f"✅ Wallet restored from {backup_file}")
        
    else:
        print_usage()


def print_usage():
    """Print usage information."""
    print("🏦 WALLET MANAGER")
    print("=" * 50)
    print("Usage: python wallet_manager.py <command> [args]")
    print()
    print("Commands:")
    print("  status                    - Show current wallet status")
    print("  reset [cash_amount]       - Reset wallet to initial state")
    print("  add-cash <amount>         - Add cash to wallet")
    print("  add-crypto <symbol> <amt> - Add crypto to wallet")
    print("  simulate '<decision>'     - Simulate a trade decision")
    print("  backup                    - Backup wallet to file")
    print("  restore <backup_file>     - Restore wallet from backup")
    print()
    print("Examples:")
    print("  python wallet_manager.py status")
    print("  python wallet_manager.py reset 100000")
    print("  python wallet_manager.py add-cash 10000")
    print("  python wallet_manager.py add-crypto BTC 0.1")
    print("  python wallet_manager.py simulate 'BUY 0.05 BTC'")


if __name__ == "__main__":
    main()
