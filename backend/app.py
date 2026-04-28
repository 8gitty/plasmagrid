import os
import json
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, db
from dotenv import load_dotenv
from datetime import datetime

from ai_engine import get_allocation_plan, check_threat
from slime import slime_allocate
from blockchain import log_transfer_on_chain, get_total_transfers

load_dotenv()

app = Flask(__name__)
CORS(app)

# ── FIREBASE INIT ─────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_PATH  = os.path.join(BASE_DIR, "firebase_key.json")
USE_FB    = False

try:
    cred = credentials.Certificate(KEY_PATH)
    firebase_admin.initialize_app(cred, {"databaseURL": os.getenv("FIREBASE_URL")})
    USE_FB = True
    print("[Firebase] Connected")
except Exception as e:
    print(f"[Firebase] Disabled — {e}")

# ── LOCAL FALLBACK DB ─────────────────────────────────────
LOCAL_DB = os.path.join(BASE_DIR, "local_db.json")

def _read():
    if not os.path.exists(LOCAL_DB):
        return {"nodes": {}, "allocations": {}, "threats": {}}
    with open(LOCAL_DB, "r", encoding="utf-8") as f:
        data = json.load(f)
    data.setdefault("nodes", {})
    data.setdefault("allocations", {})
    data.setdefault("threats", {})
    return data

def _write(data):
    with open(LOCAL_DB, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def _get_col(name):
    if USE_FB:
        return db.reference(f"/{name}").get() or {}
    return _read().get(name, {})

def _push_col(name, value):
    if USE_FB:
        db.reference(f"/{name}").push(value)
        return
    data = _read()
    data[name][datetime.now().isoformat()] = value
    _write(data)

def _get_node(nid):
    if USE_FB:
        return db.reference(f"/nodes/{nid}").get()
    nodes = _read().get("nodes", {})
    return nodes.get(nid) if isinstance(nodes, dict) else next((n for n in nodes if n.get("id") == nid), None)

def _update_node(nid, updates):
    if USE_FB:
        db.reference(f"/nodes/{nid}").update(updates)
        return
    data = _read()
    nodes = data.get("nodes", {})
    if isinstance(nodes, dict):
        node = nodes.get(nid, {})
        node.update(updates)
        nodes[nid] = node
    data["nodes"] = nodes
    _write(data)

# ── ROUTES ────────────────────────────────────────────────

@app.route("/nodes", methods=["GET"])
def get_nodes():
    data = _get_col("nodes")
    if not data:
        return jsonify([])
    return jsonify(list(data.values()) if isinstance(data, dict) else data)


@app.route("/allocate", methods=["POST"])
def allocate():
    data = _get_col("nodes")
    hospitals = list(data.values()) if isinstance(data, dict) else data

    slime_result  = slime_allocate(hospitals)
    gemini_result = get_allocation_plan(hospitals, slime_result)

    # log to blockchain
    blockchain_hashes = []
    for t in gemini_result.get("transfers", []):
        tx = log_transfer_on_chain(
            t.get("from", "Unknown"),
            t.get("to", "Unknown"),
            t.get("resource", "resources"),
            t.get("amount", 1),
            t.get("reason", "PlasmaGrid allocation")
        )
        if tx:
            blockchain_hashes.append({
                "hash": tx,
                "from": t.get("from"),
                "to": t.get("to"),
                "resource": t.get("resource"),
                "etherscan": f"https://sepolia.etherscan.io/tx/{tx}"
            })

    # log to history
    _push_col("allocations", {
        "timestamp": datetime.now().isoformat(),
        "urgency": gemini_result.get("urgency"),
        "summary": gemini_result.get("summary"),
        "transfers": gemini_result.get("transfers"),
        "slime_transfers": slime_result
    })

    return jsonify({
        "slime": slime_result,
        "gemini": gemini_result,
        "ai_used": gemini_result.get("ai_used", "Unknown"),
        "blockchain": blockchain_hashes,
        "total_on_chain": get_total_transfers(),
        "timestamp": datetime.now().isoformat()
    })


@app.route("/update-node", methods=["POST"])
def update_node():
    body        = request.json
    node_id     = body.get("id")
    new_scarcity = body.get("scarcity")

    node = _get_node(node_id) or {}
    old_scarcity = node.get("scarcity", 50)

    threat = check_threat(node.get("name", node_id), old_scarcity, new_scarcity)

    if threat.get("threat"):
        _push_col("threats", {
            "timestamp": datetime.now().isoformat(),
            "node": node.get("name"),
            "node_id": node_id,
            "old_scarcity": old_scarcity,
            "new_scarcity": new_scarcity,
            "threat_type": threat.get("threat_type"),
            "confidence": threat.get("confidence"),
            "reason": threat.get("reason"),
            "action": "QUARANTINED",
            "status": "active"
        })
        return jsonify({
            "success": False,
            "threat_detected": True,
            "threat": threat,
            "message": f"Threat at {node.get('name')}"
        })

    _update_node(node_id, {
        "scarcity": new_scarcity,
        "last_updated": datetime.now().isoformat()
    })
    return jsonify({"success": True, "threat_detected": False, "node_id": node_id, "new_scarcity": new_scarcity})


@app.route("/threats", methods=["GET"])
def get_threats():
    data = _get_col("threats")
    if not data:
        return jsonify([])
    threats = list(data.values()) if isinstance(data, dict) else data
    return jsonify(sorted(threats, key=lambda x: x.get("timestamp",""), reverse=True))


@app.route("/history", methods=["GET"])
def get_history():
    data = _get_col("allocations")
    if not data:
        return jsonify([])
    items = list(data.values()) if isinstance(data, dict) else data
    return jsonify(items[-10:])


@app.route("/")
def serve_index():
    frontend = os.path.join(BASE_DIR, "../frontend")
    return send_from_directory(frontend, "index.html")


@app.route("/<path:path>")
def serve_static(path):
    frontend = os.path.join(BASE_DIR, "../frontend")
    return send_from_directory(frontend, path)


if __name__ == "__main__":
    app.run(debug=False, port=5000)