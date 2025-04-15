# claim_verifier.py

import openai
import requests
import random
from utils import trust_level_emoji, random_catchphrase

class ClaimVerifier:
    def __init__(self, use_gpt=False, openai_key=None, google_api_key=None, google_cse_id=None):
        self.use_gpt = use_gpt
        self.openai_key = openai_key
        self.google_api_key = google_api_key
        self.google_cse_id = google_cse_id
        if self.use_gpt and self.openai_key:
            openai.api_key = self.openai_key

    def search_google_cse(self, claim):
        query = claim.replace("\n", " ").strip()
        params = {
            "key": self.google_api_key,
            "cx": self.google_cse_id,
            "q": query
        }
        try:
            response = requests.get("https://www.googleapis.com/customsearch/v1", params=params)
            data = response.json()
            results = data.get("items", [])
            print(f"✅ Fetched {len(results)} search results.")
            for i, item in enumerate(results[:3]):
                print(f"Snippet {i+1}: {item.get('snippet', '[No snippet]')}")
            return [item.get("snippet", "No snippet available.") for item in results[:3]]
        except Exception as e:
            print(f"Google Search failed: {e}")
            return []

    def summarize_with_gpt(self, claim, snippets):
        prompt = f"Claim: {claim}\n\nBased on the following sources, is this claim true or false?\n\n" + "\n\n".join(snippets)
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    

    def format_result(self, result, claim_id):
        verdict = result["verdict"]
        confidence = result["confidence"]
        shield, level = trust_level_emoji(confidence)
        catchphrase = random_catchphrase()
        summary_url = f"https://chexbot-web.onrender.com/claim/{claim_id}"

        return (
            f"✅ Claim Verified: {verdict}\n"
            f"🧠 Confidence: {confidence:.2f}\n"
            f"🤖 {shield} Trust Level {level} — View Summary 🔗 {summary_url}\n\n"
            f"{catchphrase}"
        )
