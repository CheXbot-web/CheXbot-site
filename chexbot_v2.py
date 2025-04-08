# chexbot.py

import openai
import tweepy
import time
import requests
from transformers import pipeline
import os
import logging
import csv
from datetime import datetime
from requests.exceptions import RequestException
import wikipedia  # Added for evidence retrieval
from claim_categorizer import categorize_claim
from claim_verifier import ClaimVerifier
from safe_verify import safe_verify
import json
from urllib.parse import unquote

from db import init_db, save_fact_check
init_db()

from config import OPENAI_KEY, GOOGLE_API_KEY, GOOGLE_CSE_ID, \
    CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET, BEARER_TOKEN


# === Setup Tweepy Auth ===
auth = tweepy.OAuth1UserHandler(
    CONSUMER_KEY,
    CONSUMER_SECRET,
    ACCESS_TOKEN,
    ACCESS_SECRET
)
api = tweepy.API(auth)

# Setup Tweepy v2 Client with user context for read/write
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_SECRET
)

# === Setup Verifier ===
verifier = ClaimVerifier(
    use_gpt=True if OPENAI_KEY else False,
    openai_key=OPENAI_KEY,
    google_api_key=GOOGLE_API_KEY,
    google_cse_id=GOOGLE_CSE_ID
)



