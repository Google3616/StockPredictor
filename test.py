import requests
from bs4 import BeautifulSoup
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import stanza
import logging
import json
import re

# Suppress Stanza logging
logging.getLogger("stanza").setLevel(logging.WARNING)

# Initialize the Stanza NLP pipeline
stanza.download('en')  # Download the English model (only needed once)
nlp = stanza.Pipeline('en')  # Initialize pipeline

# Load company ticker mapping from JSON file
def load_company_mapping(filename="company_mapping.json"):
    try:
        with open(filename, 'r') as f:
            company_mapping = json.load(f)
        return company_mapping
    except Exception as e:
        print(f"Error loading company mapping: {e}")
        return {}

# Function to search Wikipedia for the company associated with a name
def search_wikipedia_for_company(name):
    """
    Search Wikipedia for the company associated with a name.
    Args:
        name (str): The person's name.
    Returns:
        str: The associated company or a relevant summary.
    """
    url = f"https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": name,
        "srlimit": 1
    }
    response = requests.get(url, params=params)
    data = response.json()

    if "query" in data and data["query"]["search"]:
        snippet = data["query"]["search"][0]["snippet"]
        return snippet
    return "No company found."

# Function to extract the company name from the Wikipedia snippet
def extract_company_from_snippet(snippet):
    """
    Extracts the company name from the Wikipedia snippet.
    Args:
        snippet (str): The snippet containing the company information.
    Returns:
        str: The company name.
    """
    # Use a regex to find the pattern "owns the company [company name]"
    match = re.search(r"owns the company (\w+)", snippet)
    if match:
        return match.group(1)
    return None

# Function to extract names from headlines using Stanza's NER
def extract_name_with_stanza(headline):
    """
    Extracts names from a headline using stanza's Named Entity Recognition (NER).
    Args:
        headline (str): The headline text.
    Returns:
        list: A list of names found in the headline.
    """
    # Process the text
    doc = nlp(headline)

    # Extract entities labeled as PERSON
    names = [ent.text for ent in doc.entities if ent.type == "PERSON"]

    return names

# Function to find the company ticker
def find_company_ticker(company_name, company_mapping):
    """
    Find the ticker symbol for a company from the company mapping.
    Args:
        company_name (str): The company name.
        company_mapping (dict): A dictionary mapping company names to ticker symbols.
    Returns:
        str: The company ticker or None if not found.
    """
    return company_mapping.get(company_name)

# Function to scrape news articles
def scrape_news():
    # URLs for Fox News and Wall Street Journal
    urls = {
        "Fox News": "https://www.foxnews.com/",
        "Wall Street Journal": "https://www.wsj.com/"
    }

    articles = {}

    for source, url in urls.items():
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Example: Get headlines from the main page
            if source == "Fox News":
                headlines = soup.select('h3.title > a')  # Update selector as needed
            elif source == "Wall Street Journal":
                headlines = soup.select('h3.wsj-headline > a')  # Update selector as needed

            articles[source] = [headline.get_text().strip() for headline in headlines[:300]]  # Limiting to 5 headlines
        except Exception as e:
            print(f"Error fetching news from {source}: {e}")
    return articles

# Function to analyze sentiment of news articles
def analyze_news_sentiment(news_articles):
    sia = SentimentIntensityAnalyzer()
    sentiments = {}

    for source, headlines in news_articles.items():
        sentiments[source] = []
        for headline in headlines:
            score = sia.polarity_scores(headline)['compound']
            sentiments[source].append({"headline": headline, "sentiment": score})

    return sentiments

# Main function to fetch, analyze, and combine all data
def fetch_and_analyze_news_and_company_info(company_mapping):
    # Scrape news articles
    news_articles = scrape_news()

    # Analyze sentiment of news articles
    news_sentiments = analyze_news_sentiment(news_articles)

    # Dictionary to hold ticker-based sentiment scores
    ticker_sentiments = {}

    # Process each article
    for source, articles in news_articles.items():
        for article in articles:
            # Extract names from the headline
            names = extract_name_with_stanza(article)

            # Process each name
            for name in names:
                # Search for the company associated with the person
                company_info = search_wikipedia_for_company(name)
                print(f"Company Info for {name}: {company_info}")

                # Extract company name from the snippet
                company_name = extract_company_from_snippet(company_info)
                if company_name:
                    print(f"Company Name Extracted: {company_name}")
                    # Find the ticker from the company mapping
                    ticker = find_company_ticker(company_name, company_mapping)
                    if ticker:
                        print(f"Company Ticker: {ticker}")
                        # If ticker is found, add the sentiment to the ticker's list
                        if ticker not in ticker_sentiments:
                            ticker_sentiments[ticker] = []
                        sentiment_score = next(item['sentiment'] for item in news_sentiments[source] if item['headline'] == article)
                        ticker_sentiments[ticker].append(sentiment_score)

    # Display the results
    print(f"\nSentiment Scores by Ticker:")
    for ticker, sentiments in ticker_sentiments.items():
        print(f"Ticker: {ticker}")
        print(f"Sentiment Scores: {sentiments}")

# Example usage
if __name__ == "__main__":
    company_mapping = load_company_mapping()  # Load the company mapping from JSON
    fetch_and_analyze_news_and_company_info(company_mapping)
