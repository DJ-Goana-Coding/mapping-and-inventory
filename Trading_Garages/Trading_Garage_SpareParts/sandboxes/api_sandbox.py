"""
API Testing Sandbox
Test real-time crypto APIs without secrets
"""
import sys
import os

# Add api_templates to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api_templates'))

try:
    from binance_public_api import BinancePublicAPI
    from generic_crypto_api import GenericCryptoAPI
except ImportError:
    print("⚠️  API templates not found. Please ensure api_templates/ directory exists.")
    sys.exit(1)


def test_binance_api():
    """Test Binance public API."""
    print("=" * 60)
    print("🔧 Test 1: Binance Public API")
    print("=" * 60)
    print()
    
    api = BinancePublicAPI()
    
    # Get multiple prices
    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT"]
    
    print("📊 Current Crypto Prices:")
    for symbol in symbols:
        price = api.get_ticker_price(symbol)
        if price:
            coin = symbol.replace("USDT", "")
            print(f"   {coin:6} ${price:,.2f}")
    
    print()


def test_price_comparison():
    """Test price comparison across exchanges."""
    print("=" * 60)
    print("🔧 Test 2: Multi-Exchange Price Comparison")
    print("=" * 60)
    print()
    
    api = GenericCryptoAPI()
    
    print("📊 BTC Price Across Exchanges:")
    prices = api.compare_prices("BTCUSDT")
    for exchange, price in prices.items():
        if price:
            print(f"   {exchange.capitalize():15} ${price:,.2f}")
        else:
            print(f"   {exchange.capitalize():15} N/A")
    
    print()


def test_arbitrage_detection():
    """Test arbitrage opportunity detection."""
    print("=" * 60)
    print("🔧 Test 3: Arbitrage Detection")
    print("=" * 60)
    print()
    
    api = GenericCryptoAPI()
    
    symbols = ["BTCUSDT", "ETHUSDT"]
    
    print("🔍 Scanning for Arbitrage Opportunities:")
    print()
    
    for symbol in symbols:
        coin = symbol.replace("USDT", "")
        print(f"   {coin}:")
        
        arb = api.find_arbitrage(symbol, min_diff_percent=0.1)
        if arb:
            print(f"      ✅ Opportunity Found!")
            print(f"      Buy:   {arb['buy_from']} @ ${arb['buy_price']:,.2f}")
            print(f"      Sell:  {arb['sell_to']} @ ${arb['sell_price']:,.2f}")
            print(f"      Profit: {arb['profit_percent']:.2f}%")
        else:
            print(f"      No significant opportunities")
        print()
    
    print()


def test_orderbook():
    """Test orderbook data retrieval."""
    print("=" * 60)
    print("🔧 Test 4: Order Book Analysis")
    print("=" * 60)
    print()
    
    api = BinancePublicAPI()
    
    print("📊 BTC/USDT Order Book:")
    orderbook = api.get_orderbook("BTCUSDT", limit=5)
    
    if orderbook:
        print("\n   Top 5 Sell Orders (Asks):")
        for i, ask in enumerate(orderbook['asks'][:5], 1):
            print(f"      {i}. ${float(ask[0]):,.2f} - {float(ask[1]):.4f} BTC")
        
        print("\n   Top 5 Buy Orders (Bids):")
        for i, bid in enumerate(orderbook['bids'][:5], 1):
            print(f"      {i}. ${float(bid[0]):,.2f} - {float(bid[1]):.4f} BTC")
        
        # Calculate spread
        best_ask = float(orderbook['asks'][0][0])
        best_bid = float(orderbook['bids'][0][0])
        spread = best_ask - best_bid
        spread_percent = (spread / best_ask) * 100
        
        print(f"\n   Spread: ${spread:.2f} ({spread_percent:.3f}%)")
    
    print()


def test_recent_trades():
    """Test recent trades data."""
    print("=" * 60)
    print("🔧 Test 5: Recent Trades")
    print("=" * 60)
    print()
    
    api = BinancePublicAPI()
    
    print("📊 Last 10 BTC/USDT Trades:")
    trades = api.get_recent_trades("BTCUSDT", limit=10)
    
    if trades:
        for i, trade in enumerate(trades[:10], 1):
            price = float(trade['price'])
            qty = float(trade['qty'])
            side = "🟢 BUY " if trade['isBuyerMaker'] else "🔴 SELL"
            print(f"   {i:2}. {side} ${price:,.2f} x {qty:.4f} BTC")
    
    print()


def interactive_mode():
    """Interactive testing mode."""
    print("=" * 60)
    print("🎮 INTERACTIVE MODE")
    print("=" * 60)
    print()
    
    api = BinancePublicAPI()
    
    print("Commands:")
    print("  price <SYMBOL>  - Get current price (e.g., price BTCUSDT)")
    print("  compare <SYMBOL> - Compare prices across exchanges")
    print("  book <SYMBOL>   - Show order book")
    print("  help            - Show this message")
    print("  quit            - Exit")
    print()
    
    while True:
        try:
            cmd = input("api> ").strip()
            
            if not cmd:
                continue
            
            parts = cmd.split()
            command = parts[0].lower()
            
            if command == "quit":
                print("Goodbye!")
                break
            
            elif command == "help":
                print("\nCommands:")
                print("  price <SYMBOL>  - Get current price")
                print("  compare <SYMBOL> - Compare across exchanges")
                print("  book <SYMBOL>   - Show order book")
                print("  quit            - Exit\n")
            
            elif command == "price" and len(parts) > 1:
                symbol = parts[1].upper()
                price = api.get_ticker_price(symbol)
                if price:
                    print(f"   {symbol}: ${price:,.2f}\n")
                else:
                    print(f"   Error fetching price for {symbol}\n")
            
            elif command == "compare" and len(parts) > 1:
                symbol = parts[1].upper()
                multi_api = GenericCryptoAPI()
                prices = multi_api.compare_prices(symbol)
                print()
                for exchange, price in prices.items():
                    if price:
                        print(f"   {exchange:15} ${price:,.2f}")
                print()
            
            elif command == "book" and len(parts) > 1:
                symbol = parts[1].upper()
                book = api.get_orderbook(symbol, limit=5)
                if book:
                    print("\n   Top Asks:")
                    for ask in book['asks'][:5]:
                        print(f"      ${float(ask[0]):,.2f} - {float(ask[1]):.4f}")
                    print("   Top Bids:")
                    for bid in book['bids'][:5]:
                        print(f"      ${float(bid[0]):,.2f} - {float(bid[1]):.4f}")
                    print()
            
            else:
                print("   Unknown command. Type 'help' for commands.\n")
        
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"   Error: {e}\n")


def main():
    """Main test runner."""
    print("=" * 60)
    print("🔧 API TESTING SANDBOX - NO SECRETS REQUIRED")
    print("=" * 60)
    print()
    
    print("Running automated tests...\n")
    
    test_binance_api()
    test_price_comparison()
    test_arbitrage_detection()
    test_orderbook()
    test_recent_trades()
    
    print("=" * 60)
    print("✅ All automated tests complete!")
    print("=" * 60)
    print()
    
    # Ask if user wants interactive mode
    response = input("Enter interactive mode? (y/n): ").strip().lower()
    if response == 'y':
        interactive_mode()


if __name__ == "__main__":
    main()
