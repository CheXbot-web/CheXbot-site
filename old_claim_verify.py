import wikipedia
from transformers import pipeline
import logging

# Suppress transformers warnings
logging.getLogger("transformers").setLevel(logging.ERROR)

# Load model
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

def classify_claim_topic(claim):
    topic_labels = ["health", "politics", "science", "technology", "history", "general"]
    result = classifier(claim, candidate_labels=topic_labels, hypothesis_template="This text is about {}.")
    return result['labels'][0], dict(zip(result['labels'], result['scores']))

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

def verify_using_claimreview(claim):
    return ("NotEnoughInfo", {}, [], "ClaimReview integration not implemented yet.")

def verify_claim_with_evidence(claim, wiki_search_limit=2):
    try:
        topic, topic_scores = classify_claim_topic(claim)

        if topic == "politics":
            return verify_using_claimreview(claim)
        else:
            return verify_using_wikipedia(claim, wiki_search_limit)
    except Exception as e:
        return ("Error", {}, [], str(e))

