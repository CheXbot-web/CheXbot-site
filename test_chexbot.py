# chexbot.py
import tweepy
import time
import requests
from transformers import pipeline
import os
import logging
import csv
from datetime import datetime
from requests.exceptions import RequestException

# Suppress transformers warnings
logging.getLogger("transformers").setLevel(logging.ERROR)

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
def search_recent_tweets(client, query, since_id=None, tweet_fields=None):
    return client.search_recent_tweets(query=query, since_id=since_id, tweet_fields=tweet_fields)

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

with open("x_keys.txt", "r") as f:
    lines = f.readlines()
    bearer_token = lines[0].split("= ")[1].strip()
    api_key = lines[1].split("= ")[1].strip()
    api_secret = lines[2].split("= ")[1].strip()
    access_token = lines[3].split("= ")[1].strip()
    access_secret = lines[4].split("= ")[1].strip()
    bitly_token = lines[5].split("= ")[1].strip()

client = tweepy.Client(bearer_token=bearer_token, consumer_key=api_key, consumer_secret=api_secret,
                      access_token=access_token, access_token_secret=access_secret)

classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
subs = {"@User123", "@Sub456", "@CheXbot67888"}
last_id = None
processed_replies = load_processed_replies()
processed_mentions = load_processed_mentions()
processed_conversations = load_processed_conversations()
daily_cycles = 0
max_daily_cycles = 10  # Temporary increase for testing
read_count = 0
post_count = 0

def shorten_url(long_url, bitly_token):
    url = "https://api-ssl.bitly.com/v4/shorten"
    headers = {"Authorization": f"Bearer {bitly_token}", "Content-Type": "application/json"}
    data = {"long_url": long_url}
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["link"]
    except Exception as e:
        print(f"Bitly error: {e}")
        return long_url

