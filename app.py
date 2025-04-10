from flask import Flask, render_template, abort
import hashlib
import json
import os
from flask import request, jsonify
from config import UPDATE_API_KEY

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
""" @app.route("/update", methods=["POST"])
def update_cache():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer ") or auth.split(" ")[1] != UPDATE_API_KEY:
        return "Unauthorized", 401

    try:
        data = request.get_json()
        claim_id = data["id"]
        claim_cache[claim_id] = data

        # Save updated cache to file
        with open(CACHE_FILE, "w") as f:
            json.dump(claim_cache, f, indent=2)

        print(f"✅ Updated cache with claim ID: {claim_id}")
        return "✅ Claim added to cache", 200

    except Exception as e:
        print("❌ Error updating cache:", e)
        return "Server error", 500
     """
    
@app.route("/update", methods=["POST"])
def update_cache():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if token != UPDATE_API_KEY:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    if not data or "claim_id" not in data:
        return jsonify({"error": "Missing claim_id"}), 400

    claim_id = data["claim_id"]
    result = data["result"]

    claim_cache[claim_id] = result
    save_cache()

    return jsonify({"message": "Cache updated"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
