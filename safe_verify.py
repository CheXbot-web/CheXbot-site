# safe_verify.py

import hashlib
import json
import os
from transformers import pipeline

CACHE_FILE = "claim_cache.json"

# Load or initialize claim cache
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r") as f:
        claim_cache = json.load(f)
else:
    claim_cache = {}

# Setup Hugging Face classifier
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Utility: Save cache to disk
def save_cache():
    with open(CACHE_FILE, "w") as f:
        json.dump(claim_cache, f, indent=2)

# Utility: Hash a claim text
def hash_claim(claim):
    return hashlib.sha256(claim.encode()).hexdigest()

# Main verification function
def safe_verify(claim, verifier, confidence_threshold=0.85):
    claim_id = hash_claim(claim)

    # Return cached result if available
    if claim_id in claim_cache:
        return claim_cache[claim_id]

    # Step 1: Run BART zero-shot classification
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

    # Step 2: Escalate if confidence is low
    if result["confidence"] < confidence_threshold:
        print("⚠️  Low confidence — checking search and GPT...")
        snippets = verifier.search_google_cse(claim)
        result["sources"] = snippets
        if verifier.use_gpt and snippets:
            gpt_summary = verifier.summarize_with_gpt(claim, snippets)
            result["verdict"] = "See GPT summary"
            result["confidence"] = 0.99
            result["model"] = "gpt-enhanced"
            result["gpt_summary"] = gpt_summary

    # Cache and return result
    claim_cache[claim_id] = result
    save_cache()
    post_cache_update(claim_id, result)

    return result