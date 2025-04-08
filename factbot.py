import tweepy
import torch
from transformers import pipeline

# X API v2 setup
client = tweepy.Client(
    consumer_key="pxrwe3CARWTbSE5e9pxtKGEVQ",
    consumer_secret="tPkVU4km6z0YDk1D2V02FxRmhTMJDgzqyarhVoOEbYBF9eQuRA",
    access_token="1901717905299161088-Ub4zKyf2DYeixnNS4vi2EeW6J8PPcu",
    access_token_secret="lAeXkn1fj3JL4OIkxc36dbAu7XarNwwlPKDsm7KnIBHrG"
)

# Test tweet
tweet_id = "1904970465816232311"  # e.g., "1901717905299161088"
tweet = client.get_tweet(tweet_id, tweet_fields=["text"])  # v2 call
tweet_text = tweet.data["text"]  # v2 response format
print(f"Tweet: {tweet_text}")

# Classify claim
torch.backends.mkldnn.enabled = True
classifier = pipeline("zero-shot-classification", model="distilbert-base-uncased")
result = classifier(tweet_text, candidate_labels=["factual", "opinion"])
label = result["labels"][0]
print(f"Verdict: {label}")

# Web check (disabled for now)
"""
query = f"{tweet_text} site:*.gov site:*.org -inurl:signup"
url = f"https://serpapi.com/search?api_key=YOUR_SERPAPI_KEY&q={query}"
response = requests.get(url).json()
top_result = response["organic_results"][0]["link"]
page = requests.get(top_result)
soup = BeautifulSoup(page.content, "html.parser")
text = soup.get_text()
verdict = "True" if tweet_text.lower() in text.lower() else "False (check source)"
print(f"Web check: {verdict}, Source: {top_result}")
"""

# Reply on X (v2)
reply_text = f"Checked: {label}"
client.create_tweet(text=reply_text, in_reply_to_tweet_id=tweet_id)
print(f"Replied: {reply_text}")