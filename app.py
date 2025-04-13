from flask import Flask, render_template, abort
import hashlib
import json
import os
from flask import request, jsonify
from config import UPDATE_API_KEY
from flask import send_file

app = Flask(__name__)

CACHE_FILE = "claim_cache.json"

# Backup file transfer
@app.route("/backup/<filename>")
def download_backup(filename):
    if filename not in ["chexbot.db", "last_seen.json"]:
        abort(403)
    return send_file(filename, as_attachment=True)

# Load cache at startup
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r") as f:
        claim_cache = json.load(f)
    print(f"✅ Loaded {len(claim_cache)} cached claims")
else:
    claim_cache = {}
    print("⚠️ No claim_cache.json found")

def save_cache():
    with open(CACHE_FILE, "w") as f:
        json.dump(claim_cache, f, indent=2)


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

@app.route("/update", methods=["POST"])
def update_cache():
    try:
        print("📬 /update endpoint was hit")

        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        print(f"🔑 Received token: {token}")

        if token != UPDATE_API_KEY:
            print("⛔ Token mismatch — unauthorized request.")
            return jsonify({"error": "Unauthorized"}), 403

        data = request.get_json()
        print(f"📦 Incoming data: {data}")

        if not data or "claim_id" not in data or "result" not in data:
            print("❌ Missing 'claim_id' or 'result' in data.")
            return jsonify({"error": "Invalid data"}), 400

        claim_id = data["claim_id"]
        result = data["result"]
        claim_cache[claim_id] = result

        save_cache()

        print(f"✅ Updated cache with claim ID: {claim_id}")
        return jsonify({"message": "Cache updated"}), 200

    except Exception as e:
        print(f"🔥 Exception in update_cache(): {e}")
        return jsonify({"error": "Server error", "detail": str(e)}), 500




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
