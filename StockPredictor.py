import praw
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import re
import requests
import json
import yfinance as yf
import matplotlib.pyplot as plt

def analyze_reddit_sentiment(numPosts):
    # Initialize JSON files
    with open('reddit_credentials.json', 'r') as file:
        try:
            reddit_credentials = json.load(file)
            print("JSON loaded successfully:", reddit_credentials)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")

    with open('company_mapping.json', 'r') as file:
        company_mapping = json.load(file)

    with open('subreddits.txt', 'r') as file:
        subreddits = file.readlines()

    # Initialize Reddit instance
    reddit = praw.Reddit(
        client_id=reddit_credentials['client_id'],
        client_secret=reddit_credentials['client_secret'],
        user_agent=reddit_credentials['user_agent']
    )

    # Initialize sentiment analyzer
    sia = SentimentIntensityAnalyzer()
    print("Reddit API and sentiment analysis initialized!")

    # Initialize dictionary to hold sentiment scores
    ticker_sentiments = {}

    # Regex for extracting company key words, dw about how it works
    company_pattern = re.compile(r'\b(' + '|'.join(re.escape(company) for company in company_mapping.keys()) + r')\b', re.IGNORECASE)

    # Iterate over each subreddit
    count = 0
    for subreddit_name in subreddits:
        
        subreddit = reddit.subreddit(subreddit_name)

        # Fetch top posts from the subreddit
        for post in subreddit.new(limit=numPosts):

            # Analyze the post title and selftext by getting the sentiment
            content = f"{post.title} {post.selftext}"
            ticker_sentiments.update(analyze_content(content, company_pattern, company_mapping, sia, ticker_sentiments))

            # Analyze comments
            post.comments.replace_more(limit=0)
            for comment in post.comments.list():
                ticker_sentiments.update(analyze_content(comment.body, company_pattern, company_mapping, sia, ticker_sentiments))
            count+=1
            print(f"{count/(numPosts*len(subreddits))*100:.0f}% done scanning Reddit",end="\r")
            

    # Calculate average sentiment for each ticker
    average_sentiments = {ticker: sum(scores) / len(scores) for ticker, scores in ticker_sentiments.items()}

    return average_sentiments




def analyze_content(content, company_pattern, company_mapping, sia, ticker_sentiments):
    tickers = {}
    # Find all company mentions in the content
    matches = company_pattern.findall(content)
    for match in matches:
        company_name = match.lower()
        if company_name in company_mapping:
            parent_company_info = company_mapping[company_name]
            ticker = parent_company_info['ticker']
            # Perform sentiment analysis
            sentiment_score = sia.polarity_scores(content)['compound'] * 0.5
            # Update sentiment scores for the ticker
            if ticker in tickers:
                tickers[ticker].append(sentiment_score)
            else:
                tickers[ticker] = [sentiment_score]

    return tickers


def get_Mentioned_Ticks():
    tickerValues = {}
    average_sentiments = analyze_reddit_sentiment()
    for ticker, sentiment in average_sentiments.items():
        tickerValues[ticker] = sentiment
    return tickerValues


def run(stock):
    # Define the stock ticker
    ticker = stock  # Example: Apple Inc.
    detail = 3


    # Fetch historical data from January 1, 2025, to today
    stock = yf.Ticker(ticker)
    historical_data = stock.history(start="2000-01-01", end="2025-01-11")  # Update the end date as needed

    detail = round((max(historical_data["Close"]) - min(historical_data["Close"])) / 20) *0.5
    cost = [round(x/detail)*detail for x in historical_data['Close']]


    derivative = [(list(cost)[x+1]-list(cost)[x]) for x in range(len(cost)-1)]

    LOD = 10

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
    for i in range(10,1,-1):
        LOD = i
        sum += checkForMatches(combs[len(combs)-2]) * (2 ** -(10-i))
    print(sum)
    # Plot the closing pr
    #plt.plot(combs[3])
    #plt.show()
    def plot():

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
    plot

    print(derivative[-1])


