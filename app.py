import sys
import os
import time

from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "prop_firm_signals"))
import signal_engine as se

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder="frontend/build", static_url_path="")
CORS(app, origins=["http://localhost:3000"])


@app.route("/api/scan")
def scan():
    results = {}
    for asset in se.ASSETS:
        name, symbol = asset["name"], asset["symbol"]
        time.sleep(1)
        c15 = se.fetch_candles(symbol, "15min", 220)
        time.sleep(1)
        c4h = se.fetch_candles(symbol, "4h", 220)
        sig = se.analyze_signal(c15, c4h)
        results[name] = sig if sig else {"direction": "ERROR"}
    return jsonify(results)


@app.route("/api/history")
def history():
    h = se.load_history()
    stats = se.calc_accuracy(h)
    return jsonify({"signals": h, "stats": stats})


@app.route("/api/push-clickup", methods=["POST"])
def push_clickup():
    data = request.get_json()
    se.push_to_clickup(data["asset"], data["signal"])
    return jsonify({"ok": True})


# Serve built React app in production
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    build = app.static_folder
    if build and path and os.path.exists(os.path.join(build, path)):
        return send_from_directory(build, path)
    if build and os.path.exists(os.path.join(build, "index.html")):
        return send_from_directory(build, "index.html")
    return jsonify({"error": "Frontend not built. Run: cd frontend && npm run build"}), 404


if __name__ == "__main__":
    app.run(debug=True, port=5000)