# Retry decorator for API calls
def retry_on_failure(max_retries=3, delay=5):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (RequestException, tweepy.TweepyException, ConnectionResetError) as e:
                    if attempt == max_retries - 1:
                        raise e
                    print(f"API call failed: {e}. Retrying in {delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(delay)
        return wrapper
    return decorator

# Apply retry to API calls
@retry_on_failure(max_retries=3, delay=5)
def search_recent_tweets(client, query, since_id=None, tweet_fields=None,max_results=None):
    return client.search_recent_tweets(query=query, since_id=since_id, tweet_fields=tweet_fields,max_results=max_results)

@retry_on_failure(max_retries=3, delay=5)
def get_users_tweets(client, user_id, tweet_fields=None, max_results=None):
    return client.get_users_tweets(id=user_id, tweet_fields=tweet_fields, max_results=max_results)

@retry_on_failure(max_retries=3, delay=5)
def get_tweet(client, tweet_id, tweet_fields=None):
    return client.get_tweet(id=tweet_id, tweet_fields=tweet_fields)

@retry_on_failure(max_retries=3, delay=5)
def get_user(client, user_id):
    return client.get_user(id=user_id)

@retry_on_failure(max_retries=3, delay=5)
def get_me(client):
    return client.get_me()

@retry_on_failure(max_retries=3, delay=5)
def create_tweet(client, text, in_reply_to_tweet_id=None):
    return client.create_tweet(text=text, in_reply_to_tweet_id=in_reply_to_tweet_id)

# Load processed replies from file
def load_processed_replies(filename="processed_replies.txt"):
    try:
        if os.path.exists(filename):
            with open(filename, "r") as f:
                replies = set(int(line.strip()) for line in f if line.strip())
                print(f"Loaded {len(replies)} processed replies from {filename}")
                return replies
        print(f"No processed_replies file found at {filename}. Starting with empty set.")
        return set()
    except Exception as e:
        print(f"Error loading processed_replies: {e}")
        return set()

# Save processed replies to file
def save_processed_replies(processed_replies, filename="processed_replies.txt"):
    try:
        with open(filename, "w") as f:
            for reply_id in processed_replies:
                f.write(f"{reply_id}\n")
        print(f"Saved {len(processed_replies)} processed replies to {filename}")
    except Exception as e:
        print(f"Error saving processed_replies: {e}")

# Load processed mentions from file
def load_processed_mentions(filename="processed_mentions.txt"):
    try:
        if os.path.exists(filename):
            with open(filename, "r") as f:
                mentions = set(int(line.strip()) for line in f if line.strip())
                print(f"Loaded {len(mentions)} processed mentions from {filename}")
                return mentions
        print(f"No processed_mentions file found at {filename}. Starting with empty set.")
        return set()
    except Exception as e:
        print(f"Error loading processed_mentions: {e}")
        return set()
    
def get_latest_processed_mention_id(mention_set):
    if not mention_set:
        return None
    return max(mention_set)
    

# Save processed mentions to file
def save_processed_mentions(processed_mentions, filename="processed_mentions.txt"):
    try:
        with open(filename, "w") as f:
            for mention_id in processed_mentions:
                f.write(f"{mention_id}\n")
        print(f"Saved {len(processed_mentions)} processed mentions to {filename}")
    except Exception as e:
        print(f"Error saving processed_mentions: {e}")

# Load processed conversations from file
def load_processed_conversations(filename="processed_conversations.txt"):
    try:
        if os.path.exists(filename):
            with open(filename, "r") as f:
                conversations = set(int(line.strip()) for line in f if line.strip())
                print(f"Loaded {len(conversations)} processed conversations from {filename}")
                return conversations
        print(f"No processed_conversations file found at {filename}. Starting with empty set.")
        return set()
    except Exception as e:
        print(f"Error loading processed_conversations: {e}")
        return set()

# Save processed conversations to file
def save_processed_conversations(processed_conversations, filename="processed_conversations.txt"):
    try:
        with open(filename, "w") as f:
            for conv_id in processed_conversations:
                f.write(f"{conv_id}\n")
        print(f"Saved {len(processed_conversations)} processed conversations to {filename}")
    except Exception as e:
        print(f"Error saving processed_conversations: {e}")

# Log user data for fine-tuning
def log_user_data(text, label, data_type, filename="user_data.csv"):
    try:
        file_exists = os.path.exists(filename)
        with open(filename, "a", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["text", "label", "data_type", "timestamp"])
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow([text, label, data_type, timestamp])
        print(f"Logged {data_type} data: {text} -> {label}")
    except Exception as e:
        print(f"Error logging user data: {e}")

# Rule-based override for known false claims
def override_claim_classification(tweet_text, label):
    if "moon" in tweet_text.lower() and ("cheese" in tweet_text.lower() or "cheddar" in tweet_text.lower()):
        return "FalseClaim"
    return label


classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
#subs = {"@User123", "@Sub456", "@CheXbot67888"}
# === Subscriber List ===
SUBSCRIBERS = ["@User123", "@Sub456", "@CheXbot67888"]
processed_replies = load_processed_replies()
processed_mentions = load_processed_mentions()
# === Main Bot Loop ===
last_seen_id = None  # Replace with persistent storage later

processed_conversations = load_processed_conversations()
daily_cycles = 0
max_daily_cycles = 10  # Temporary increase for testing
read_count = 0
post_count = 0

# Before the loop starts:
author_cache = {}
fetched_ids = []

def shorten_url(long_url, BITLY_TOKEN):
    url = "https://api-ssl.bitly.com/v4/shorten"
    headers = {"Authorization": f"Bearer {BITLY_TOKEN}", "Content-Type": "application/json"}
    data = {"long_url": long_url}
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["link"]
    except Exception as e:
        print(f"Bitly error: {e}")
        return long_url



SEEN_FILE = "last_seen.json"

def load_last_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return json.load(f).get("last_seen_id")
    return None

def save_last_seen(tweet_id):
    with open(SEEN_FILE, "w") as f:
        json.dump({"last_seen_id": tweet_id}, f)

last_seen_id = load_last_seen()

def check_mentions():
    global last_seen_id

    # Get CheXbot's user ID
    me = client.get_user(username="CheXbot").data.id

    # Get recent mentions using Twitter API v2
    mentions = client.get_users_mentions(
        id=me,
        since_id=last_seen_id,
        tweet_fields=["author_id", "created_at"],
        expansions=["author_id"]
    )

    # Build a cache of author IDs → usernames
    author_map = {}
    if mentions.includes and "users" in mentions.includes:
        for user in mentions.includes["users"]:
            author_map[user.id] = user.username

    for tweet in reversed(mentions.data or []):
        author = author_map.get(tweet.author_id, "unknown")
        if author.lower() == "chexbot":
            continue  # Skip self

        if f"@{author}" not in SUBSCRIBERS:
            print(f"User @{author} is not a subscriber. Skipping.")
            continue

        # Determine the claim source
        if tweet.in_reply_to_user_id:
            parent = client.get_tweet(id=tweet.in_reply_to_status_id, tweet_fields=["text"])
            claim = parent.data.text
        elif hasattr(tweet, "referenced_tweets") and tweet.referenced_tweets:
            quoted_tweet = tweet.referenced_tweets[0]
            quoted = client.get_tweet(id=quoted_tweet.id, tweet_fields=["text"])
            claim = quoted.data.text
        else:
            claim = tweet.text.replace("@CheXbot", "").strip()
        import hashlib
        claim_id = hashlib.md5(claim.encode()).hexdigest()


        # Unshorten any percent-encoded URLs or hashtags
        claim = unquote(claim)

        # Categorize the claim
        category = categorize_claim(claim)
        print(f"Detected claim category: {category}")

        # Run claim through verifier
        result = safe_verify(claim, verifier)

        # Format reply
        reply_text = verifier.format_result(result, claim_id)
        reply_text += f"\n\nCategory: {category}\nDo you agree or disagree?"

        # Send reply
        try:
            if DRY_RUN:
                print(f"[DRY RUN] Would reply to @{author}:\n{reply_text}\n")
                reply_id = "dry_run"
            else:
                reply = client.create_tweet(
                    text=reply_text,
                    in_reply_to_tweet_id=tweet.id
                )
                reply_id = reply.data["id"]

            # Save to DB
            save_fact_check(
                original_tweet_id=tweet.id,
                reply_id=reply_id,
                username=author,
                claim=claim,
                verdict=result["verdict"],
                confidence=result["confidence"]
            )

            last_seen_id = tweet.id
            save_last_seen(tweet.id)

        except Exception as e:
            print(f"Failed to reply: {e}")
            log_failed_reply(tweet.id, author, claim, e)

# === Logging and Mode ===
DRY_RUN = False  # Set to True to simulate replies without posting
LOG_FILE = "failed_replies.log"

def log_failed_reply(tweet_id, author, claim, reason):
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps({
            "tweet_id": tweet_id,
            "author": author,
            "claim": claim,
            "reason": str(reason)
        }) + "\n")
            
# === Run Loop ===
if __name__ == "__main__":
    while True:
        check_mentions()
        time.sleep(120)



