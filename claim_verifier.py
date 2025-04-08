# claim_verifier.py

import openai
import requests
import random

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
    def format_result(self, result, claim_id=None):
        support_messages = [
            "✅ Support real-time checks: bit.ly/CheXbot",
            "✅ Help keep CheXbot running: bit.ly/CheXbot",
            "✅ Back this project: bit.ly/CheXbot",
            "✅ Fuel the fact-checks: bit.ly/CheXbot"
        ]
        support_line = random.choice(support_messages)

        verdict = result.get("verdict", "Unknown")
        confidence = result.get("confidence", 0.0)
        link = f"https://chexbot-web.onrender.com/claim/{claim_id}" if claim_id else ""

        return (
            f"✅ Claim Verified: {verdict}\n"
            f"🧠 Confidence: {confidence:.2f}\n"
            f"🔗 {link}\n"
            f"{support_line}"
        )
        