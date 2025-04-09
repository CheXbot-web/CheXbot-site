from flask import Flask, render_template, abort
import hashlib
import json
import os

app = Flask(__name__)

CACHE_FILE = "claim_cache.json"

# Load cache at startup
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r") as f:
        claim_cache = json.load(f)
    print(f"✅ Loaded {len(claim_cache)} cached claims")
else:
    claim_cache = {}
    print("⚠️ No claim_cache.json found")

# Utility to generate MD5 claim IDs
def get_claim_id(claim_text):
    return hashlib.md5(claim_text.encode("utf-8")).hexdigest()

@app.route("/")
def index():
    return "<h1>Welcome to CheXbot</h1><p>To view a claim, use /claim/&lt;claim_id&gt;</p>"

@app.route("/claim/<claim_id>")
def show_claim(claim_id):
    result = claim_cache.get(claim_id)
    if not result:
        abort(404)
    return render_template("claim.html", result=result)

# Optional debug route
@app.route("/debug-cache")
def debug_cache():
    return {
        "total_cached": len(claim_cache),
        "sample_keys": list(claim_cache.keys())[:5]
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
