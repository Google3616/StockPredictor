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

    def predictStocks(self,plot=False):
        # Define the stock ticker
        detail = 3


        # Fetch historical data from January 1, 2025, to today
        stock = yf.Ticker(self.ticker)
        historical_data = stock.history(start=self.startDate, end=date.today())  # Update the end date as needed

        detail = round((max(historical_data["Close"]) - min(historical_data["Close"])) / 60) *0.5
        cost = [round(x/detail)*detail for x in historical_data['Close']]


        derivative = [(list(cost)[x+1]-list(cost)[x]) for x in range(len(cost)-1)]
        #{(date.fromisoformat(startDate)+timedelta(days=x):derivative[x]) for x in range(len(derivative))}
        derivativeDates = self._derivativeToDates(derivative,historical_data.index[1:])
        #print(derivativeDates)
        LOD = 20

        combs = {}
        for i in range(0,len(derivative)-LOD):
            combs[i] = derivative[i:i+LOD]

        def checkForMatches(l):
            sum = 0
            abssum = 0
            for date,combo in enumerate(combs.values()): 
                if combo == l:
                    sum += derivative[date+1+LOD]
                    abssum += abs(derivative[date+1+LOD])
            try:
                return(sum/abssum)
            except:
                return 0

        sum = 0
        for i in range(20,1,-1):
            LOD = i
            sum += checkForMatches(combs[len(combs)-2]) * (1.2 ** -(10-i))
        print(sum)
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


Apple = StockPredictor(input("Stock?   "),"2000-01-01")

Apple.predictStocks()