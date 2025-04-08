# claim_categorizer.py

def categorize_claim(claim_text):
    """
    Categorizes a claim based on keyword heuristics.
    Later this can be replaced with a classifier or NLI model.
    Returns a category like 'health', 'politics', 'science', or 'general'.
    """
    claim = claim_text.lower()

    if any(keyword in claim for keyword in ["vaccine", "virus", "covid", "pandemic", "cdc", "who"]):
        return "health"
    elif any(keyword in claim for keyword in ["election", "vote", "president", "congress", "trump", "biden"]):
        return "politics"
    elif any(keyword in claim for keyword in ["climate", "nasa", "space", "gravity", "theory"]):
        return "science"
    elif any(keyword in claim for keyword in ["bitcoin", "stock", "crypto", "money", "economy"]):
        return "finance"
    else:
        return "general"
