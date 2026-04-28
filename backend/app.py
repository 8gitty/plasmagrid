import os
import json
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime

from ai_engine import get_allocation_plan, check_threat
from slime import slime_allocate

# ── SAFE IMPORTS ──────────────────────────────────────────
try:
    import firebase_admin
    from firebase_admin import credentials, db as firebase_db
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    print("[Firebase] Module not installed")

try:
    from blockchain import log_transfer_on_chain, get_total_transfers
    BLOCKCHAIN_ENABLED = True
except Exception:
    BLOCKCHAIN_ENABLED = False
    def log_transfer_on_chain(*args, **kwargs): return None
    def get_total_transfers(): return 0

load_dotenv()

app = Flask(__name__)
CORS(app)

# ── FIREBASE INIT ─────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
key_json = json.loads(os.getenv("FIREBASE_KEY_JSON", "{}"))
USE_FB    = False

if FIREBASE_AVAILABLE:
    try:
        cred = credentials.Certificate(key_json)
        firebase_admin.initialize_app(cred, {
            "databaseURL": os.getenv("FIREBASE_URL")
        })
        USE_FB = True
        print("[Firebase] Connected")
    except Exception as e:
        print(f"[Firebase] Disabled — {e}")
else:
    print("[Firebase] Using local JSON storage")

# ── LOCAL FALLBACK DB ─────────────────────────────────────
LOCAL_DB = os.path.join(BASE_DIR, "local_db.json")

def _read():
    if not os.path.exists(LOCAL_DB):
        return {"nodes": {}, "allocations": {}, "threats": {}}
    try:
        with open(LOCAL_DB, "r", encoding="utf-8") as f:
            data = json.load(f)
        data.setdefault("nodes", {})
        data.setdefault("allocations", {})
        data.setdefault("threats", {})
        return data
    except Exception:
        return {"nodes": {}, "allocations": {}, "threats": {}}

def _write(data):
    try:
        with open(LOCAL_DB, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"[LocalDB] Write error: {e}")

def _get_col(name):
    if USE_FB:
        return firebase_db.reference(f"/{name}").get() or {}
    return _read().get(name, {})

def _push_col(name, value):
    if USE_FB:
        firebase_db.reference(f"/{name}").push(value)
        return
    data = _read()
    data[name][datetime.now().isoformat()] = value
    _write(data)

def _get_node(nid):
    if USE_FB:
        return firebase_db.reference(f"/nodes/{nid}").get()
    nodes = _read().get("nodes", {})
    if isinstance(nodes, dict):
        return nodes.get(nid)
    return next((n for n in nodes if n.get("id") == nid), None)

def _update_node(nid, updates):
    if USE_FB:
        firebase_db.reference(f"/nodes/{nid}").update(updates)
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
    try:
        data = _get_col("nodes")
        if not data:
            return jsonify([])
        return jsonify(list(data.values()) if isinstance(data, dict) else data)
    except Exception as e:
        print(f"[/nodes] Error: {e}")
        return jsonify([])


@app.route("/allocate", methods=["POST"])
def allocate():
    try:
        data = _get_col("nodes")
        hospitals = list(data.values()) if isinstance(data, dict) else data

        if not hospitals:
            return jsonify({"error": "No hospital data found"}), 400

        slime_result  = slime_allocate(hospitals)
        gemini_result = get_allocation_plan(hospitals, slime_result)

        blockchain_hashes = []
        if BLOCKCHAIN_ENABLED:
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
    except Exception as e:
        print(f"[/allocate] Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/update-node", methods=["POST"])
def update_node():
    try:
        body         = request.json
        node_id      = body.get("id")
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
        return jsonify({
            "success": True,
            "threat_detected": False,
            "node_id": node_id,
            "new_scarcity": new_scarcity
        })
    except Exception as e:
        print(f"[/update-node] Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/threats", methods=["GET"])
def get_threats():
    try:
        data = _get_col("threats")
        if not data:
            return jsonify([])
        threats = list(data.values()) if isinstance(data, dict) else data
        return jsonify(sorted(threats, key=lambda x: x.get("timestamp", ""), reverse=True))
    except Exception as e:
        return jsonify([])


@app.route("/history", methods=["GET"])
def get_history():
    try:
        data = _get_col("allocations")
        if not data:
            return jsonify([])
        items = list(data.values()) if isinstance(data, dict) else data
        return jsonify(items[-10:])
    except Exception as e:
        return jsonify([])


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "firebase": USE_FB,
        "blockchain": BLOCKCHAIN_ENABLED,
        "timestamp": datetime.now().isoformat()
    })


@app.route("/")
def serve_index():
    frontend = os.path.join(BASE_DIR, "../frontend")
    return send_from_directory(frontend, "index.html")


@app.route("/<path:path>")
def serve_static(path):
    frontend = os.path.join(BASE_DIR, "../frontend")
    return send_from_directory(frontend, path)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)