import tweepy
from config import BEARER_TOKEN

client = tweepy.Client(bearer_token=BEARER_TOKEN)

user = client.get_user(username="CheXbot")
print("Username:", user.data.username)
print("ID:", user.data.id)
