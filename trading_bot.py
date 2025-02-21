from lumibot.brokers import Alpaca
from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies.strategy import Strategy
from lumibot.traders import Trader
from datetime import datetime
from api_keys import * # To not git!
from alpaca_trade_api import REST
from timedelta import Timedelta
from finbert_utils import estimate_sentiment

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
        self.api = REST(key_id=API_KEY,secret_key=API_SECRET, base_url=BASE_URL)

    def position_sizing(self):
        cash = self.get_cash()
        last_price = self.get_last_price(self.symbol)
        # how much of our cash balance we use per trade. 
        # Cash at risk of 0.5 means that for each trade we 're using 50% of remaining cash
        quantity = round(cash * self.cash_at_risk/ last_price)
        return cash, last_price, quantity
    

    def get_dates(self):
        today = self.get_datetime()
        three_days_prior = today - Timedelta(days = 3)
        return today.strftime('%Y-%m-%d'), three_days_prior.strftime('%Y-%m-%d')
    def get_news(self):
        today, three_day_prior = self.get_dates()
        news = self.api.get_news(symbol=self.symbol, start = three_day_prior, end = today)
        # Get the news:
        news = [ev.__dict__["_raw"]["headline"]for ev in news ]
        return news
    
    def get_sentiments(self):
        today, three_day_prior = self.get_dates()
        news = self.api.get_news(symbol=self.symbol, start = three_day_prior, end = today)
        # Get the news:
        news = [ev.__dict__["_raw"]["headline"]for ev in news ]
        probability, sentiment = estimate_sentiment(news)
        return probability, sentiment

    def on_trading_iteration(self):
        # Method define in the Strategy part but herited.
        # Call every sleeptime
        cash, last_price, quantity = self.position_sizing()

        # Check if we have enough cash:
        if cash > last_price:
            if self.last_trade == None:
                news = self.get_news()
                print(news)
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