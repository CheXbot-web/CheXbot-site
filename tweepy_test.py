import tweepy

client = tweepy.Client(
    consumer_key="wabGL48dhV0Azwqqsk631iKtz",
    consumer_secret="Rri02HktT6shGuHCCkXZ8MKsiavhusWlR9Am1RRtIHPvpp4QC4",
    access_token="1901717905299161088-HCu0n570cuLwt1MFQwsd1p8sTIbhVy",
    access_token_secret="TOxdO2B547Hauc7BB9kSZLql7QodECpVZo9IXvzmkdvaB"
)

tweet_id = "1903546924223099314"
reply_text = "fact bot Test reply number 3"
client.create_tweet(text=reply_text, in_reply_to_tweet_id=tweet_id)
print(f"Replied: {reply_text}")