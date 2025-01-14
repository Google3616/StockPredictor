import yfinance as yf
from datetime import date,timedelta
import math
def su(num):
    sum = 0
    for i in range(15):
        sum += round(math.pow(num,-i)/0.01)*0.01
    return sum
class StockPredictor:
    def __init__(self, ticker, startDate):
        self.ticker = ticker
        self.startDate = startDate
        self.derivatives = {}

    def _derivativeToDates(self, d, dates):
        return {str(dates[i].date()): d[i] for i in range(len(d))}

    def _checkForMatches(self, l, combs, daysAhead, LOD, derivative):
        total_sum = 0
        total_abs_sum = 0
        for date_idx, combo in enumerate(combs.values()):
            if combo == l and (date_idx + daysAhead + LOD - 1) < len(derivative):
                total_sum += derivative[date_idx + LOD + daysAhead - 1]
                total_abs_sum += abs(derivative[date_idx + LOD + daysAhead - 1])
        try:
            return total_sum / total_abs_sum if total_abs_sum != 0 else 0
        except ZeroDivisionError:
            print("0 div")
            return 0

    def predictStocks(self, scale=2, LOD=10, daysAhead=1, date=date.today(),control = 2):
        stock = yf.Ticker(self.ticker)
        historical_data = stock.history(start=self.startDate, end=date)

        if historical_data.empty:
            raise ValueError("No historical data available for the given ticker and date range.")

        cost = [round(x / scale) * scale for x in historical_data['Close']]
        derivative = [(cost[x + 1] - cost[x]) for x in range(len(cost) - 1)]
        self.derivatives = self._derivativeToDates(derivative, historical_data.index[1:])
        #print(self.derivatives)
        combs = {i: derivative[i:i + LOD] for i in range(len(derivative) - LOD)}

        if len(derivative) < LOD + daysAhead:
            raise ValueError("Insufficient data for the given LOD and daysAhead values.")
        try:

            total_sum = 0
            for i in range(LOD, 1, -1):
                if len(combs) < 2:
                    break  # Ensure there are enough combinations to work with
                total_sum += self._checkForMatches(
                    combs[len(combs) - 2], combs, daysAhead, i, derivative
                ) * (control ** -(LOD - i))
            return (total_sum / (su(control) * scale)) / (1 / scale)
        except:
            print("error")


accuracy = 0
import random

def sign(num):
     if num < 0:
          return -1
     if num > 0:
          return 1
     return 0

import random

def test_stock_predictor(ticker, start_date, end_date, scale=1, LOD=10, days_ahead=1, test_cases=10,count=2):
    # Initialize StockPredictor
    predictor = StockPredictor(ticker, start_date)
    
    # Fetch historical data to determine valid date range
    stock = yf.Ticker(ticker)
    historical_data = stock.history(start=start_date, end=end_date)
    
    if historical_data.empty:
        print(f"No historical data found for {ticker} from {start_date} to {end_date}.")
        return

    valid_dates = historical_data.index  # Valid dates for prediction
    accuracy = 0
    total_attempts = 0
    results = []

    if len(valid_dates) <= LOD + days_ahead:
        print("Not enough data to perform tests with the given LOD and daysAhead.")
        return

    for _ in range(test_cases):

            # Pick a random date ensuring it has enough data for LOD and daysAhead
            max_index = len(valid_dates) - days_ahead - 1
            random_index = random.randint(LOD, max_index)
            random_date = valid_dates[random_index].date()
            random_date_str = random_date.strftime("%Y-%m-%d")
            next_day = random_date + timedelta(days=2)
            next_day_str = next_day.strftime("%Y-%m-%d")

            # Run prediction for the adjusted date
            predicted_change = predictor.predictStocks(scale=scale, LOD=LOD, daysAhead=days_ahead, date=next_day,control=count)
            
            # Get the actual derivative value for the random date
            actual_change = predictor.derivatives[random_date_str]
            if actual_change is None:
                continue  # Skip if the derivative is missing
            
            # Compare predicted and actual values
            predicted_sign = sign(predicted_change)
            actual_sign = sign(actual_change)
            is_correct = predicted_sign == actual_sign
            accuracy += 1 if is_correct else 0
            total_attempts += 1
            
            # Log results
            results.append({
                "date": random_date_str,
                "actual_change": actual_change,
                "predicted_change": predicted_change,
                "correct": is_correct
            })
        

    
    # Calculate and print overall accuracy
    accuracy_percentage = (accuracy / total_attempts) * 100 if total_attempts > 0 else 0
    print(f"Test Results for {ticker}:")
    print(f"Accuracy: {accuracy_percentage:.2f}% ({accuracy}/{total_attempts})")
    
    # Print detailed results

print(StockPredictor("NVDA","2010-01-01").predictStocks(LOD=15,control=2))
test_stock_predictor("NVDA","2010-01-01","2025-01-01",test_cases=50,LOD=8,count=1.8)