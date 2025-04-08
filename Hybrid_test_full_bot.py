import tweepy
import torch
from transformers import pipeline

# v2 Bearer for fetch
client_bearer = tweepy.Client(bearer_token="AAAAAAAAAAAAAAAAAAAAAO5Y0AEAAAAAvTo84Cbpkom3qJmU7wrpi4%2FC2N8%3DNhzUZFG3uWYCotRmHWc5X3xmtpHYJkCCNxXtb9J3I9DrneaxQR")

# v2 OAuth for post
client_oauth = tweepy.Client(
    consumer_key="bO74B5gNnaLfs0aYUZYxj70F5",
    consumer_secret="ZajtxqKqS3EniWYwvqDV2GDccBVALUKlRAX82OfJaeRrSpW2z4",
    access_token="1901717905299161088-57HvrmQz3iMdBUKWf0Pvhsgnoer398",
    access_token_secret="UiFhMXNWtaQclLxkOXUbJJ06gQAg5UdJhrBKsbGMBlpWk"
)

# Test tweet
tweet_id = "1904001460037394936"  # Your test ID
tweet = client_bearer.get_tweet(tweet_id, tweet_fields=["text"])
tweet_text = tweet.data["text"]
print(f"Tweet: {tweet_text}")

# Classify claim
torch.backends.mkldnn.enabled = True
classifier = pipeline("zero-shot-classification", model="distilbert-base-uncased")
result = classifier(tweet_text, candidate_labels=["factual", "opinion"])
label = result["labels"][0]
print(f"Verdict: {label}")

# Reply on X (v2 OAuth)
reply_text = f"Checked: {label}"
client_oauth.create_tweet(text=reply_text, in_reply_to_tweet_id=tweet_id)
print(f"Replied: {reply_text}")