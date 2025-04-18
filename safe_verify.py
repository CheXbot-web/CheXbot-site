# safe_verify.py

from transformers import pipeline
from site_api import post_cache_update
from db import save_fact_check, save_claim_details 

# Setup Hugging Face classifier
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")


# Main verification function
def safe_verify(claim, verifier, claim_id, confidence_threshold=0.85):

    print("🔎 Running BART classification on claim...")
    candidate_labels = ["TrueClaim", "FalseClaim"]
    classification = classifier(claim, candidate_labels)
    label = classification["labels"][0]
    confidence = classification["scores"][0]

    result = {
        "verdict": "True" if label == "TrueClaim" else "False",
        "confidence": confidence,
        "sources": [],
        "model": "bart-large-mnli",
        "gpt_summary": None
    }

    if result["confidence"] < confidence_threshold:
        snippets = verifier.search_google_cse(claim)
        result["sources"] = snippets
        if verifier.use_gpt and snippets:
            gpt_summary = verifier.summarize_with_gpt(claim, snippets)
            result.update({
                "verdict":    "See GPT summary",
                "confidence": 0.99,
                "model":      "gpt-enhanced",
                "gpt_summary": gpt_summary
            })
            save_claim_details(claim_id, gpt_summary, snippets)
    # Push to web with correct tweet-based ID
    post_cache_update(claim_id, result)

    return result
