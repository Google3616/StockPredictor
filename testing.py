import praw
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import re
import requests
import json
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import date

class StockPredictor:
    def __init__(self, ticker, startDate):
        self.ticker = ticker
        self.startDate = startDate

    def _derivativeToDates(self, d, dates):
        return {str(dates[i].date()): d[i] for i in range(len(d))}

    def predictStocks(self,scale=2,LOD=10,daysAhead = 1,plot=False):
        # Define the stock ticker
        detail = 3


        # Fetch historical data from January 1, 2025, to today
        stock = yf.Ticker(self.ticker)
        historical_data = stock.history(start=self.startDate, end=date.today())  # Update the end date as needed

        detail = round((max(historical_data["Close"]) - min(historical_data["Close"])) / 60) *0.5
        cost = [round(x/scale)*scale for x in historical_data['Close']]


        derivative = [(list(cost)[x+1]-list(cost)[x]) for x in range(len(cost)-1)]
        #{(date.fromisoformat(startDate)+timedelta(days=x):derivative[x]) for x in range(len(derivative))}
        derivativeDates = self._derivativeToDates(derivative,historical_data.index[1:])
        #print(derivativeDates)
        combs = {}
        for i in range(0,len(derivative)-LOD-daysAhead+1):
            combs[i] = derivative[i:i+LOD]

        def checkForMatches(l):
            sum = 0
            abssum = 0
            for date,combo in enumerate(combs.values()): 
                if combo == l and (date + daysAhead + LOD - 1) <= len(derivative):
                    sum += derivative[date+1+LOD]
                    abssum += abs(derivative[date+1+LOD])
                if daysAhead > 1:
                    derivative.append(sum)
            try:
                return(sum/abssum)
            except:
                return 0

        sum = 0
        for i in range(LOD,1,-1):
            LOD = i
            sum += checkForMatches(combs[len(combs)-2]) * (2 ** -(LOD-i))
        print((sum/(2*scale))/(1/scale))
        # Plot the closing pr
        #plt.plot(combs[3])
        #plt.show()
        if plot:
            # %% 
            plt.figure(figsize=(10, 6))
            plt.plot(historical_data.index[1:],derivative, label='Closing Price', color='blue')
            # Customize the plot
            plt.title(f'{ticker} Stock Closing Prices (2025-01-01 to Today)')
            plt.xlabel('Date')
            plt.ylabel('Closing Price (USD)')
            plt.ylim(min(derivative)-detail,max(derivative)+detail)
            plt.xticks(rotation=45)
            plt.grid(True)
            plt.legend()

            # Show the plot
            plt.tight_layout()
            plt.show()


Apple = StockPredictor(input("Stock?   "),"1970-01-01")

for day in range(1,10):
    Apple.predictStocks(3,15,day)