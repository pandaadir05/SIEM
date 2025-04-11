#!/usr/bin/env python3
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/llm/summarize", methods=["POST"])
def summarize():
    data = request.json or {}
    alerts = data.get("alerts", [])
    summary = f"You have {len(alerts)} alerts. Potential threats: " + ", ".join(a.get("alert_type","Unknown") for a in alerts)
    return jsonify({"summary": summary})

if __name__ == "__main__":
    app.run(port=7000, debug=True)
