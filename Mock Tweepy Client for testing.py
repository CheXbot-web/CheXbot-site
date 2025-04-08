# Mock Tweepy Client for testing
class MockTweet:
    def __init__(self, id, text, author_id, in_reply_to_tweet_id=None):
        self.id = id
        self.text = text
        self.author_id = author_id
        self.in_reply_to_tweet_id = in_reply_to_tweet_id

class MockUser:
    def __init__(self, username):
        self.username = username

class MockClient:
    def search_recent_tweets(self, query, since_id=None, tweet_fields=None):
        if query == "@CheXbot -from:CheXbot":
            # Simulate a mention
            return MockResponse([MockTweet(id=12345, text="@CheXbot Check: Moon’s cheese", author_id="111")])
        elif query == "to:CheXbot":
            # Simulate a reply
            return MockResponse([MockTweet(id=67890, text="No, I don’t agree", author_id="111", in_reply_to_tweet_id=12345)])
        return MockResponse([])

    def get_user(self, id):
        return MockResponse(MockUser("User123"))

    def create_tweet(self, text, in_reply_to_tweet_id=None):
        print(f"Mock tweet created: {text} (in reply to {in_reply_to_tweet_id})")
        return MockResponse({"id": in_reply_to_tweet_id + 1 if in_reply_to_tweet_id else 1000})

class MockResponse:
    def __init__(self, data):
        self.data = data

# Mock Bitly response
def mock_shorten_url(long_url, bitly_token):
    return "bit.ly/NASAmoon"