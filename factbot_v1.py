import tweepy
import torch
from transformers import pipeline

# Load keys from file (optional—keep secure!)
with open("x_keys.txt", "r") as f:
    lines = f.readlines()
    bearer_token = lines[0].split(": ")[1].strip()
    api_key = lines[1].split(": ")[1].strip()
    api_secret = lines[2].split(": ")[1].strip()
    access_token = lines[3].split(": ")[1].strip()
    access_secret = lines[4].split(": ")[1].strip()

# v2 Bearer for fetch
client_bearer = tweepy.Client(bearer_token=bearer_token)

# v2 OAuth for post
client_oauth = tweepy.Client(
    consumer_key=api_key,
    consumer_secret=api_secret,
    access_token=access_token,
    access_token_secret=access_secret
)

# Test tweet (replace with your ID)
tweet_id = "1904970465816232311"
tweet = client_bearer.get_tweet(tweet_id, tweet_fields=["text"])
tweet_text = tweet.data["text"]
print(f"Tweet: {tweet_text}")

# Classify claim
torch.backends.mkldnn.enabled = True
classifier = pipeline("zero-shot-classification", model="distilbert-base-uncased")
result = classifier(tweet_text, candidate_labels=["factual", "opinion"])
label = result["labels"][0]
print(f"Verdict: {label}")

# Reply on X
reply_text = f"Checked: {label}"
client_oauth.create_tweet(text=reply_text, in_reply_to_tweet_id=tweet_id)
print(f"Replied: {reply_text}")