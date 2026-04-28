"""
PlasmaGrid — Triple AI Engine
Primary:  Gemini 2.0 Flash  (Google)
Backup 1: Groq Llama 3.3    (Meta via Groq)
Backup 2: Cohere Command-R  (Cohere)

Automatic failover — if one hits rate limit, next activates instantly.
"""
import os
import json
from dotenv import load_dotenv

load_dotenv()

# ── Configure AI clients ──────────────────────────────────
try:
    from google import genai as google_genai
    _gemini_client = google_genai.Client(api_key=os.getenv("GEMINI_KEY", ""))
    _GEMINI_OK = bool(os.getenv("GEMINI_KEY"))
except Exception:
    _gemini_client = None
    _GEMINI_OK = False

try:
    from groq import Groq
    _groq_client = Groq(api_key=os.getenv("GROQ_KEY", ""))
    _GROQ_OK = bool(os.getenv("GROQ_KEY"))
except Exception:
    _groq_client = None
    _GROQ_OK = False

try:
    import cohere
    _cohere_client = cohere.Client(api_key=os.getenv("COHERE_KEY", ""))
    _COHERE_OK = bool(os.getenv("COHERE_KEY"))
except Exception:
    _cohere_client = None
    _COHERE_OK = False

active_ai = "none"

SYSTEM_PROMPT = (
    "You are PlasmaGrid AI — a real-time emergency resource allocation system "
    "for Karnataka state, India. You respond ONLY with valid JSON. "
    "No markdown. No backticks. No explanation. Pure JSON only."
)


def _clean_json(text: str) -> str:
    """Strip markdown fences if model adds them despite instructions."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
    return text.strip()


def ask_ai(prompt: str) -> tuple[str, str]:
    """
    Tries Gemini → Groq → Cohere in order.
    Returns (response_text, ai_name_used).
    Raises Exception if all fail.
    """
    global active_ai

    # ── PRIMARY: Gemini 2.0 Flash ─────────────────────────
    if _GEMINI_OK and _gemini_client:
        try:
            print("[AI] Trying Gemini 2.0 Flash...")
            resp = _gemini_client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"{SYSTEM_PROMPT}\n\n{prompt}"
            )
            text = _clean_json(resp.text)
            active_ai = "Gemini 2.0 Flash"
            print("[AI] Gemini responded ✓")
            return text, "Gemini 2.0 Flash"
        except Exception as e:
            print(f"[AI] Gemini failed: {e}")

    # ── BACKUP 1: Groq Llama 3.3 ─────────────────────────
    if _GROQ_OK and _groq_client:
        try:
            print("[AI] Trying Groq Llama 3.3-70B...")
            chat = _groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.2,
            )
            text = _clean_json(chat.choices[0].message.content)
            active_ai = "Groq Llama 3.3"
            print("[AI] Groq responded ✓")
            return text, "Groq Llama 3.3"
        except Exception as e:
            print(f"[AI] Groq failed: {e}")

    # ── BACKUP 2: Cohere Command-R ────────────────────────
    if _COHERE_OK and _cohere_client:
        try:
            print("[AI] Trying Cohere Command-R...")
            resp = _cohere_client.chat(
                model="command-r",
                message=prompt,
                preamble=SYSTEM_PROMPT,
            )
            text = _clean_json(resp.text)
            active_ai = "Cohere Command-R"
            print("[AI] Cohere responded ✓")
            return text, "Cohere Command-R"
        except Exception as e:
            print(f"[AI] Cohere failed: {e}")

    active_ai = "none"
    raise RuntimeError("All AI services unavailable. Check your API keys in .env")


def get_allocation_plan(hospitals: list, slime_transfers: list) -> dict:
    """
    Analyses Karnataka hospital network and returns AI allocation plan.
    Combines biological routing (slime) with AI reasoning (Gemini/Groq/Cohere).
    """
    prompt = f"""
You are analysing Karnataka's emergency medical resource network.

HOSPITAL NETWORK STATE (scarcity: 0=surplus, 100=critical):
{json.dumps(hospitals, indent=2)}

BIOLOGICAL ROUTING (Physarum slime mould algorithm output):
{json.dumps(slime_transfers, indent=2)}

