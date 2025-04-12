print("👋 Sanity check: CheXbot_main.py actually executing...")


print("🚀 Starting CheXbot...")

# Core libraries
try:
    import openai
    import os
    import time
    import json
    import hashlib
    import logging
    import csv
    from datetime import datetime
    from urllib.parse import unquote
    print("✅ Core libraries imported")
except Exception as e:
    print("❌ Core import failed:", e)

# External libraries
try:
    from requests.exceptions import RequestException
    import requests
    import tweepy
    import wikipedia
    from transformers import pipeline
    print("✅ External libraries imported")
except Exception as e:
    print("❌ External lib import failed:", e)

# Custom/local modules
try:
    from claim_categorizer import categorize_claim
    from claim_verifier import ClaimVerifier
    from safe_verify import safe_verify
    from db import init_db, save_fact_check
    from config import OPENAI_KEY, GOOGLE_API_KEY, GOOGLE_CSE_ID, \
        CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET, BEARER_TOKEN, \
        SITE_API_URL, UPDATE_API_KEY
    print("✅ Internal modules and config loaded")
except Exception as e:
    print("❌ Custom module import failed:", e)

# Check critical keys
print("OPENAI_KEY:", "✅" if OPENAI_KEY else "❌ MISSING")
print("UPDATE_API_KEY:", "✅" if UPDATE_API_KEY else "❌ MISSING")
print("SITE_API_URL:", SITE_API_URL if SITE_API_URL else "❌ MISSING")

# Set fixed CheXbot ID
CHEXBOT_USER_ID = 1901717905299161088

# Initialize DB
try:
    init_db()
    print("✅ DB initialized")
except Exception as e:
    print("❌ DB init failed:", e)

print("✅ Script reached main block")

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

@retry_on_failure(max_retries=3, delay=5)
def search_recent_tweets(client, query, since_id=None, tweet_fields=None, max_results=None):
    return client.search_recent_tweets(query=query, since_id=since_id, tweet_fields=tweet_fields, max_results=max_results)

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

# === Dry Run and Logging ===
DRY_RUN = False
LOG_FILE = "failed_replies.log"

# === Subscriber List ===
SUBSCRIBERS = ["@User123", "@Sub456", "@CheXbot67888"]

# === Load/Save Helpers ===
def load_processed_set(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return set(int(line.strip()) for line in f if line.strip())
    return set()

def save_processed_set(data_set, filename):
    with open(filename, "w") as f:
        for item in data_set:
            f.write(f"{item}\n")

processed_replies = load_processed_set("processed_replies.txt")
processed_mentions = load_processed_set("processed_mentions.txt")
processed_conversations = load_processed_set("processed_conversations.txt")

def get_latest_processed_mention_id(mention_set):
    return max(mention_set) if mention_set else None

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

def override_claim_classification(tweet_text, label):
    if "moon" in tweet_text.lower() and ("cheese" in tweet_text.lower() or "cheddar" in tweet_text.lower()):
        return "FalseClaim"
    return label

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

def log_failed_reply(tweet_id, author, claim, reason):
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps({
            "tweet_id": tweet_id,
            "author": author,
            "claim": claim,
            "reason": str(reason)
        }) + "\n")

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
       
# === Main Bot Loop ===
def check_mentions():
    global last_seen_id
    me = CHEXBOT_USER_ID

    mentions = client.get_users_mentions(
        id=me,
        since_id=last_seen_id,
        tweet_fields=["author_id", "created_at"],
        expansions=["author_id"]
    )

    author_map = {}
    if mentions.includes and "users" in mentions.includes:
        for user in mentions.includes["users"]:
            author_map[user.id] = user.username

    for tweet in reversed(mentions.data or []):
        author = author_map.get(tweet.author_id, "unknown")
        if author.lower() == "chexbot":
            continue

        if f"@{author}" not in SUBSCRIBERS:
            print(f"User @{author} is not a subscriber. Skipping.")
            continue

        if tweet.in_reply_to_user_id:
            parent = client.get_tweet(id=tweet.in_reply_to_status_id, tweet_fields=["text"])
            claim = parent.data.text
        elif hasattr(tweet, "referenced_tweets") and tweet.referenced_tweets:
            quoted_tweet = tweet.referenced_tweets[0]
            quoted = client.get_tweet(id=quoted_tweet.id, tweet_fields=["text"])
            claim = quoted.data.text
        else:
            claim = tweet.text.replace("@CheXbot", "").strip()

        claim = unquote(claim)
        import hashlib
        claim_id = hashlib.sha256(claim.encode()).hexdigest()

        category = categorize_claim(claim)
        print(f"Detected claim category: {category}")

        result = safe_verify(claim, verifier)

        reply_text = verifier.format_result(result, claim_id)
        reply_text += f"\n\nCategory: {category}\nDo you agree or disagree?"

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

if __name__ == "__main__":
    print("✅ Script reached main block")
    while True:
        print("🔄 Loop running. Calling check_mentions()...")
        check_mentions()
        time.sleep(120)