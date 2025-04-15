import random

def trust_level_emoji(confidence):
    if confidence >= 0.90:
        return "🟩", "5/5"
    elif confidence >= 0.75:
        return "🟨", "4/5"
    elif confidence >= 0.60:
        return "🟧", "3/5"
    elif confidence >= 0.40:
        return "🟥", "2/5"
    else:
        return "⬛", "1/5"

def random_catchphrase():
    phrases = [
        "Truth is trending.",
        "Verified by CheXbot.",
        "Facts over fiction.",
        "Reality check complete.",
        "Stay informed."
    ]
    return random.choice(phrases)
