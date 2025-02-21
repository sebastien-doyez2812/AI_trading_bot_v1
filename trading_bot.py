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

    def initialize(self, symbol:str="SPY", cash_at_risk:float= 0.5):
        # cash at risk is 
        self.symbol = symbol
        self.sleeptime = "24H"
        self.last_trade = None
        self.cash_at_risk = cash_at_risk

    def position_sizing(self):
        cash = self.get_cash()
        last_price = self.get_last_price(self.symbol)
        # how much of our cash balance we use per trade. 
        # Cash at risk of 0.5 means that for each trade we 're using 50% of remaining cash
        quantity = round(cash * self.cash_at_risk/ last_price)
        return cash, last_price, quantity
    
    def on_trading_iteration(self):
        # Method define in the Strategy part but herited.
        # Call every sleeptime
        cash, last_price, quantity = self.position_sizing()

        # Check if we have enough cash:
        if cash > last_price:
            if self.last_trade == None:
                # Backet: if the share loss to much (>5%): sell
                # we the share gain too muh sell
                order = self.create_order(
                    self.symbol,
                    quantity,
                    "buy",
                    type="bracket",
                    take_profit_price = last_price*1.2,
                    stop_loss_price = last_price* 0.95
                )
                self.submit_order(order)
                self.last_trade = "buy"


start_date = datetime(2023,12,15)
end_date= datetime(2023,12,31)


broker = Alpaca(ALPACA_CREDS)
strategy = MLTrader(name='MLstrat', broker=broker, parameters = {"symbol": "SPY", "cash_at_risk":0.5})
strategy.backtest(YahooDataBacktesting, start_date, end_date, parameters={})