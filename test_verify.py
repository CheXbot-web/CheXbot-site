# test_verify.py

from config import OPENAI_KEY, GOOGLE_API_KEY, GOOGLE_CSE_ID
from claim_verifier import ClaimVerifier
from safe_verify import safe_verify

# Initialize the verifier
verifier = ClaimVerifier(
    use_gpt=True,
    openai_key=OPENAI_KEY,
    google_api_key=GOOGLE_API_KEY,
    google_cse_id=GOOGLE_CSE_ID
)

# Sample claim
claim_text = "Trumps tariffs will kill the economy."

# Run the verification
result = safe_verify(claim_text, verifier)

# Show the result
print("\n🔍 Final Result:")
print(f"Verdict: {result['verdict']}")
print(f"Confidence: {result['confidence']:.2f}")
print(f"Sources: {result['sources']}")
if result['gpt_summary']:
    print(f"\n🧠 GPT Summary:\n{result['gpt_summary']}")
