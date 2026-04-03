"""
Strategy Sandbox - Quick Testing Environment
Mix and match components to build and test trading strategies
"""
import sys
from typing import List, Dict, Any

# Mock data for testing (replace with real data in production)
MOCK_PRICES = [
    100, 102, 101, 103, 105, 104, 106, 108, 107, 109,
    111, 110, 112, 114, 113, 115, 117, 116, 118, 120
]


class Indicator:
    """Base class for technical indicators."""
    
    def __init__(self, name: str):
        self.name = name
    
    def calculate(self, prices: List[float]) -> List[float]:
        """Calculate indicator values."""
        raise NotImplementedError


class MovingAverage(Indicator):
    """Simple Moving Average indicator."""
    
    def __init__(self, period: int = 10):
        super().__init__(f"MA({period})")
        self.period = period
    
    def calculate(self, prices: List[float]) -> List[float]:
        """Calculate moving average."""
        result = []
        for i in range(len(prices)):
            if i < self.period - 1:
                result.append(None)
            else:
                window = prices[i - self.period + 1:i + 1]
                result.append(sum(window) / len(window))
        return result


class RSI(Indicator):
    """Relative Strength Index indicator."""
    
    def __init__(self, period: int = 14):
        super().__init__(f"RSI({period})")
        self.period = period
    
    def calculate(self, prices: List[float]) -> List[float]:
        """Calculate RSI (simplified)."""
        result = []
        for i in range(len(prices)):
            if i < self.period:
                result.append(50)  # Neutral default
            else:
                gains = []
                losses = []
                for j in range(i - self.period + 1, i + 1):
                    change = prices[j] - prices[j - 1]
                    if change > 0:
                        gains.append(change)
                    else:
                        losses.append(abs(change))
                
                avg_gain = sum(gains) / self.period if gains else 0
                avg_loss = sum(losses) / self.period if losses else 0
                
                if avg_loss == 0:
                    result.append(100)
                else:
                    rs = avg_gain / avg_loss
                    rsi = 100 - (100 / (1 + rs))
                    result.append(rsi)
        
        return result


class Signal:
    """Base class for trading signals."""
    
    def __init__(self, name: str):
        self.name = name
    
    def generate(self, prices: List[float], indicators: Dict[str, List[float]]) -> List[str]:
        """Generate trading signals (BUY, SELL, HOLD)."""
        raise NotImplementedError


class CrossoverSignal(Signal):
    """Generate signals based on indicator crossovers."""
    
    def __init__(self, fast_indicator: str, slow_indicator: str):
        super().__init__(f"Crossover({fast_indicator}, {slow_indicator})")
        self.fast = fast_indicator
        self.slow = slow_indicator
    
    def generate(self, prices: List[float], indicators: Dict[str, List[float]]) -> List[str]:
        """Generate crossover signals."""
        signals = []
        fast_values = indicators.get(self.fast, [])
        slow_values = indicators.get(self.slow, [])
        
        for i in range(len(prices)):
            if i == 0 or not fast_values[i] or not slow_values[i]:
                signals.append("HOLD")
            else:
                prev_fast = fast_values[i - 1]
                prev_slow = slow_values[i - 1]
                curr_fast = fast_values[i]
                curr_slow = slow_values[i]
                
                # Golden cross - fast crosses above slow
                if prev_fast <= prev_slow and curr_fast > curr_slow:
                    signals.append("BUY")
                # Death cross - fast crosses below slow
                elif prev_fast >= prev_slow and curr_fast < curr_slow:
                    signals.append("SELL")
                else:
                    signals.append("HOLD")
        
        return signals


