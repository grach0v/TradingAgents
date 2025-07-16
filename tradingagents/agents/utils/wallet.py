from typing import Dict, Optional, Tuple
from datetime import datetime
import json
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class WalletState:
    """Represents the current state of the trading wallet."""
    cash_usd: float
    crypto_holdings: Dict[str, float]  # symbol -> amount
    last_updated: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'WalletState':
        """Create from dictionary."""
        return cls(**data)


class TradingWallet:
    """Manages the trading wallet with cash and cryptocurrency holdings."""
    
    def __init__(self, initial_cash_usd: float = 50000.0, initial_crypto: Optional[Dict[str, float]] = None):
        """
        Initialize the trading wallet.
        
        Args:
            initial_cash_usd: Initial USD cash amount
            initial_crypto: Initial crypto holdings {symbol: amount}
        """
        self.state = WalletState(
            cash_usd=initial_cash_usd,
            crypto_holdings=initial_crypto or {
                "BTC": 0.1,
                "ETH": 1.0,
                "SOL": 10.0,
                "NVDA": 5.0  # Example stock holdings
            },
            last_updated=datetime.now().isoformat()
        )
        self.wallet_file = Path("wallet_state.json")
        self.load_wallet()
    
    def get_portfolio_summary(self) -> str:
        """Get a formatted summary of the current portfolio."""
        summary = f"💰 **Current Portfolio:**\n"
        summary += f"Cash (USD): ${self.state.cash_usd:,.2f}\n\n"
        summary += "**Holdings:**\n"
        
        for symbol, amount in self.state.crypto_holdings.items():
            if amount > 0:
                if symbol in ['BTC', 'ETH', 'SOL', 'ADA', 'AVAX', 'DOT', 'MATIC', 'LINK', 'UNI', 'AAVE']:
                    summary += f"• {symbol}: {amount:.6f}\n"
                else:
                    summary += f"• {symbol}: {amount:.2f} shares\n"
        
        return summary
    
    def get_holding_amount(self, symbol: str) -> float:
        """Get the current amount of a specific asset."""
        # Normalize symbol (remove -USD suffix for crypto)
        clean_symbol = symbol.replace('-USD', '').replace('-USDT', '')
        return self.state.crypto_holdings.get(clean_symbol, 0.0)
    
    def can_buy(self, symbol: str, quantity: float, price_per_unit: float) -> Tuple[bool, str]:
        """
        Check if a buy order can be executed.
        
        Args:
            symbol: Asset symbol
            quantity: Amount to buy
            price_per_unit: Price per unit
            
        Returns:
            Tuple of (can_buy, reason)
        """
        total_cost = quantity * price_per_unit
        
        if total_cost > self.state.cash_usd:
            return False, f"Insufficient funds. Need ${total_cost:.2f}, have ${self.state.cash_usd:.2f}"
        
        if quantity <= 0:
            return False, "Quantity must be positive"
            
        return True, "Order can be executed"
    
    def can_sell(self, symbol: str, quantity: float) -> Tuple[bool, str]:
        """
        Check if a sell order can be executed.
        
        Args:
            symbol: Asset symbol
            quantity: Amount to sell
            
        Returns:
            Tuple of (can_sell, reason)
        """
        clean_symbol = symbol.replace('-USD', '').replace('-USDT', '')
        current_holding = self.state.crypto_holdings.get(clean_symbol, 0.0)
        
        if quantity > current_holding:
            return False, f"Insufficient {clean_symbol}. Need {quantity:.6f}, have {current_holding:.6f}"
        
        if quantity <= 0:
            return False, "Quantity must be positive"
            
        return True, "Order can be executed"
    
    def execute_buy(self, symbol: str, quantity: float, price_per_unit: float) -> Tuple[bool, str]:
        """
        Execute a buy order.
        
        Args:
            symbol: Asset symbol
            quantity: Amount to buy
            price_per_unit: Price per unit
            
        Returns:
            Tuple of (success, message)
        """
        can_buy, reason = self.can_buy(symbol, quantity, price_per_unit)
        if not can_buy:
            return False, reason
        
        total_cost = quantity * price_per_unit
        clean_symbol = symbol.replace('-USD', '').replace('-USDT', '')
        
        # Update wallet
        self.state.cash_usd -= total_cost
        self.state.crypto_holdings[clean_symbol] = self.state.crypto_holdings.get(clean_symbol, 0.0) + quantity
        self.state.last_updated = datetime.now().isoformat()
        
        # Save to file
        self.save_wallet()
        
        return True, f"Successfully bought {quantity:.6f} {clean_symbol} for ${total_cost:.2f}"
    
    def execute_sell(self, symbol: str, quantity: float, price_per_unit: float) -> Tuple[bool, str]:
        """
        Execute a sell order.
        
        Args:
            symbol: Asset symbol
            quantity: Amount to sell
            price_per_unit: Price per unit
            
        Returns:
            Tuple of (success, message)
        """
        can_sell, reason = self.can_sell(symbol, quantity)
        if not can_sell:
            return False, reason
        
        total_proceeds = quantity * price_per_unit
        clean_symbol = symbol.replace('-USD', '').replace('-USDT', '')
        
        # Update wallet
        self.state.cash_usd += total_proceeds
        self.state.crypto_holdings[clean_symbol] -= quantity
        self.state.last_updated = datetime.now().isoformat()
        
        # Save to file
        self.save_wallet()
        
        return True, f"Successfully sold {quantity:.6f} {clean_symbol} for ${total_proceeds:.2f}"
    
    def get_wallet_context_for_agent(self, symbol: str) -> str:
        """
        Get wallet context formatted for agent decision making.
        
        Args:
            symbol: The symbol being analyzed
            
        Returns:
            Formatted wallet context string
        """
        clean_symbol = symbol.replace('-USD', '').replace('-USDT', '')
        current_holding = self.state.crypto_holdings.get(clean_symbol, 0.0)
        
        context = f"""
📊 **WALLET CONTEXT FOR {symbol}:**

💰 **Available Cash:** ${self.state.cash_usd:,.2f}

🏦 **Current Holdings:**
• {clean_symbol}: {current_holding:.6f} {"(cryptocurrency)" if clean_symbol in ['BTC', 'ETH', 'SOL', 'ADA', 'AVAX', 'DOT', 'MATIC', 'LINK', 'UNI', 'AAVE'] else "(shares)"}

📈 **Portfolio Summary:**
{self.get_portfolio_summary()}

💡 **Decision Guidelines:**
- You have ${self.state.cash_usd:,.2f} available for purchases
- Consider position sizing based on portfolio allocation
- Factor in risk management when determining buy/sell quantities
- Current {clean_symbol} position: {current_holding:.6f}

🎯 **Required Output Format:**
Your final decision must include specific quantities:
- For BUY: "BUY X.XXX {clean_symbol}" (specify exact amount)
- For SELL: "SELL X.XXX {clean_symbol}" (specify exact amount)  
- For HOLD: "HOLD" (maintain current position)

Examples:
- "BUY 0.05 BTC" 
- "SELL 0.5 ETH"
- "BUY 10 NVDA"
- "HOLD"
"""
        return context
    
    def save_wallet(self):
        """Save wallet state to file."""
        try:
            with open(self.wallet_file, 'w') as f:
                json.dump(self.state.to_dict(), f, indent=2)
        except Exception as e:
            print(f"Error saving wallet: {e}")
    
    def load_wallet(self):
        """Load wallet state from file."""
        try:
            if self.wallet_file.exists():
                with open(self.wallet_file, 'r') as f:
                    data = json.load(f)
                self.state = WalletState.from_dict(data)
        except Exception as e:
            print(f"Error loading wallet: {e}")
            # Keep default state if loading fails
    
    def reset_wallet(self, initial_cash_usd: float = 50000.0, initial_crypto: Optional[Dict[str, float]] = None):
        """Reset wallet to initial state."""
        self.state = WalletState(
            cash_usd=initial_cash_usd,
            crypto_holdings=initial_crypto or {
                "BTC": 0.1,
                "ETH": 1.0,
                "SOL": 10.0,
                "NVDA": 5.0
            },
            last_updated=datetime.now().isoformat()
        )
        self.save_wallet()