Analyse and return ONLY this JSON structure:
{{
  "urgency": "LOW|MEDIUM|HIGH|CRITICAL",
  "summary": "one sentence describing the Karnataka network situation right now",
  "transfers": [
    {{
      "from": "hospital name",
      "to": "hospital name",
      "resource": "blood_units|ambulances|oxygen_cylinders|beds",
      "amount": <integer>,
      "reason": "plain English clinical reason for this transfer",
      "estimated_time_minutes": <integer>
    }}
  ],
  "priority_message": "one urgent sentence for coordinators",
  "lives_at_risk": <integer>,
  "cities_affected": ["city1", "city2"]
}}
"""
    text, ai_used = ask_ai(prompt)
    try:
        result = json.loads(text)
        result["ai_used"] = ai_used
        return result
    except json.JSONDecodeError as e:
        print(f"[AI] JSON parse error: {e} | Raw: {text[:300]}")
        return {
            "urgency": "HIGH",
            "summary": f"AI responded ({ai_used}) but output could not be parsed. Manual review required.",
            "transfers": [],
            "priority_message": "System degraded — manual coordination required.",
            "lives_at_risk": 0,
            "cities_affected": [],
            "ai_used": ai_used,
        }


def check_threat(node_name: str, old_score: int, new_score: int, time_seconds: int = 30) -> dict:
    """
    Cybersecurity immune layer.
    Analyses whether a data change is legitimate or a cyberattack.
    """
    prompt = f"""
You are PlasmaGrid's zero-trust cybersecurity immune layer.
Protect Karnataka's emergency resource network from data spoofing.

ANOMALY DETECTED:
- Node: {node_name}
- Scarcity changed: {old_score} → {new_score}
- Time elapsed: {time_seconds} seconds
- Change magnitude: {abs(new_score - old_score)} points

RULE: A legitimate hospital scarcity change > 40 points in < 60 seconds
is physically impossible. No real hospital can discharge or admit that many
patients that quickly.

Return ONLY this JSON:
{{
  "threat": <true|false>,
  "confidence": <0-100>,
  "threat_type": "SPOOFED_DATA|RANSOMWARE|SENSOR_FAULT|LEGITIMATE",
  "reason": "plain English explanation of your analysis",
  "action": "QUARANTINE|MONITOR|CLEAR"
}}
"""
    text, ai_used = ask_ai(prompt)
    try:
        result = json.loads(text)
        result["ai_used"] = ai_used
        return result
    except json.JSONDecodeError:
        return {
            "threat": False,
            "confidence": 0,
            "threat_type": "UNKNOWN",
            "reason": "AI parsing error — manual review required",
            "action": "MONITOR",
            "ai_used": ai_used,
        }


# ── Self-test ─────────────────────────────────────────────
if __name__ == "__main__":
    print("\nPlasmaGrid Triple AI Engine — Self Test")
    print("=" * 50)

    hospitals = [
        {"id": "jayadeva", "name": "Jayadeva Institute of Cardiology",
         "city": "Bengaluru", "area": "Jayanagar", "type": "government",
         "lat": 12.9250, "lng": 77.5938, "scarcity": 85,
         "beds_available": 4, "blood_units": 6, "ambulances": 2, "oxygen_cylinders": 3},
        {"id": "manipal_blr", "name": "Manipal Hospital",
         "city": "Bengaluru", "area": "Old Airport Road", "type": "private",
         "lat": 12.9592, "lng": 77.6489, "scarcity": 20,
         "beds_available": 60, "blood_units": 85, "ambulances": 10, "oxygen_cylinders": 55},
        {"id": "victoria", "name": "Victoria Hospital",
         "city": "Bengaluru", "area": "Kalasipalya", "type": "government",
         "lat": 12.9634, "lng": 77.5855, "scarcity": 72,
         "beds_available": 8, "blood_units": 12, "ambulances": 3, "oxygen_cylinders": 5},
    ]

    print("\n[TEST 1] Allocation Plan")
    print("-" * 30)
    result = get_allocation_plan(hospitals, [])
    print(f"AI used      : {result.get('ai_used')}")
    print(f"Urgency      : {result.get('urgency')}")
    print(f"Summary      : {result.get('summary')}")
    print(f"Transfers    : {len(result.get('transfers', []))}")
    print(f"Lives at risk: {result.get('lives_at_risk')}")

    print("\n[TEST 2] Threat Detection")
    print("-" * 30)
    threat = check_threat("Manipal Hospital", 20, 99, 5)
    print(f"AI used    : {threat.get('ai_used')}")
    print(f"Threat     : {threat.get('threat')}")
    print(f"Type       : {threat.get('threat_type')}")
    print(f"Confidence : {threat.get('confidence')}%")
    print(f"Action     : {threat.get('action')}")
    print(f"Reason     : {threat.get('reason')}")
    print("\n✅ AI Engine test complete.")