import tweepy
with open("x_keys.txt", "r") as f:
    bearer_token = f.readlines()[0].split(": ")[1].strip()
stream = tweepy.StreamingClient(bearer_token=bearer_token)
stream.filter()  # Just connect