"""
Binance Public API Template - NO SECRETS REQUIRED
Real-time crypto data using public endpoints only
"""
import requests
from typing import Dict, Optional, List


class BinancePublicAPI:
    """
    Binance Public API client for testing and experimentation.
    Uses only public endpoints - no authentication required!
    """
    
    BASE_URL = "https://api.binance.com/api/v3"
    
    def get_ticker_price(self, symbol: str = "BTCUSDT") -> Optional[float]:
        """
        Get current price for a trading pair.
        
        Args:
            symbol: Trading pair (e.g., "BTCUSDT", "ETHUSDT")
            
        Returns:
            Current price as float, or None if error
        """
        try:
            url = f"{self.BASE_URL}/ticker/price"
            params = {"symbol": symbol}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return float(data.get("price", 0))
        except Exception as e:
            print(f"Error fetching price: {e}")
            return None
    
    def get_24h_ticker(self, symbol: str = "BTCUSDT") -> Optional[Dict]:
        """
        Get 24-hour ticker statistics.
        
        Returns:
            Dict with price change, volume, high, low, etc.
        """
        try:
            url = f"{self.BASE_URL}/ticker/24hr"
            params = {"symbol": symbol}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching 24h ticker: {e}")
            return None
    
    def get_orderbook(self, symbol: str = "BTCUSDT", limit: int = 10) -> Optional[Dict]:
        """
        Get current order book (bids and asks).
        
        Args:
            symbol: Trading pair
            limit: Number of price levels (max 5000)
            
        Returns:
            Dict with 'bids' and 'asks' arrays
        """
        try:
            url = f"{self.BASE_URL}/depth"
            params = {"symbol": symbol, "limit": limit}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching orderbook: {e}")
            return None
    
    def get_recent_trades(self, symbol: str = "BTCUSDT", limit: int = 10) -> Optional[List]:
        """
        Get recent trades for a symbol.
        
        Returns:
            List of recent trades with price, quantity, time
        """
        try:
            url = f"{self.BASE_URL}/trades"
            params = {"symbol": symbol, "limit": limit}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching recent trades: {e}")
            return None
    
    def get_klines(
        self, 
        symbol: str = "BTCUSDT", 
        interval: str = "1h", 
        limit: int = 100
    ) -> Optional[List]:
        """
        Get candlestick/kline data for charting.
        
        Args:
            symbol: Trading pair
            interval: Timeframe (1m, 5m, 15m, 1h, 4h, 1d, etc.)
            limit: Number of candles (max 1000)
            
        Returns:
            List of OHLCV candles
        """
        try:
            url = f"{self.BASE_URL}/klines"
            params = {
                "symbol": symbol,
                "interval": interval,
                "limit": limit
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching klines: {e}")
            return None
    
    def get_exchange_info(self) -> Optional[Dict]:
        """Get exchange trading rules and symbol information."""
        try:
            url = f"{self.BASE_URL}/exchangeInfo"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching exchange info: {e}")
            return None


def quick_test():
    """Quick test of Binance public API."""
    print("=" * 60)
    print("🔧 Binance Public API Test - NO SECRETS REQUIRED")
    print("=" * 60)
    print()
    
    api = BinancePublicAPI()
    
    # Test 1: Get current BTC price
    print("📊 Test 1: Current BTC Price")
    btc_price = api.get_ticker_price("BTCUSDT")
    if btc_price:
        print(f"   BTC/USDT: ${btc_price:,.2f}")
    print()
    
    # Test 2: Get ETH price
    print("📊 Test 2: Current ETH Price")
    eth_price = api.get_ticker_price("ETHUSDT")
    if eth_price:
        print(f"   ETH/USDT: ${eth_price:,.2f}")
    print()
    
    # Test 3: 24h stats
    print("📊 Test 3: 24-Hour BTC Statistics")
    ticker = api.get_24h_ticker("BTCUSDT")
    if ticker:
        print(f"   High:        ${float(ticker['highPrice']):,.2f}")
        print(f"   Low:         ${float(ticker['lowPrice']):,.2f}")
        print(f"   Volume:      {float(ticker['volume']):,.2f} BTC")
        print(f"   Price Change: {float(ticker['priceChangePercent']):.2f}%")
    print()
    
    # Test 4: Order book
    print("📊 Test 4: Order Book (Top 5 Bids/Asks)")
    orderbook = api.get_orderbook("BTCUSDT", limit=5)
    if orderbook:
        print("   Top 5 Asks (Sell Orders):")
        for ask in orderbook['asks'][:5]:
            print(f"      ${float(ask[0]):,.2f} - {float(ask[1]):.4f} BTC")
        print("   Top 5 Bids (Buy Orders):")
        for bid in orderbook['bids'][:5]:
            print(f"      ${float(bid[0]):,.2f} - {float(bid[1]):.4f} BTC")
    print()
    
    print("=" * 60)
    print("✅ Binance Public API test complete!")
    print("=" * 60)


if __name__ == "__main__":
    quick_test()
