def get_crypto_aware_system_message(ticker, original_message):
    """
    Modify system messages to be crypto-aware when analyzing crypto symbols
    """
    is_crypto = ticker.endswith('-USD') or ticker.endswith('-USDT') or ticker in ['BTC', 'ETH', 'ADA', 'SOL', 'AVAX', 'DOT', 'MATIC', 'LINK', 'UNI', 'AAVE']
    
    if is_crypto:
        # Replace stock-specific terms with crypto equivalents
        crypto_message = original_message.replace("company", "cryptocurrency project")
        crypto_message = crypto_message.replace("stock", "cryptocurrency")
        crypto_message = crypto_message.replace("stocks", "cryptocurrencies")
        crypto_message = crypto_message.replace("financial markets", "cryptocurrency markets")
        crypto_message = crypto_message.replace("company's", "cryptocurrency's")
        crypto_message = crypto_message.replace("Company", "Cryptocurrency")
        crypto_message = crypto_message.replace("trading", "crypto trading")
        crypto_message = crypto_message.replace("Stock", "Cryptocurrency")
        
        # Add crypto-specific context
        crypto_additions = """
        
        IMPORTANT: You are analyzing a CRYPTOCURRENCY. Consider these crypto-specific factors:
        - 24/7 trading with no market close
        - Higher volatility and faster price movements
        - Sentiment-driven price action
        - Regulatory uncertainty and news impacts
        - On-chain metrics and network health
        - Community and social media influence
        - DeFi/NFT ecosystem integration
        - Institutional adoption trends
        - Technical analysis patterns in high-volatility environment
        """
        
        crypto_message = crypto_message + crypto_additions
        
        return crypto_message
    
    return original_message

def get_crypto_aware_analyst_message(ticker, analyst_type):
    """
    Get crypto-specific analyst system messages
    """
    base_messages = {
        "market": """You are a cryptocurrency technical analyst tasked with analyzing crypto market data. Focus on:
        - 24/7 market dynamics and volatility patterns
        - Crypto-specific technical indicators effectiveness
        - Support/resistance levels in volatile markets
        - Volume analysis and liquidity considerations
        - Sentiment-driven price movements
        - Regulatory impact on technical patterns
        """,
        
        "social": """You are a cryptocurrency social media and community analyst. Focus on:
        - Twitter/X crypto sentiment and influencer opinions
        - Reddit crypto communities and discussions
        - Telegram/Discord community activity
        - Fear and Greed Index analysis
        - Whale activity and on-chain social signals
        - Crypto-specific news and regulatory sentiment
        """,
        
        "news": """You are a cryptocurrency news analyst. Focus on:
        - Regulatory developments and government announcements
        - Institutional adoption and corporate crypto strategies
        - DeFi protocol news and security incidents
        - Exchange news and regulatory issues
        - Macroeconomic factors affecting crypto
        - Technology upgrades and blockchain developments
        """,
        
        "fundamentals": """You are a cryptocurrency fundamental analyst. Focus on:
        - Network fundamentals (hash rate, active addresses, TVL)
        - Development activity and ecosystem health
        - Adoption metrics and institutional holdings
        - Tokenomics and supply dynamics
        - On-chain metrics and protocol revenue
        - Regulatory environment impact
        """
    }
    
    is_crypto = ticker.endswith('-USD') or ticker.endswith('-USDT') or ticker in ['BTC', 'ETH', 'ADA', 'SOL', 'AVAX', 'DOT', 'MATIC', 'LINK', 'UNI', 'AAVE']
    
    if is_crypto and analyst_type in base_messages:
        return base_messages[analyst_type]
    
    return None
