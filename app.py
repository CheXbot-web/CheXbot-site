from flask import Flask, render_template, abort, request, send_file, jsonify
import hashlib
import json
import os
import io
import zipfile
# from config import UPDATE_API_KEY
UPDATE_API_KEY = "jB5jdm44haN4txs4lULsPYYizgekrahniu"

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

# Backup file transfer
@app.route("/backup", methods=["GET"])
def backup_files():
    try:
        db_path = "chexbot.db"
        # last_seen_path = "last_seen.json"

        # Confirm both files exist
        files_to_backup = []
        if os.path.exists(db_path):
            files_to_backup.append(db_path)
        if not files_to_backup:
            return jsonify({"error": "No files to back up"}), 404

        # Create in-memory zip archive
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for file_path in files_to_backup:
                zipf.write(file_path, arcname=os.path.basename(file_path))

        zip_buffer.seek(0)

        return send_file(
            zip_buffer,
            mimetype="application/zip",
            as_attachment=True,
            download_name="chexbot_backup.zip"
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Server error", "details": str(e)}), 500
    
@app.route("/summary/<claim_id>")
def get_summary(claim_id):
    from db import get_fact_check_by_id
    from gpt_summarizer import generate_gpt_summary

    try:
        # ✅ Check if summary already exists in claim_cache
        if claim_id in claim_cache and claim_cache[claim_id].get("gpt_summary"):
            return jsonify({"summary": claim_cache[claim_id]["gpt_summary"]})

        # 🧠 Otherwise, fetch the claim from DB
        fact = get_fact_check_by_id(claim_id)
        if not fact:
            return jsonify({"error": "Claim not found"}), 404

        # 🤖 Generate GPT summary on the fly
        summary = generate_gpt_summary(fact["claim"], fact["verdict"], fact["confidence"])

        # 💾 Save to cache
        if claim_id not in claim_cache:
            claim_cache[claim_id] = {}
        claim_cache[claim_id]["gpt_summary"] = summary
        save_cache()

        return jsonify({"summary": summary})

    except Exception as e:
        return jsonify({"error": "Failed to generate summary", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
