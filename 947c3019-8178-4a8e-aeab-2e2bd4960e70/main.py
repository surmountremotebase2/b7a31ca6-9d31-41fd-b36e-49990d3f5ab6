from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI, EMA
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Define the ticker symbol for the asset to be traded
        self.ticker = "AAPL"

    @property
    def assets(self):
        # Specify the asset this strategy targets (AAPL in our case)
        return [self.ticker]

    @property
    def interval(self):
        # Set the interval for the data. Here, we use daily data for the analysis.
        return "1day"

    def run(self, data):
        # Initialize the allocation dictionary with 0 allocation for safety
        allocation = {self.ticker: 0}

        # Calculate the RSI and EMA values for the AAPL data
        rsi_values = RSI(self.ticker, data["ohlcv"], length=14)  # Using a 14-day period for RSI
        ema_values = EMA(self.ticker, data["ohlcv"], length=50)  # Using a 50-day period for EMA

        # Ensure we have enough data points to make a decision
        if rsi_values is not None and ema_values is not None and len(rsi_values) > 0 and len(ema_values) > 0:
            current_rsi = rsi_values[-1]
            current_price = data["ohlcv"][-1][self.ticker]["close"]
            current_ema = ema_values[-1]

            # Define the RSI thresholds for oversold and overbought conditions
            oversold_rsi_threshold = 30
            overbought_rsi_threshold = 70

            # Buy signal: RSI below oversold threshold and current price above EMA (bullish trend)
            if current_rsi < oversold_rsi_threshold and current_price > current_ema:
                allocation[self.ticker] = 1  # Allocate 100% to AAPL
                log("Buy signal identified for AAPL based on RSI and EMA criteria.")

            # Sell signal: RSI above overbought threshold or price below EMA (bearish indication)
            elif current_rsi > overbought_rsi_threshold or current_price < current_ema:
                allocation[self.ticker] = 0  # Allocate 0% to AAPL indicating a sell/exit signal
                log("Sell/Exit signal identified for AAPL based on RSI and EMA criteria.")
            else:
                # No clear signal, maintain previous allocation (could be holding or not holding)
                log("No clear trading signal for AAPL. Holding previous position.")

        else:
            # In case there's insufficient data for RSI or EMA calculation.
            log("Insufficient data to calculate RSI and EMA. No action recommended.")

        return TargetAllocation(allocation)