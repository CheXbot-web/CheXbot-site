import tweepy
from transformers import pipeline

with open("x_keys.txt", "r") as f:
    lines = f.readlines()
    bearer_token = lines[0].split(": ")[1].strip()
    api_key = lines[1].split(": ")[1].strip()
    api_secret = lines[2].split(": ")[1].strip()
    access_token = lines[3].split(": ")[1].strip()
    access_secret = lines[4].split(": ")[1].strip()

client_oauth = tweepy.Client(consumer_key=api_key, consumer_secret=api_secret,
                             access_token=access_token, access_token_secret=access_secret)

class FactStream(tweepy.StreamingClient):
    def on_tweet(self, tweet):
        tweet_id = tweet.id
        tweet_text = tweet.text
        classifier = pipeline("zero-shot-classification", model="distilbert-base-uncased")
        result = classifier(tweet_text, candidate_labels=["factual", "opinion"])
        label = result["labels"][0]
        reply_text = f"Checked: {label}"
        client_oauth.create_tweet(text=reply_text, in_reply_to_tweet_id=tweet_id)
        print(f"Replied to {tweet_id}: {reply_text}")

stream = FactStream(bearer_token=bearer_token)
stream.add_rules(tweepy.StreamRule("@CheXbot"))  # Listen for @CheXbot mentions
stream.filter()