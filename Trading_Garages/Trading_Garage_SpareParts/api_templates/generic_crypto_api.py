"""
Generic Crypto Exchange API Template
Works with multiple exchanges using public endpoints
"""
import requests
from typing import Dict, Optional, List, Any
from datetime import datetime


class GenericCryptoAPI:
    """
    Generic cryptocurrency exchange API template.
    Supports multiple exchanges through unified interface.
    NO SECRETS REQUIRED - Public endpoints only!
    """
    
    SUPPORTED_EXCHANGES = {
        "binance": "https://api.binance.com/api/v3",
        "coinbase": "https://api.coinbase.com/v2",
        "kraken": "https://api.kraken.com/0/public",
        "coinmarketcap": "https://api.coinmarketcap.com/data-api/v3"
    }
    
    def __init__(self, exchange: str = "binance"):
        """
        Initialize API client for specific exchange.
        
        Args:
            exchange: Exchange name (binance, coinbase, kraken)
        """
        self.exchange = exchange.lower()
        if self.exchange not in self.SUPPORTED_EXCHANGES:
            raise ValueError(f"Unsupported exchange: {exchange}")
        self.base_url = self.SUPPORTED_EXCHANGES[self.exchange]
    
    def get_price(self, symbol: str) -> Optional[float]:
        """
        Get current price for a trading pair.
        Exchange-agnostic method.
        """
        if self.exchange == "binance":
            return self._get_binance_price(symbol)
        elif self.exchange == "coinbase":
            return self._get_coinbase_price(symbol)
        elif self.exchange == "kraken":
            return self._get_kraken_price(symbol)
        return None
    
    def _get_binance_price(self, symbol: str) -> Optional[float]:
        """Get price from Binance."""
        try:
            url = f"{self.base_url}/ticker/price"
            response = requests.get(url, params={"symbol": symbol}, timeout=10)
            response.raise_for_status()
            return float(response.json()["price"])
        except:
            return None
    
    def _get_coinbase_price(self, symbol: str) -> Optional[float]:
        """Get price from Coinbase."""
        try:
            # Coinbase uses BTC-USD format
            symbol = symbol.replace("USDT", "USD").replace("", "-")
            url = f"{self.base_url}/prices/{symbol}/spot"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return float(response.json()["data"]["amount"])
        except:
            return None
    
    def _get_kraken_price(self, symbol: str) -> Optional[float]:
        """Get price from Kraken."""
        try:
            # Kraken uses XXBTZUSD format
            url = f"{self.base_url}/Ticker"
            response = requests.get(url, params={"pair": symbol}, timeout=10)
            response.raise_for_status()
            data = response.json()
            if "result" in data:
                for pair_data in data["result"].values():
                    return float(pair_data["c"][0])
            return None
        except:
            return None
    
    def compare_prices(self, symbol: str) -> Dict[str, Optional[float]]:
        """
        Compare price across all supported exchanges.
        
        Returns:
            Dict with exchange names as keys and prices as values
        """
        prices = {}
        for exchange_name in self.SUPPORTED_EXCHANGES.keys():
            try:
                api = GenericCryptoAPI(exchange_name)
                price = api.get_price(symbol)
                prices[exchange_name] = price
            except:
                prices[exchange_name] = None
        return prices
    
    def find_arbitrage(self, symbol: str, min_diff_percent: float = 0.5) -> Optional[Dict]:
        """
        Find arbitrage opportunities between exchanges.
        
        Args:
            symbol: Trading pair to check
            min_diff_percent: Minimum price difference percentage
            
        Returns:
            Dict with arbitrage opportunity details, or None
        """
        prices = self.compare_prices(symbol)
        valid_prices = {k: v for k, v in prices.items() if v is not None}
        
        if len(valid_prices) < 2:
            return None
        
        lowest_exchange = min(valid_prices, key=valid_prices.get)
        highest_exchange = max(valid_prices, key=valid_prices.get)
        
        lowest_price = valid_prices[lowest_exchange]
        highest_price = valid_prices[highest_exchange]
        
        diff_percent = ((highest_price - lowest_price) / lowest_price) * 100
        
        if diff_percent >= min_diff_percent:
            return {
                "symbol": symbol,
                "buy_from": lowest_exchange,
                "buy_price": lowest_price,
                "sell_to": highest_exchange,
                "sell_price": highest_price,
                "profit_percent": diff_percent,
                "timestamp": datetime.now().isoformat()
            }
        
        return None


def quick_test():
    """Test generic crypto API."""
    print("=" * 60)
    print("🔧 Generic Crypto API Test")
    print("=" * 60)
    print()
    
    # Test single exchange
    print("📊 Test 1: Binance BTC Price")
    binance = GenericCryptoAPI("binance")
    btc_price = binance.get_price("BTCUSDT")
    if btc_price:
        print(f"   BTC: ${btc_price:,.2f}")
    print()
    
    # Test price comparison
    print("📊 Test 2: Compare BTC Price Across Exchanges")
    prices = binance.compare_prices("BTCUSDT")
    for exchange, price in prices.items():
        if price:
            print(f"   {exchange.capitalize():15} ${price:,.2f}")
        else:
            print(f"   {exchange.capitalize():15} N/A")
    print()
    
    # Test arbitrage detection
    print("📊 Test 3: Arbitrage Opportunities")
    arb = binance.find_arbitrage("BTCUSDT", min_diff_percent=0.1)
    if arb:
        print(f"   🎯 Opportunity Found!")
        print(f"   Buy from:  {arb['buy_from']} @ ${arb['buy_price']:,.2f}")
        print(f"   Sell to:   {arb['sell_to']} @ ${arb['sell_price']:,.2f}")
        print(f"   Profit:    {arb['profit_percent']:.2f}%")
    else:
        print("   No significant arbitrage opportunities found")
    print()
    
    print("=" * 60)
    print("✅ Generic crypto API test complete!")
    print("=" * 60)


if __name__ == "__main__":
    quick_test()
