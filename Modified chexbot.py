# Modified chexbot.py with Wikipedia evidence and claim verification
import tweepy
import time
import requests
from transformers import pipeline
import os
import logging
import csv
from datetime import datetime
from requests.exceptions import RequestException
import wikipedia  # Added for evidence retrieval

# Suppress transformers warnings
logging.getLogger("transformers").setLevel(logging.ERROR)

# Initialize classifier
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Classify topic of claim
def classify_claim_topic(claim):
    topic_labels = ["health", "politics", "science", "technology", "history", "general"]
    result = classifier(claim, candidate_labels=topic_labels, hypothesis_template="This text is about {}.")
    return result['labels'][0], dict(zip(result['labels'], result['scores']))

# Wikipedia-based evidence gathering
def verify_using_wikipedia(claim, wiki_search_limit=2):
    try:
        search_results = wikipedia.search(claim, results=wiki_search_limit)
        if not search_results:
            return ("NotEnoughInfo", {"true": 0, "false": 0, "not enough info": 1}, [], "No Wikipedia results found.")

        evidence = ""
        for title in search_results:
            try:
                page = wikipedia.page(title)
                evidence += page.content[:1000] + "\n"
            except Exception:
                continue

        if not evidence:
            return ("NotEnoughInfo", {"true": 0, "false": 0, "not enough info": 1}, search_results, "No usable Wikipedia content found.")

        result = classifier(claim, candidate_labels=["true", "false", "not enough info"], hypothesis_template="This statement is {}.")
        top_label = result['labels'][0]
        scores = dict(zip(result['labels'], result['scores']))

        return (top_label, scores, search_results, evidence[:500])
    except Exception as e:
        return ("Error", {}, [], str(e))

# Placeholder for future claimreview-based verification

def verify_using_claimreview(claim):
    return ("NotEnoughInfo", {}, [], "ClaimReview integration not implemented yet.")

# Route claim to best source

def verify_claim_with_evidence(claim, wiki_search_limit=2):
    try:
        topic, topic_scores = classify_claim_topic(claim)

        if topic == "politics":
            return verify_using_claimreview(claim)
        else:
            return verify_using_wikipedia(claim, wiki_search_limit)

    except Exception as e:
        return ("Error", {}, [], str(e))

# Replace this block in your mention handling logic:
label, scores, sources, evidence = verify_claim_with_evidence(tweet_text)
label = label if label.lower() in ["true", "false"] else "NotEnoughInfo"
log_user_data(tweet_text, label, "claim")

# Fallback handling
if sources:
    source_url = shorten_url("https://en.wikipedia.org/wiki/" + sources[0].replace(" ", "_"))
else:
    source_url = "https://en.wikipedia.org"

# Compose reply text
confidence_score = scores.get(label.lower(), 0.0)
reply_text = (f"@{author}: Checked: {label.title()} (Confidence: {confidence_score:.2f}).\n"
              f"Source: {source_url}\n"
              f"Excerpt: {evidence[:240]}...\n\n"
              f"Reply to this tweet with @CheXbot in your message! Support real-time checks: bit.ly/CheXbot")
