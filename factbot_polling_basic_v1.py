import tweepy
import time
import requests
from transformers import pipeline

# Load API keys
with open("x_keys.txt", "r") as f:
    lines = f.readlines()
    bearer_token = lines[0].split(": ")[1].strip()
    api_key = lines[1].split(": ")[1].strip()
    api_secret = lines[2].split(": ")[1].strip()
    access_token = lines[3].split(": ")[1].strip()
    access_secret = lines[4].split(": ")[1].strip()
    bitly_token = lines[5].split(": ")[1].strip()

client = tweepy.Client(bearer_token=bearer_token, consumer_key=api_key, consumer_secret=api_secret,
                      access_token=access_token, access_token_secret=access_secret)

classifier = pipeline("zero-shot-classification", model="distilbert-base-uncased")
subs = {"@User123", "@Sub456"}
last_id = None
processed_replies = set()
processed_mentions = set()

# Function to shorten URL with Bitly
def shorten_url(long_url, bitly_token):
    url = "https://api-ssl.bitly.com/v4/shorten"
    headers = {"Authorization": f"Bearer {bitly_token}", "Content-Type": "application/json"}
    data = {"long_url": long_url}
    try:
        response = requests.post(url, headers=headers, json=data)
        return response.json()["link"]
    except Exception as e:
        print(f"Bitly error: {e}")
        return long_url

while True:
    try:
        query = "@CheXbot -from:CheXbot"
        tweets = client.search_recent_tweets(query=query, since_id=last_id, tweet_fields=["text", "author_id"])
        if tweets and tweets.data:
            for tweet in reversed(tweets.data):
                tweet_id = tweet.id
                if tweet_id in processed_mentions:
                    continue
                tweet_text = tweet.text
                author_id = tweet.author_id
                author = client.get_user(id=author_id).data.username
                if f"@{author}" in subs:
                    result = classifier(tweet_text, candidate_labels=["factual", "opinion"])
                    label = result["labels"][0]
                    long_url = "https://www.nasa.gov/moon-facts"
                    source_url = shorten_url(long_url, bitly_token)
                    reply_text = (f"@{author}: Checked: {label}. [Source: {source_url}] Do you agree? Reply or DM! "
                                  f"@CheXbot checks mentions every 5 minutes—thanks for your patience! Support real-time checks: bit.ly/CheXbot")
                    reply = client.create_tweet(text=reply_text, in_reply_to_tweet_id=tweet_id)
                    print(f"Replied to {tweet_id}: {reply_text}")
                    last_id = tweet_id
                    processed_mentions.add(tweet_id)

        replies = client.search_recent_tweets(query=f"to:CheXbot", tweet_fields=["in_reply_to_tweet_id", "text", "author_id"])
        if replies and replies.data:
            for reply in replies.data:
                if reply.id not in processed_replies and reply.in_reply_to_tweet_id:
                    reply_text = reply.text
                    author_id = reply.author_id
                    author = client.get_user(id=author_id).data.username
                    intent = classifier(reply_text, candidate_labels=["Agree", "Disagree", "Question", "Neutral"])["labels"][0]
                    if intent == "Disagree":
                        follow_up = f"@{author}: Interesting! Science says it’s rock, not cheese—[Source: {source_url}]. What do you think?"
                    elif intent == "Agree":
                        follow_up = f"@{author}: Glad you agree! More checks @ bit.ly/CheXbot—any other claims?"
                    elif intent == "Question":
                        follow_up = f"@{author}: Good question! Here’s more: [Source: {source_url}]. Thoughts?"
                    else:
                        follow_up = f"@{author}: Thanks for chiming in! See the source: [{source_url}]. What’s your take?"
                    client.create_tweet(text=follow_up, in_reply_to_tweet_id=reply.id)
                    print(f"Follow-up to {reply.id}: {follow_up}")
                    processed_replies.add(reply.id)

        time.sleep(300)
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(600)