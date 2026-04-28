"""
PlasmaGrid — Hexa AI Engine
Primary:   Gemini 2.0 Flash Lite  (Google)
Backup 1:  Groq Llama 3.3         (Meta via Groq)
Backup 2:  OpenRouter Llama       (OpenRouter)
Backup 3:  Together AI            (Together)
Backup 4:  Hugging Face           (HuggingFace Inference)
Backup 5:  Mistral AI             (Mistral)

Automatic failover — if one hits rate limit, next activates instantly.
"""
import os
import json
import requests as _requests
from dotenv import load_dotenv

load_dotenv()

# ── GEMINI ────────────────────────────────────────────────
try:
    from google import genai as google_genai
    _gemini_client = google_genai.Client(api_key=os.getenv("GEMINI_KEY", ""))
    _GEMINI_OK = bool(os.getenv("GEMINI_KEY"))
except Exception:
    _gemini_client = None
    _GEMINI_OK = False

# ── GROQ ──────────────────────────────────────────────────
try:
    from groq import Groq
    _groq_client = Groq(api_key=os.getenv("GROQ_KEY", ""))
    _GROQ_OK = bool(os.getenv("GROQ_KEY"))
except Exception:
    _groq_client = None
    _GROQ_OK = False

# ── OPENROUTER ────────────────────────────────────────────
_OPENROUTER_KEY = os.getenv("OPENROUTER_KEY", "")
_OPENROUTER_OK  = bool(_OPENROUTER_KEY)

# ── TOGETHER AI ───────────────────────────────────────────
_TOGETHER_KEY = os.getenv("TOGETHER_KEY", "")
_TOGETHER_OK  = bool(_TOGETHER_KEY)

# ── HUGGING FACE ──────────────────────────────────────────
_HF_KEY = os.getenv("HF_KEY", "")
_HF_OK  = bool(_HF_KEY)

# ── MISTRAL ───────────────────────────────────────────────
_MISTRAL_KEY = os.getenv("MISTRAL_KEY", "")
_MISTRAL_OK  = bool(_MISTRAL_KEY)

# ─────────────────────────────────────────────────────────
active_ai = "none"

SYSTEM_PROMPT = (
    "You are PlasmaGrid AI — a real-time emergency resource allocation system "
    "for Karnataka state, India. You respond ONLY with valid JSON. "
    "No markdown. No backticks. No explanation. Pure JSON only."
)


