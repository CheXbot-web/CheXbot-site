from claim_verifier import ClaimVerifier
from safe_verify import safe_verify

verifier = ClaimVerifier(use_gpt=True)
claim = "The earth is flat"
result = safe_verify(claim, verifier)
print(verifier.format_result(result))
