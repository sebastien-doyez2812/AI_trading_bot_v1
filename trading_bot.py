from lumibot.brokers import Alpaca
from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies.strategy import Strategy
from lumibot.traders import Trader
from datetime import datetime
from api_keys import * # To not git!

ALPACA_CREDS = {
    "API_KEY" : API_KEY,
    "API_SECRET": API_SECRET,
    "PAPER": True
}




class MLTrader(Strategy):
    def initialize(self, symbol:str="SPY"):
        self.symbol = symbol
        self.sleeptime = "24H"
        self.last_trade = None


    def on_trading_iteration(self):
        # Method define in the Strategy part but herited.
        # Call every sleeptime
        if self.last_trade == None:
            order = self.create_order(
                self.symbol,
                1,
                "buy",
                type="market"
            )
            self.submit_order(order)
            self.last_trade = "buy"


start_date = datetime(2023,12,15)
end_date= datetime(2023,12,31)


broker = Alpaca(ALPACA_CREDS)
strategy = MLTrader(name='MLstrat', broker=broker, parameters = {})
strategy.backtest(YahooDataBacktesting, start_date, end_date, parameters={})