from flask import Flask, render_template, abort
import json
import os

app = Flask(__name__)

CACHE_FILE = "claim_cache.json"

if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r") as f:
        claim_cache = json.load(f)
else:
    claim_cache = {}

@app.route("/")
def index():
    return "<h1>Welcome to CheXbot</h1><p>To view a claim, use /claim/&lt;claim_id&gt;</p>"

@app.route("/claim/<claim_id>")
def show_claim(claim_id):
    result = claim_cache.get(claim_id)
    if not result:
        abort(404)
    return render_template("claim.html", result=result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
