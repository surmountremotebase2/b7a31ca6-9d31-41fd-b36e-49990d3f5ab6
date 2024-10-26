from surmount.base_class import Strategy, TargetAllocation
from surmount.data import InstitutionalOwnership, InsiderTrading, SocialSentiment

class TradingStrategy(Strategy):
    def __init__(self):
        # Placeholder stock tickers for sustainable tech, AI, and energy sectors
        self.tickers = ["TSLA", "NVDA", "ENPH", "PLTR"]  # Example companies
        self.data_list = [InstitutionalOwnership(ticker) for ticker in self.tickers]
        self.data_list += [InsiderTrading(ticker) for ticker in self.tickers]
        self.data_list += [SocialSentiment(ticker) for ticker in self.tickers]

    @property
    def interval(self):
        return "1day"  # Daily analysis

    @property
    def assets(self):
        return self.tickers

    def run(self, data):
        allocation_dict = {}
        
        # Start with equal allocation as a base, then adjust based on signals
        initial_allocation = 1 / len(self.tickers)  # Simplistic equal allocation
        
        for ticker in self.tickers:
            positive_signals = 0
            
            # Check for institutional ownership trend
            institutional_data = data[("institutional_ownership", ticker)]
            if institutional_data and institutional_data[-1]["ownershipPercentChange"] > 0:
                positive_signals += 1

            # Check for insider buying signals (no insider sales recently)
            insider_data = data[("insider_trading", ticker)]
            if insider_data and not any(item["transactionType"].startswith("S") for item in insider_data):
                positive_signals += 1

            # Check social sentiment
            sentiment_data = data[("social_sentiment", ticker)]
            if sentiment_data and sentiment_data[-1]["stocktwitsSentiment"] > 0.5:
                positive_signals += 1
            
            # Adjust allocation based on the number of positive signals
            if positive_signals < 2:
                # Considered higher risk or less confidence, reduce allocation
                allocation_dict[ticker] = initial_allocation / 2
            else:
                # Stronger confidence, increase allocation
                allocation_dict[ticker] = initial_allocation * 1.5  # Increase by 50%

        # Ensure total allocation does not exceed 1
        total_allocation = sum(allocation_dict.values())
        normalized_allocation_dict = {ticker: allocation / total_allocation for ticker, allocation in allocation_dict.items()}

        return TargetAllocation(normalized_allocation_dict)