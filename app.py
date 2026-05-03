"""
CivicGuide AI - Interactive Election Education Assistant
Powered by Google Gemini AI, deployed on Google Cloud Run
"""

import os
import json
import time
import hashlib
import logging
from flask import Flask, request, jsonify, render_template
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Security: validate API key exists at startup
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY not set - AI features will not work")

genai.configure(api_key=GEMINI_API_KEY)

# Google Gemini AI model configuration
model = genai.GenerativeModel(
    model_name="gemini-flash-latest",
    generation_config={
        "temperature": 0.7,
        "top_p": 0.8,
        "max_output_tokens": 1000,
    }
)

# Simple in-memory cache for efficiency
_cache = {}
CACHE_TTL = 3600  # 1 hour

SYSTEM_PROMPT = """You are CivicGuide AI — a friendly, expert civic education assistant specializing in election processes worldwide.

Your role:
- Explain election processes, timelines, voting steps, eligibility, registration, and results in simple, clear language
- Cover major democracies: India, USA, UK, EU countries, Australia, Canada, etc.
- Use analogies and simple language — imagine explaining to a first-time voter
- Be encouraging and non-partisan — never favor any political party
- Keep answers concise (2-4 short paragraphs max) unless asked for detail
- Use bullet points and emojis sparingly to aid clarity
- If asked about a specific country, give country-specific details
- Always end with an encouraging note about civic participation

You do NOT:
- Endorse any candidate, party, or political ideology
- Give legal advice
- Make predictions about election outcomes

Format: Use markdown. Keep it conversational and warm."""

SUPPORTED_COUNTRIES = [
    "India", "United States", "United Kingdom", "Australia",
    "Canada", "Germany", "France", "Japan", "Brazil", "General"
]

def get_cache_key(data):
    return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()

def get_from_cache(key):
    if key in _cache:
        value, timestamp = _cache[key]
        if time.time() - timestamp < CACHE_TTL:
            return value
        del _cache[key]
    return None

def set_cache(key, value):
    _cache[key] = (value, time.time())

def validate_country(country):
    if not country or not isinstance(country, str):
        return "General"
    country = country.strip()[:50]
    return country if country in SUPPORTED_COUNTRIES else "General"

def validate_message(message):
    if not message or not isinstance(message, str):
        return None
    message = message.strip()
    if len(message) > 1000:
        return None
    return message

def build_gemini_history(messages):
    history = []
    for msg in messages[:-1]:
        if msg.get("role") in ["user", "assistant"] and msg.get("content"):
            role = "user" if msg["role"] == "user" else "model"
            history.append({"role": role, "parts": [str(msg["content"])[:500]]})
    return history


# ─── ROUTES ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the main application."""
    return render_template("index.html")


@app.route("/health")
def health():
    """Health check endpoint for Cloud Run monitoring."""
    return jsonify({
        "status": "healthy",
        "service": "CivicGuide AI",
        "version": "2.0.0",
        "ai_provider": "Google Gemini",
        "model": "gemini-flash-latest",
        "api_configured": bool(GEMINI_API_KEY)
    }), 200


@app.route("/chat", methods=["POST"])
def chat():
    """AI chat endpoint powered by Google Gemini."""
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    messages = data.get("messages", [])
    country = validate_country(data.get("country", "General"))

    if not messages or not isinstance(messages, list):
        return jsonify({"error": "Messages array is required"}), 400

    if len(messages) > 20:
        messages = messages[-20:]

    last_msg = validate_message(messages[-1].get("content", ""))
    if not last_msg:
        return jsonify({"error": "Invalid message content"}), 400

    cache_key = get_cache_key({"msg": last_msg, "country": country})
    cached = get_from_cache(cache_key)
    if cached:
        logger.info("Cache hit for chat request")
        return jsonify({"reply": cached})

    contextualized_msg = f"[Context: User is asking about elections in {country}]\n\n{last_msg}"

    try:
        history = build_gemini_history(messages)
        chat_session = model.start_chat(
            history=[
                {"role": "user", "parts": [SYSTEM_PROMPT]},
                {"role": "model", "parts": ["Understood! I'm CivicGuide AI, ready to help explain elections clearly and impartially."]}
            ] + history
        )
        response = chat_session.send_message(contextualized_msg)
        reply = response.text
        set_cache(cache_key, reply)
        logger.info(f"Chat response for country: {country}")
        return jsonify({"reply": reply})

    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/timeline", methods=["GET"])
def timeline():
    """Generate election timeline using Google Gemini AI."""
    country = validate_country(request.args.get("country", "India"))

    cache_key = get_cache_key({"timeline": country})
    cached = get_from_cache(cache_key)
    if cached:
        logger.info(f"Cache hit for timeline: {country}")
        return jsonify({"steps": cached, "country": country, "cached": True})

    prompt = f"""Return a JSON array of election timeline steps for {country}'s general/national elections.
Each step must have:
- "step": step number (1-based integer)
- "title": short title (3-5 words)
- "description": one clear sentence explanation for a first-time voter
- "icon": a single relevant emoji
- "duration": typical timeframe (e.g., "60 days before election")
- "phase": exactly one of: "preparation", "campaign", "voting", "results"

Rules:
- Return ONLY a valid JSON array
- No markdown, no code fences, no explanation text
- 6 to 8 steps total
- Make it educational and easy to understand"""

    try:
        response = model.generate_content(prompt)
        raw = response.text.strip()
        if raw.startswith("```"):
            parts = raw.split("```")
            raw = parts[1] if len(parts) > 1 else raw
            if raw.startswith("json"):
                raw = raw[4:]
        steps = json.loads(raw.strip())
        if not isinstance(steps, list) or len(steps) == 0:
            raise ValueError("Invalid timeline structure")
        set_cache(cache_key, steps)
        logger.info(f"Timeline generated for: {country}")
        return jsonify({"steps": steps, "country": country, "cached": False})

    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {str(e)}")
        return jsonify({"error": "Failed to parse AI response. Please try again."}), 500
    except Exception as e:
        logger.error(f"Timeline error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method not allowed"}), 405

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
