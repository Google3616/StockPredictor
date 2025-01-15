import yfinance as yf
import math

stock = yf.Ticker("AAPL")
historical_data = stock.history(start="2020-02-02", end="2025-01-14")
scale = 1
LOD = 400

StockPredictor("AAPL","2020-02-02")

cost = [round(x / scale) * scale for x in historical_data['Close']]
derivative = [(cost[x + 1] - cost[x]) for x in range(len(cost) - 1)]

combs = {i: derivative[i:i + LOD] for i in range(len(derivative) - LOD)}


def listDiff(lista,listb):
  diff = 0

  for index in range(len(lista)):
    diff += math.pow(2.5, abs(lista[index] - listb[index]))
  return round((2*math.pow(0.5,math.pow(round(diff/(len(lista)*0.001))*0.001,0.8)))/0.0001)*0.0001

checker = combs[12]
sum = 0
for LOD in range(LOD,2,-1):

  for index,comb in combs.items():
    c = listDiff(comb[:LOD],checker)
    if c == 0:
      pass

    sum += (c/len(combs)) * (0.5 + 1.5 * math.exp(-6 / (LOD ** 0.9) * LOD))

print(round(sum*100))
