from flask import Flask, render_template, abort, request, send_file, jsonify
import hashlib
import json
import os
import io
import zipfile
from datetime import datetime
from db import get_fact_check_by_original_id
# from config import UPDATE_API_KEY
UPDATE_API_KEY = "jB5jdm44haN4txs4lULsPYYizgekrahniu"

app = Flask(__name__)


@app.route("/")
def index():
    return "<h1>Welcome to CheXbot</h1><p>To view a claim, use /claim/&lt;claim_id&gt;</p>"

@app.route("/claim/<claim_id>")
def show_claim(claim_id):
    import json
    from db import get_fact_check_by_original_id, get_claim_details

    # 1) Grab the base fact‑check row
    fact = get_fact_check_by_original_id(claim_id)
    if not fact:
        return "Claim not found.", 404

    # 2) Build your result dict
    result = {
        "claim":      fact["claim"],
        "verdict":    fact["verdict"],
        "confidence": fact["confidence"],
        "sources":    [],
        "model":      "unknown",     # or convert to dict and .get if you add this column later
        "gpt_summary": None
    }

    # 3) Pull in any saved summary + sources
    details = get_claim_details(claim_id)  # returns (gpt_summary, sources_json) or None
    if details:
        summary, sources_json = details
        result["gpt_summary"] = summary
        try:
            result["sources"] = json.loads(sources_json or "[]")
        except ValueError:
            result["sources"] = []

    # 4) Return it
    return render_template("claim.html", result=result, claim_id=claim_id, now=datetime.now())

@app.route("/update", methods=["POST"])
def update_cache():
    from db import save_fact_check, save_claim_details

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

        # Save to fact_checks
        save_fact_check(
            original_tweet_id=claim_id,
            reply_id=result.get("reply_id", ""),  # Optional
            username=result.get("username", "unknown"),
            claim=result.get("claim", ""),
            verdict=result.get("verdict", "Unknown"),
            confidence=result.get("confidence", 0.0)
        )

        # Save to claim_details
        save_claim_details(
            claim_id=claim_id,
            summary=result.get("gpt_summary"),
            sources=json.dumps(result.get("sources", []))
        )

        print(f"✅ Saved claim {claim_id} to DB (fact_checks + claim_details)")
        return jsonify({"message": "Cache updated"}), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
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
    from db import get_fact_check_by_original_id, get_claim_details, save_claim_details
    from gpt_summarizer import generate_gpt_summary

    try:
        existing = get_claim_details(claim_id)
        if existing and existing[0]:  # gpt_summary exists
            return jsonify({"summary": existing[0]})

        fact = get_fact_check_by_original_id(claim_id)
        if not fact:
            return jsonify({"error": "Claim not found"}), 404

        summary = generate_gpt_summary(fact["claim"], fact["verdict"], fact["confidence"])
        save_claim_details(claim_id, summary)
        return jsonify({"summary": summary})

    except Exception as e:
        return jsonify({"error": "Failed to generate summary", "details": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
