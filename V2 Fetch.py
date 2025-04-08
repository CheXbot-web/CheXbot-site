import tweepy
auth = tweepy.OAuth1UserHandler("wabGL48dhV0Azwqqsk631iKtz", "Rri02HktT6shGuHCCkXZ8MKsiavhusWlR9Am1RRtIHPvpp4QC4", "1901717905299161088-HCu0n570cuLwt1MFQwsd1p8sTIbhVy", "TOxdO2B547Hauc7BB9kSZLql7QodECpVZo9IXvzmkdvaB")
api = tweepy.API(auth)
tweet = api.get_status("1903546924223099314")
print(tweet.text)