while True:
    try:
        query = "@CheXbot -from:CheXbot"
        tweets = search_recent_tweets(client, query, since_id=last_id, tweet_fields=["text", "author_id", "conversation_id"])
        read_count += 1
        if tweets and tweets.data:
            for tweet in reversed(tweets.data):
                if daily_cycles >= max_daily_cycles:
                    print("Daily cycle limit reached within mention loop. Breaking...")
                    break
                tweet_id = tweet.id
                last_id = max(last_id or 0, tweet_id)
                if tweet_id in processed_mentions:
                    continue
                tweet_text = tweet.text
                author_id = tweet.author_id
                author = get_user(client, author_id).data.username
                read_count += 1
                if f"@{author}" in subs:
                    start_time = time.time()
                    result = classifier(tweet_text, candidate_labels=["TrueClaim", "FalseClaim"])
                    inference_time = time.time() - start_time
                    print(f"Claim classification inference time: {inference_time:.2f} seconds")
                    label = result["labels"][0]
                    label = override_claim_classification(tweet_text, label)
                    log_user_data(tweet_text, label, "claim")
                    long_url = "https://www.nasa.gov/moon-facts"
                    source_url = shorten_url(long_url, bitly_token)
                    reply_text = (f"@{author}: Checked: {label}. [Source: {source_url}] Do you agree? Reply to this tweet with @CheXbot in your message! "
                                  f"@CheXbot checks mentions every 10 minutes—thanks for your patience! Support real-time checks: bit.ly/CheXbot")
                    try:
                        reply = create_tweet(client, reply_text, in_reply_to_tweet_id=tweet_id)
                        post_count += 1
                        print(f"Replied to {tweet_id}: {reply_text}")
                        processed_mentions.add(tweet_id)
                        save_processed_mentions(processed_mentions)
                        processed_conversations.add(tweet.conversation_id)
                        save_processed_conversations(processed_conversations)
                        daily_cycles += 1
                    except tweepy.errors.Forbidden as e:
                        if "duplicate content" in str(e).lower():
                            print(f"Duplicate content error for tweet {tweet_id}: {e}. Skipping this reply.")
                        else:
                            raise e

        # Fetch replies to @CheXbot's recent tweets
        my_tweets = get_users_tweets(client, client.get_me().data.id, tweet_fields=["conversation_id"], max_results=10)
        read_count += 1
        if my_tweets and my_tweets.data:
            for my_tweet in my_tweets.data:
                conversation_id = my_tweet.conversation_id
                if conversation_id in processed_conversations:
                    replies = search_recent_tweets(client, f"conversation_id:{conversation_id} -from:CheXbot", tweet_fields=["referenced_tweets", "text", "author_id", "in_reply_to_user_id"])
                    read_count += 1
                    if replies and replies.data:
                        for reply in replies.data:
                            if reply.id not in processed_replies:
                                in_reply_to_tweet_id = None
                                in_reply_to_user_id = getattr(reply, "in_reply_to_user_id", None)
                                if reply.referenced_tweets:
                                    for ref_tweet in reply.referenced_tweets:
                                        if ref_tweet.type == "replied_to":
                                            in_reply_to_tweet_id = ref_tweet.id
                                            break
                                if in_reply_to_tweet_id and in_reply_to_user_id:
                                    parent_tweet = get_tweet(client, in_reply_to_tweet_id, tweet_fields=["author_id"]).data
                                    read_count += 1
                                    my_user_id = get_me(client).data.id
                                    read_count += 1
                                    if parent_tweet and parent_tweet.author_id == my_user_id and in_reply_to_user_id == my_user_id:
                                        original_tweet = get_tweet(client, in_reply_to_tweet_id, tweet_fields=["text"]).data
                                        read_count += 1
                                        original_claim = original_tweet.text if original_tweet else "the claim"
                                        original_claim = original_claim[:50] + "..." if len(original_claim) > 50 else original_claim
                                        timestamp = time.strftime("%H:%M:%S")
                                        reply_text = reply.text
                                        author_id = reply.author_id
                                        author = get_user(client, author_id).data.username
                                        read_count += 1
                                        start_time = time.time()
                                        intent_result = classifier(reply_text, candidate_labels=["UserAgrees", "UserDisagrees", "UserQuestions", "UserNeutral"])
                                        inference_time = time.time() - start_time
                                        print(f"Intent classification inference time: {inference_time:.2f} seconds")
                                        intent = intent_result["labels"][0]
                                        print(f"Classified reply '{reply_text}' as {intent} with scores: {intent_result['scores']}")
                                        log_user_data(reply_text, intent, "reply")
                                        long_url = "https://www.nasa.gov/moon-facts"
                                        source_url = shorten_url(long_url, bitly_token)
                                        if intent == "UserDisagrees":
                                            follow_up = f"@{author}: Re: '{original_claim}' - Science says it’s rock, not cheese—[Source: {source_url}]. Thoughts? [{timestamp}]"
                                        elif intent == "UserAgrees":
                                            follow_up = f"@{author}: Re: '{original_claim}' - Glad you agree! More checks @ bit.ly/CheXbot—any other claims? [{timestamp}]"
                                        elif intent == "UserQuestions":
                                            follow_up = f"@{author}: Re: '{original_claim}' - Good question! Here’s more: [Source: {source_url}]. Thoughts? [{timestamp}]"
                                        else:
                                            follow_up = f"@{author}: Re: '{original_claim}' - Thanks for chiming in! See the source: [{source_url}]. What’s your take? [{timestamp}]"
                                        try:
                                            create_tweet(client, follow_up, in_reply_to_tweet_id=reply.id)
                                            post_count += 1
                                            print(f"Follow-up to {reply.id}: {follow_up}")
                                            processed_replies.add(reply.id)
                                            save_processed_replies(processed_replies)
                                        except tweepy.errors.Forbidden as e:
                                            if "duplicate content" in str(e).lower():
                                                print(f"Duplicate content error for reply {reply.id}: {e}. Skipping this follow-up.")
                                            else:
                                                raise e

        print(f"API Usage: {read_count} reads, {post_count} posts")
        time.sleep(600)
    except tweepy.errors.TooManyRequests as e:
        print(f"Rate limit exceeded: {e}. Waiting 15 minutes before retrying...")
        time.sleep(15 * 60)
    except Exception as e:
        print(f"Unexpected error: {e}")
        time.sleep(600)