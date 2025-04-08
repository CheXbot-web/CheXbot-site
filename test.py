# test_chexbot.py
from transformers import pipeline

class MockTweet:
    def __init__(self, id, text, author_id, referenced_tweets=None):
        self.id = id
        self.text = text
        self.author_id = author_id
        self.referenced_tweets = referenced_tweets

class MockReferencedTweet:
    def __init__(self, type, id):
        self.type = type
        self.id = id

class MockUser:
    def __init__(self, username):
        self.username = username

class MockClient:
    def search_recent_tweets(self, query, since_id=None, tweet_fields=None):
        if query == "@CheXbot -from:CheXbot":
            return MockResponse([MockTweet(id=12345, text="@CheXbot Check: Moon’s cheese", author_id="111")])
        elif query == "to:CheXbot":
            return MockResponse([MockTweet(id=67890, text="No, I don’t agree", author_id="111", 
                                          referenced_tweets=[MockReferencedTweet(type="replied_to", id=12345)])])
        return MockResponse([])

    def get_user(self, id):
        return MockResponse(MockUser("User123"))

    def create_tweet(self, text, in_reply_to_tweet_id=None):
        print(f"Mock tweet created: {text} (in reply to {in_reply_to_tweet_id})")
        return MockResponse({"id": in_reply_to_tweet_id + 1 if in_reply_to_tweet_id else 1000})

class MockResponse:
    def __init__(self, data):
        self.data = data

def mock_shorten_url(long_url, bitly_token):
    return "bit.ly/NASAmoon"

client = MockClient()
classifier = pipeline("zero-shot-classification", model="distilbert-base-uncased")
subs = {"@User123", "@Sub456"}
last_id = None
processed_replies = set()
processed_mentions = set()

shorten_url = mock_shorten_url

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
            label = "FalseClaim"  # Hardcoded
            long_url = "https://www.nasa.gov/moon-facts"
            source_url = shorten_url(long_url, "mock_bitly_token")
            reply_text = (f"@{author}: Checked: {label}. [Source: {source_url}] Do you agree? Reply or DM! "
                          f"@CheXbot checks mentions every 5 minutes—thanks for your patience! Support real-time checks: bit.ly/CheXbot")
            reply = client.create_tweet(text=reply_text, in_reply_to_tweet_id=tweet_id)
            print(f"Replied to {tweet_id}: {reply_text}")
            last_id = tweet_id
            processed_mentions.add(tweet_id)

replies = client.search_recent_tweets(query=f"to:CheXbot", tweet_fields=["referenced_tweets", "text", "author_id"])
if replies and replies.data:
    for reply in replies.data:
        if reply.id not in processed_replies:
            in_reply_to_tweet_id = None
            if reply.referenced_tweets:
                for ref_tweet in reply.referenced_tweets:
                    if ref_tweet.type == "replied_to":
                        in_reply_to_tweet_id = ref_tweet.id
                        break
            if in_reply_to_tweet_id:
                reply_text = reply.text
                author_id = reply.author_id
                author = client.get_user(id=author_id).data.username
                intent = "UserDisagrees"  # Hardcoded
                long_url = "https://www.nasa.gov/moon-facts"  # Recompute source_url
                source_url = shorten_url(long_url, "mock_bitly_token")
                if intent == "UserDisagrees":
                    follow_up = f"@{author}: Interesting! Science says it’s rock, not cheese—[Source: {source_url}]. What do you think?"
                elif intent == "UserAgrees":
                    follow_up = f"@{author}: Glad you agree! More checks @ bit.ly/CheXbot—any other claims?"
                elif intent == "UserQuestions":
                    follow_up = f"@{author}: Good question! Here’s more: [Source: {source_url}]. Thoughts?"
                else:
                    follow_up = f"@{author}: Thanks for chiming in! See the source: [{source_url}]. What’s your take?"
                client.create_tweet(text=follow_up, in_reply_to_tweet_id=reply.id)
                print(f"Follow-up to {reply.id}: {follow_up}")
                processed_replies.add(reply.id)