class Strategy:
    """Trading strategy builder."""
    
    def __init__(self, name: str = "Custom Strategy"):
        self.name = name
        self.indicators = {}
        self.signals = []
    
    def add_indicator(self, indicator: Indicator):
        """Add an indicator to the strategy."""
        self.indicators[indicator.name] = indicator
        print(f"✅ Added indicator: {indicator.name}")
    
    def add_signal(self, signal: Signal):
        """Add a signal generator to the strategy."""
        self.signals.append(signal)
        print(f"✅ Added signal: {signal.name}")
    
    def backtest(self, prices: List[float]) -> Dict[str, Any]:
        """Backtest the strategy on historical prices."""
        print()
        print("=" * 60)
        print(f"🎯 Backtesting Strategy: {self.name}")
        print("=" * 60)
        print()
        
        # Calculate all indicators
        indicator_values = {}
        for name, indicator in self.indicators.items():
            values = indicator.calculate(prices)
            indicator_values[name] = values
            print(f"📊 Calculated {name}")
        
        # Generate signals
        all_signals = []
        for signal_gen in self.signals:
            signals = signal_gen.generate(prices, indicator_values)
            all_signals.append(signals)
            print(f"📈 Generated {signal_gen.name}")
        
        # Combine signals (simple majority vote)
        final_signals = []
        for i in range(len(prices)):
            signal_votes = [sig[i] for sig in all_signals]
            buy_votes = signal_votes.count("BUY")
            sell_votes = signal_votes.count("SELL")
            
            if buy_votes > sell_votes:
                final_signals.append("BUY")
            elif sell_votes > buy_votes:
                final_signals.append("SELL")
            else:
                final_signals.append("HOLD")
        
        # Calculate performance
        trades = 0
        wins = 0
        position = None
        entry_price = 0
        
        for i in range(len(prices)):
            if final_signals[i] == "BUY" and not position:
                position = "LONG"
                entry_price = prices[i]
                trades += 1
            elif final_signals[i] == "SELL" and position == "LONG":
                if prices[i] > entry_price:
                    wins += 1
                position = None
        
        win_rate = (wins / trades * 100) if trades > 0 else 0
        
        print()
        print("📊 Backtest Results:")
        print(f"   Total Trades:  {trades}")
        print(f"   Winning Trades: {wins}")
        print(f"   Win Rate:      {win_rate:.1f}%")
        print()
        
        # Show last 5 signals
        print("📈 Last 5 Signals:")
        for i in range(max(0, len(prices) - 5), len(prices)):
            print(f"   Price: ${prices[i]:,.2f} → {final_signals[i]}")
        
        print()
        print("=" * 60)
        print("✅ Backtest Complete!")
        print("=" * 60)
        
        return {
            "total_trades": trades,
            "wins": wins,
            "win_rate": win_rate,
            "signals": final_signals
        }


def example_1_simple_ma_crossover():
    """Example 1: Simple Moving Average Crossover."""
    print("\n🎨 Example 1: Simple MA Crossover Strategy\n")
    
    strategy = Strategy("MA Crossover")
    strategy.add_indicator(MovingAverage(period=5))
    strategy.add_indicator(MovingAverage(period=10))
    strategy.add_signal(CrossoverSignal("MA(5)", "MA(10)"))
    
    results = strategy.backtest(MOCK_PRICES)


def example_2_rsi_strategy():
    """Example 2: RSI-based Strategy."""
    print("\n🎨 Example 2: RSI Strategy\n")
    
    # Create custom RSI signal
    class RSISignal(Signal):
        def generate(self, prices, indicators):
            signals = []
            rsi_values = indicators.get("RSI(14)", [])
            for rsi in rsi_values:
                if rsi < 30:
                    signals.append("BUY")  # Oversold
                elif rsi > 70:
                    signals.append("SELL")  # Overbought
                else:
                    signals.append("HOLD")
            return signals
    
    strategy = Strategy("RSI Strategy")
    strategy.add_indicator(RSI(period=14))
    strategy.add_signal(RSISignal("RSI Levels"))
    
    results = strategy.backtest(MOCK_PRICES)


def example_3_combined_strategy():
    """Example 3: Combined MA + RSI Strategy."""
    print("\n🎨 Example 3: Combined MA + RSI Strategy\n")
    
    class RSISignal(Signal):
        def generate(self, prices, indicators):
            signals = []
            rsi_values = indicators.get("RSI(14)", [])
            for rsi in rsi_values:
                if rsi < 30:
                    signals.append("BUY")
                elif rsi > 70:
                    signals.append("SELL")
                else:
                    signals.append("HOLD")
            return signals
    
    strategy = Strategy("MA + RSI Combined")
    strategy.add_indicator(MovingAverage(period=5))
    strategy.add_indicator(MovingAverage(period=10))
    strategy.add_indicator(RSI(period=14))
    strategy.add_signal(CrossoverSignal("MA(5)", "MA(10)"))
    strategy.add_signal(RSISignal("RSI Levels"))
    
    results = strategy.backtest(MOCK_PRICES)


def main():
    """Run all examples."""
    print("=" * 60)
    print("🔧 STRATEGY SANDBOX - Mix & Match Trading Components")
    print("=" * 60)
    
    print("\n📚 Available Components:")
    print("   Indicators: MovingAverage, RSI")
    print("   Signals: CrossoverSignal, Custom Signals")
    print()
    print("🎯 Running Examples...\n")
    
    example_1_simple_ma_crossover()
    example_2_rsi_strategy()
    example_3_combined_strategy()
    
    print("\n" + "=" * 60)
    print("✅ All Examples Complete!")
    print("=" * 60)
    print("\n💡 Next Steps:")
    print("   1. Modify examples above")
    print("   2. Create your own indicators")
    print("   3. Build custom signal generators")
    print("   4. Test with real market data")
    print()


if __name__ == "__main__":
    main()
