# chexbot_script.py

import tweepy
import time
from claim_verifier import ClaimVerifier
# from safe_verify import safe_verify
# from db import save_fact_check
from key_loader import load_keys

# === Load Keys ===
keys = load_keys()

OPENAI_KEY = keys.get("OpenAI_Key")
GOOGLE_API_KEY = keys.get("Google_API_Key")
GOOGLE_CSE_ID = keys.get("Google_CSI_ID")

TWITTER_KEYS = {
    "bearer_token": keys.get("Bearer Token"),
    "consumer_key": keys.get("API Key"),
    "consumer_secret": keys.get("API Secret"),
    "access_token": keys.get("Access Token"),
    "access_token_secret": keys.get("Access Secret"),
}

# === Setup Twitter API ===
auth = tweepy.OAuth1UserHandler(
    TWITTER_KEYS['bearer_token'],
    TWITTER_KEYS['consumer_key'],
    TWITTER_KEYS['consumer_secret'],
    TWITTER_KEYS['access_token'],
    TWITTER_KEYS['access_token_secret']
)
api = tweepy.API(auth)

# === Initialize ClaimVerifier ===
verifier = ClaimVerifier(
    use_gpt=True if OPENAI_KEY else False,
    openai_key=OPENAI_KEY,
    google_api_key=GOOGLE_API_KEY,
    google_cse_id=GOOGLE_CSE_ID
)

# === Bot Loop ===
last_seen_id = None  # Replace with DB or file state in production

def check_mentions():
    global last_seen_id
    mentions = api.mentions_timeline(since_id=last_seen_id, tweet_mode='extended')
    for tweet in reversed(mentions):
        if tweet.user.screen_name.lower() == "chexbot":
            continue  # Skip self

        # Determine the claim
        if tweet.in_reply_to_status_id:
            parent = api.get_status(tweet.in_reply_to_status_id, tweet_mode="extended")
            claim = parent.full_text
        elif "quoted_status" in tweet._json:
            claim = tweet._json["quoted_status"]["full_text"]
        else:
            claim = tweet.full_text.replace("@CheXbot", "").strip()

        # Verify the claim
        result = safe_verify(claim, verifier)

        # Format reply
        reply_text = verifier.format_result(result)
        reply_text += "\n\nDo you agree or disagree?"

        # Post reply
        try:
            reply = api.update_status(
                status=reply_text,
                in_reply_to_status_id=tweet.id,
                auto_populate_reply_metadata=True
            )

            # Save result
            save_fact_check(
                original_tweet_id=tweet.id,
                reply_id=reply.id,
                username=tweet.user.screen_name,
                claim=claim,
                verdict=result["verdict"],
                confidence=result["confidence"]
            )
            last_seen_id = tweet.id

        except Exception as e:
            print(f"Failed to reply: {e}")

if __name__ == "__main__":
    while True:
        check_mentions()
        time.sleep(60)  # Poll every 60 seconds