def _clean_json(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
    return text.strip()


def _openai_post(url: str, api_key: str, model: str, prompt: str, extra_headers: dict = {}) -> str:
    resp = _requests.post(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            **extra_headers
        },
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt}
            ],
            "max_tokens": 1500,
            "temperature": 0.2,
        },
        timeout=30
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def ask_ai(prompt: str) -> tuple[str, str]:
    global active_ai

    # ── 1. GEMINI 2.0 Flash Lite ──────────────────────────
    if _GEMINI_OK and _gemini_client:
        try:
            print("[AI] Trying Gemini 2.0 Flash Lite...")
            resp = _gemini_client.models.generate_content(
                model="gemini-2.0-flash-lite",
                contents=f"{SYSTEM_PROMPT}\n\n{prompt}"
            )
            text = _clean_json(resp.text)
            active_ai = "Gemini 2.0 Flash Lite"
            print("[AI] Gemini responded ✓")
            return text, "Gemini 2.0 Flash Lite"
        except Exception as e:
            print(f"[AI] Gemini failed: {e}")

    # ── 2. GROQ Llama 3.3 70B ─────────────────────────────
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

    # ── 3. OPENROUTER Llama 3.1 8B Free ───────────────────
    if _OPENROUTER_OK:
        try:
            print("[AI] Trying OpenRouter...")
            text = _clean_json(_openai_post(
                url="https://openrouter.ai/api/v1/chat/completions",
                api_key=_OPENROUTER_KEY,
                model="meta-llama/llama-3.1-8b-instruct:free",
                prompt=prompt,
                extra_headers={
                    "HTTP-Referer": "https://plasmagrid.app",
                    "X-Title": "PlasmaGrid"
                }
            ))
            active_ai = "OpenRouter Llama 3.1"
            print("[AI] OpenRouter responded ✓")
            return text, "OpenRouter Llama 3.1"
        except Exception as e:
            print(f"[AI] OpenRouter failed: {e}")

    # ── 4. TOGETHER AI Llama 3 70B ────────────────────────
    if _TOGETHER_OK:
        try:
            print("[AI] Trying Together AI...")
            text = _clean_json(_openai_post(
                url="https://api.together.xyz/v1/chat/completions",
                api_key=_TOGETHER_KEY,
                model="meta-llama/Llama-3-70b-chat-hf",
                prompt=prompt
            ))
            active_ai = "Together Llama 3"
            print("[AI] Together AI responded ✓")
            return text, "Together Llama 3"
        except Exception as e:
            print(f"[AI] Together AI failed: {e}")

    # ── 5. HUGGING FACE Mistral 7B ────────────────────────
    if _HF_OK:
        try:
            print("[AI] Trying Hugging Face...")
            resp = _requests.post(
                "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {_HF_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "mistralai/Mistral-7B-Instruct-v0.3",
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user",   "content": prompt}
                    ],
                    "max_tokens": 1500,
                    "temperature": 0.2,
                },
                timeout=30
            )
            resp.raise_for_status()
            text = _clean_json(resp.json()["choices"][0]["message"]["content"])
            active_ai = "HuggingFace Mistral 7B"
            print("[AI] HuggingFace responded ✓")
            return text, "HuggingFace Mistral 7B"
        except Exception as e:
            print(f"[AI] HuggingFace failed: {e}")

    # ── 6. MISTRAL AI ─────────────────────────────────────
    if _MISTRAL_OK:
        try:
            print("[AI] Trying Mistral AI...")
            text = _clean_json(_openai_post(
                url="https://api.mistral.ai/v1/chat/completions",
                api_key=_MISTRAL_KEY,
                model="mistral-small-latest",
                prompt=prompt
            ))
            active_ai = "Mistral AI"
            print("[AI] Mistral AI responded ✓")
            return text, "Mistral AI"
        except Exception as e:
            print(f"[AI] Mistral AI failed: {e}")

    active_ai = "none"
    raise RuntimeError("All 6 AI services unavailable. Check your API keys.")


def get_allocation_plan(hospitals: list, slime_transfers: list) -> dict:
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
    print("\nPlasmaGrid Hexa AI Engine — Self Test")
    print("=" * 50)
    print(f"Gemini      : {'✓' if _GEMINI_OK else '✗'}")
    print(f"Groq        : {'✓' if _GROQ_OK else '✗'}")
    print(f"OpenRouter  : {'✓' if _OPENROUTER_OK else '✗'}")
    print(f"Together AI : {'✓' if _TOGETHER_OK else '✗'}")
    print(f"HuggingFace : {'✓' if _HF_OK else '✗'}")
    print(f"Mistral     : {'✓' if _MISTRAL_OK else '✗'}")

    hospitals = [
        {"id": "jayadeva", "name": "Jayadeva Institute of Cardiology",
         "city": "Bengaluru", "scarcity": 85, "beds_available": 4,
         "blood_units": 6, "ambulances": 2, "oxygen_cylinders": 3,
         "lat": 12.9250, "lng": 77.5938},
        {"id": "manipal_blr", "name": "Manipal Hospital",
         "city": "Bengaluru", "scarcity": 20, "beds_available": 60,
         "blood_units": 85, "ambulances": 10, "oxygen_cylinders": 55,
         "lat": 12.9592, "lng": 77.6489},
    ]

    print("\n[TEST] Allocation Plan")
    result = get_allocation_plan(hospitals, [])
    print(f"AI used  : {result.get('ai_used')}")
    print(f"Urgency  : {result.get('urgency')}")
    print(f"Summary  : {result.get('summary')}")

    print("\n[TEST] Threat Detection")
    threat = check_threat("Manipal Hospital", 20, 99, 5)
    print(f"AI used  : {threat.get('ai_used')}")
    print(f"Threat   : {threat.get('threat')}")
    print(f"Action   : {threat.get('action')}")
    print("\n✅ Hexa AI Engine test complete.")