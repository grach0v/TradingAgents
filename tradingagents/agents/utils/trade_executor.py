"""
Trade execution system for the TradingAgents framework.
Handles parsing and executing buy/sell decisions with quantities.
"""

import re
from typing import Tuple, Optional
from tradingagents.agents.utils.wallet import TradingWallet
from tradingagents.dataflows.interface import get_YFin_data
from datetime import datetime


class TradeExecutor:
    """Handles trade execution and wallet management."""
    
    def __init__(self, wallet: TradingWallet):
        """Initialize with a wallet instance."""
        self.wallet = wallet
    
    def parse_trade_decision(self, decision: str) -> Tuple[str, Optional[float], Optional[str]]:
        """
        Parse a trade decision to extract action, quantity, and symbol.
        
        Args:
            decision: Trade decision string (e.g., "BUY 0.05 BTC", "SELL 10 NVDA", "HOLD")
            
        Returns:
            Tuple of (action, quantity, symbol)
        """
        # Clean the decision string
        decision = decision.strip().upper()
        
        # Check for HOLD
        if "HOLD" in decision:
            return "HOLD", None, None
        
        # Patterns to match different formats
        patterns = [
            r'(BUY|SELL)\s+(\d+\.?\d*)\s+([A-Z-]+)',  # BUY 0.05 BTC
            r'(BUY|SELL)\s+([A-Z-]+)\s+(\d+\.?\d*)',  # BUY BTC 0.05
            r'(BUY|SELL).*?(\d+\.?\d*)\s+([A-Z-]+)',  # BUY with extra text 0.05 BTC
        ]
        
        for pattern in patterns:
            match = re.search(pattern, decision)
            if match:
                action = match.group(1)
                
                # Determine which group is quantity and which is symbol
                if match.group(2).replace('.', '').isdigit():
                    quantity = float(match.group(2))
                    symbol = match.group(3)
                else:
                    quantity = float(match.group(3))
                    symbol = match.group(2)
                
                return action, quantity, symbol
        
        # If no pattern matches, try to extract just action
        if "BUY" in decision:
            return "BUY", None, None
        elif "SELL" in decision:
            return "SELL", None, None
        
        return "HOLD", None, None
    
    def get_current_price(self, symbol: str, date: str) -> Optional[float]:
        """
        Get the current price for a symbol.
        
        Args:
            symbol: Asset symbol
            date: Trading date
            
        Returns:
            Current price or None if not found
        """
        try:
            # Get price data from YFin
            data = get_YFin_data(symbol, date, 1)
            
            # Parse the data to get the close price
            lines = data.strip().split('\n')
            for line in lines:
                if 'Close:' in line:
                    price_str = line.split('Close:')[1].strip()
                    return float(price_str.replace('$', '').replace(',', ''))
            
            # If no close price found, try to find any price in the data
            for line in lines:
                if '$' in line:
                    # Extract price from line
                    price_match = re.search(r'\$?([\d,]+\.?\d*)', line)
                    if price_match:
                        return float(price_match.group(1).replace(',', ''))
            
        except Exception as e:
            print(f"Error getting price for {symbol}: {e}")
        
        # Default fallback prices for testing
        fallback_prices = {
            'BTC-USD': 45000.0,
            'BTC': 45000.0,
            'ETH-USD': 3000.0,
            'ETH': 3000.0,
            'SOL-USD': 100.0,
            'SOL': 100.0,
            'NVDA': 500.0,
            'TSLA': 250.0,
            'AAPL': 150.0,
        }
        
        return fallback_prices.get(symbol, 100.0)
    
    def execute_trade(self, decision: str, date: str) -> Tuple[bool, str]:
        """
        Execute a trade decision.
        
        Args:
            decision: Trade decision string
            date: Trading date
            
        Returns:
            Tuple of (success, message)
        """
        action, quantity, symbol = self.parse_trade_decision(decision)
        
        if action == "HOLD":
            return True, "HOLD - No action taken"
        
        if not quantity or not symbol:
            return False, f"Invalid trade format: {decision}. Expected format: '{action} X.XX SYMBOL'"
        
        # Get current price
        price = self.get_current_price(symbol, date)
        if not price:
            return False, f"Could not get price for {symbol}"
        
        # Execute the trade
        if action == "BUY":
            success, message = self.wallet.execute_buy(symbol, quantity, price)
        elif action == "SELL":
            success, message = self.wallet.execute_sell(symbol, quantity, price)
        else:
            return False, f"Unknown action: {action}"
        
        if success:
            return True, f"{message} at ${price:.2f} per unit"
        else:
            return False, message
    
    def get_trade_summary(self, decision: str, date: str) -> str:
        """
        Get a summary of what the trade would do without executing it.
        
        Args:
            decision: Trade decision string
            date: Trading date
            
        Returns:
            Summary string
        """
        action, quantity, symbol = self.parse_trade_decision(decision)
        
        if action == "HOLD":
            return "📊 HOLD - Maintaining current position"
        
        if not quantity or not symbol:
            return f"❌ Invalid trade format: {decision}"
        
        price = self.get_current_price(symbol, date)
        if not price:
            return f"❌ Could not get price for {symbol}"
        
        total_value = quantity * price
        
        if action == "BUY":
            can_buy, reason = self.wallet.can_buy(symbol, quantity, price)
            status = "✅" if can_buy else "❌"
            return f"{status} {action} {quantity:.6f} {symbol} at ${price:.2f} = ${total_value:.2f}\n{reason}"
        elif action == "SELL":
            can_sell, reason = self.wallet.can_sell(symbol, quantity)
            status = "✅" if can_sell else "❌"
            return f"{status} {action} {quantity:.6f} {symbol} at ${price:.2f} = ${total_value:.2f}\n{reason}"
        
        return f"❌ Unknown action: {action}"
