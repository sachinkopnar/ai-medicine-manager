"""
ai_backend.py - AI inference backend for AI Medicine Manager
Supports:
  - Ollama (local inference, no API key needed)
  - OpenAI (BYOK)
  - Anthropic Claude (BYOK)
  - Google Gemini (BYOK)
  - Groq (BYOK or env-var key)

All calls use only stdlib + groq SDK - no openai/anthropic SDKs required.
Every provider returns (success: bool, text_or_error: str).
"""

import json
import re
import urllib.request
import urllib.error
from typing import Optional
import os

# ── Groq SDK (optional - graceful fallback to HTTP if not installed) ──────────
try:
    from groq import Groq as _GroqClient
    _GROQ_SDK = True
except ImportError:
    _GroqClient = None  # type: ignore
    _GROQ_SDK = False

# ── Provider constants ────────────────────────────────────────────────────────
PROVIDER_OLLAMA    = "Ollama (Local)"
PROVIDER_OPENAI    = "OpenAI (BYOK)"
PROVIDER_ANTHROPIC = "Anthropic Claude (BYOK)"
PROVIDER_GEMINI    = "Google Gemini (BYOK)"
PROVIDER_GROQ      = "Groq (Cloud)"

ALL_PROVIDERS = [
    PROVIDER_OLLAMA,
    PROVIDER_GROQ,
    PROVIDER_OPENAI,
    PROVIDER_ANTHROPIC,
    PROVIDER_GEMINI,
]

# Default Ollama models to suggest
DEFAULT_OLLAMA_MODELS = [
    "llama3.2", "llama3.1", "llama3", "llama2",
    "mistral", "mistral-nemo", "mixtral",
    "gemma2", "gemma",
    "phi3", "phi3.5",
    "qwen2.5", "qwen2",
    "deepseek-r1",
    "medllama2",
]

OPENAI_MODELS    = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]
ANTHROPIC_MODELS = ["claude-haiku-4-5-20251001", "claude-sonnet-4-6", "claude-opus-4-6"]
GEMINI_MODELS    = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
GROQ_MODELS      = [
    "llama-3.3-70b-versatile",
    "llama3-70b-8192",
    "llama3-8b-8192",
    "mixtral-8x7b-32768",
]


# ── Internal helper ────────────────────────────────────────────────────────────

def _http_post(url: str, payload: dict, headers: dict, timeout: int = 60) -> dict:
    """
    Thin urllib wrapper for JSON POST.
    Raises urllib.error.HTTPError / URLError on failure.
    Always returns parsed JSON dict.
    """
    data = json.dumps(payload).encode("utf-8")
    req  = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _http_get(url: str, headers: Optional[dict] = None, timeout: int = 5) -> dict:
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _http_error_msg(e: urllib.error.HTTPError) -> str:
    try:
        body = json.loads(e.read().decode())
        # OpenAI / Anthropic / Groq error format
        return (
            body.get("error", {}).get("message")
            or body.get("error", {}).get("msg")
            or body.get("message")
            or str(body)[:300]
        )
    except Exception:
        return f"HTTP {e.code}"


# ── Ollama ─────────────────────────────────────────────────────────────────────

def get_ollama_models(base_url: str = "http://localhost:11434") -> list[str]:
    """Fetch available models from a running Ollama instance."""
    try:
        data = _http_get(f"{base_url.rstrip('/')}/api/tags")
        return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []


def is_ollama_running(base_url: str = "http://localhost:11434") -> bool:
    try:
        _http_get(f"{base_url.rstrip('/')}/api/tags", timeout=2)
        return True
    except Exception:
        return False


def call_ollama(
    prompt: str,
    model: str = "phi3:mini",
    system: str = "",
    base_url: str = "http://localhost:11434",
    temperature: float = 0.3,
) -> tuple[bool, str]:
    """Call Ollama /api/chat. Returns (success, text_or_error)."""
    try:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        data = _http_post(
            f"{base_url.rstrip('/')}/api/chat",
            payload={
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {"temperature": temperature},
            },
            headers={"Content-Type": "application/json"},
            timeout=120,
        )
        return True, data["message"]["content"]
    except urllib.error.URLError as e:
        return False, f"Ollama connection error: {e.reason}. Is Ollama running at {base_url}?"
    except KeyError:
        return False, "Ollama returned an unexpected response format."
    except Exception as e:
        return False, f"Ollama error: {str(e)}"


# ── OpenAI ─────────────────────────────────────────────────────────────────────

def call_openai(
    prompt: str,
    api_key: str,
    model: str = "gpt-4o-mini",
    system: str = "",
    temperature: float = 0.3,
) -> tuple[bool, str]:
    if not api_key:
        return False, "OpenAI API key not provided. Please add it in AI Settings."
    try:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        data = _http_post(
            "https://api.openai.com/v1/chat/completions",
            payload={
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": 1500,
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
        )
        return True, data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        return False, f"OpenAI error {e.code}: {_http_error_msg(e)}"
    except urllib.error.URLError as e:
        return False, f"OpenAI network error: {e.reason}"
    except (KeyError, IndexError):
        return False, "OpenAI returned an unexpected response format."
    except Exception as e:
        return False, f"OpenAI error: {str(e)}"


# ── Anthropic ──────────────────────────────────────────────────────────────────

def call_anthropic(
    prompt: str,
    api_key: str,
    model: str = "claude-haiku-4-5-20251001",
    system: str = "",
    temperature: float = 0.3,
) -> tuple[bool, str]:
    if not api_key:
        return False, "Anthropic API key not provided. Please add it in AI Settings."
    try:
        body: dict = {
            "model": model,
            "max_tokens": 1500,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            body["system"] = system

        data = _http_post(
            "https://api.anthropic.com/v1/messages",
            payload=body,
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            },
        )
        return True, data["content"][0]["text"]
    except urllib.error.HTTPError as e:
        return False, f"Anthropic error {e.code}: {_http_error_msg(e)}"
    except urllib.error.URLError as e:
        return False, f"Anthropic network error: {e.reason}"
    except (KeyError, IndexError):
        return False, "Anthropic returned an unexpected response format."
    except Exception as e:
        return False, f"Anthropic error: {str(e)}"


# ── Google Gemini ──────────────────────────────────────────────────────────────

def call_gemini(
    prompt: str,
    api_key: str,
    model: str = "gemini-2.0-flash",
    system: str = "",
    temperature: float = 0.3,
) -> tuple[bool, str]:
    if not api_key:
        return False, "Gemini API key not provided. Please add it in AI Settings."
    try:
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        data = _http_post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}",
            payload={
                "contents": [{"parts": [{"text": full_prompt}]}],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": 1500,
                },
            },
            headers={"Content-Type": "application/json"},
        )
        # Handle safety blocks
        candidates = data.get("candidates", [])
        if not candidates:
            reason = data.get("promptFeedback", {}).get("blockReason", "Unknown")
            return False, f"Gemini blocked the request: {reason}"
        
        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            finish = candidates[0].get("finishReason", "UNKNOWN")
            return False, f"Gemini returned no content (finishReason: {finish})"
        
        return True, parts[0]["text"]
    except urllib.error.HTTPError as e:
        return False, f"Gemini error {e.code}: {_http_error_msg(e)}"
    except urllib.error.URLError as e:
        return False, f"Gemini network error: {e.reason}"
    except (KeyError, IndexError) as e:
        return False, f"Gemini returned an unexpected response format: {e}"
    except Exception as e:
        return False, f"Gemini error: {str(e)}"


# ── Groq ───────────────────────────────────────────────────────────────────────

def call_groq(
    prompt: str,
    api_key: str,
    model: str = "llama-3.3-70b-versatile",
    system: str = "",
    temperature: float = 0.3,
) -> tuple[bool, str]:
    """
    Call Groq. Tries the groq SDK first; falls back to direct HTTP if SDK
    is not installed. This ensures it works on Hugging Face Spaces where
    the groq package might not be in requirements.
    """
    if not api_key:
        return False, "Groq API key not provided. Set GROQ_API_KEY env var or add it in AI Settings."

    # ── SDK path ──────────────────────────────────────────────────────────────
    if _GROQ_SDK and _GroqClient is not None:
        try:
            client = _GroqClient(api_key=api_key)
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=1500,
            )
            return True, resp.choices[0].message.content
        except Exception as e:
            # If SDK call fails, fall through to HTTP path
            sdk_err = str(e)
    else:
        sdk_err = "groq SDK not installed"

    # ── HTTP fallback (no SDK required) ───────────────────────────────────────
    try:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        data = _http_post(
            "https://api.groq.com/openai/v1/chat/completions",
            payload={
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": 1500,
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
        )
        return True, data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        err = _http_error_msg(e)
        return False, f"Groq error {e.code}: {err}"
    except urllib.error.URLError as e:
        return False, f"Groq network error: {e.reason}. (SDK error was: {sdk_err})"
    except (KeyError, IndexError):
        return False, "Groq returned an unexpected response format."
    except Exception as e:
        return False, f"Groq error: {str(e)} (SDK error: {sdk_err})"


# ── Unified dispatcher ─────────────────────────────────────────────────────────

def call_ai(
    prompt: str,
    provider: str,
    model: str,
    api_key: str = "",
    system: str = "",
    ollama_url: str = "http://localhost:11434",
    temperature: float = 0.3,
) -> tuple[bool, str]:
    """Route to the correct backend based on provider name."""
    if provider == PROVIDER_OLLAMA:
        return call_ollama(prompt, model=model, system=system,
                           base_url=ollama_url, temperature=temperature)
    elif provider == PROVIDER_OPENAI:
        return call_openai(prompt, api_key=api_key, model=model,
                           system=system, temperature=temperature)
    elif provider == PROVIDER_ANTHROPIC:
        return call_anthropic(prompt, api_key=api_key, model=model,
                              system=system, temperature=temperature)
    elif provider == PROVIDER_GEMINI:
        return call_gemini(prompt, api_key=api_key, model=model,
                           system=system, temperature=temperature)
    elif provider == PROVIDER_GROQ:
        return call_groq(prompt, api_key=api_key, model=model,
                         system=system, temperature=temperature)
    else:
        return False, f"Unknown AI provider: '{provider}'. Please select a valid provider in AI Settings."


# ── System prompts ─────────────────────────────────────────────────────────────

SYSTEM_HEALTH_ASSISTANT = """\
You are a helpful medication management assistant.
You provide clear, concise, evidence-based information about medications.
Always remind users to consult their healthcare provider for medical decisions.
Keep responses concise and practical. Format with simple markdown when helpful.
Never diagnose conditions or replace professional medical advice.\
"""


# ── Feature prompts ────────────────────────────────────────────────────────────

def ai_analyze_interactions(medicines: list[dict]) -> str:
    med_list = "\n".join(
        f"- {m['name']} {m['dosage']} ({m['frequency']})" for m in medicines
    )
    return f"""Analyze the following medications for potential drug interactions:

{med_list}

Please provide:
1. Any notable drug-drug interactions (flag HIGH/MEDIUM/LOW risk)
2. General safety notes about this combination
3. Any timing recommendations (e.g., take X hours apart)
4. Foods or substances to avoid while on these medications

Keep it concise and practical. Always end with: "Consult your pharmacist or doctor before making changes."
"""


def ai_explain_medicine(name: str, dosage: str, frequency: str, notes: str) -> str:
    return f"""Provide a clear patient-friendly explanation for this medication:

Name: {name}
Dosage: {dosage}
Frequency: {frequency}
Notes: {notes or 'None'}

Please include:
1. What this medication is typically used for
2. How to take it correctly (with/without food, timing tips)
3. Common side effects to watch for
4. Important warnings or precautions
5. What to do if a dose is missed

Keep it friendly and easy to understand for a non-medical person."""


def ai_adherence_insights(stats: dict, weekly: dict, medicines: list[dict]) -> str:
    total_week = sum(v["taken"] + v["missed"] for v in weekly.values())
    taken_week = sum(v["taken"] for v in weekly.values())
    week_pct   = round(taken_week / total_week * 100) if total_week > 0 else 0

    missed_details = [
        f"  {day}: {v['missed']} missed"
        for day, v in weekly.items() if v["missed"] > 0
    ]
    med_names = [m["name"] for m in medicines[:10]]

    return f"""Analyze this patient's medication adherence and provide personalized coaching:

Current medications: {', '.join(med_names) if med_names else 'None'}
Today's adherence: {stats.get('adherence_pct', 0)}%
7-day adherence: {week_pct}%
Today: {stats.get('today_taken', 0)} taken, {stats.get('today_missed', 0)} missed, {stats.get('today_pending', 0)} pending

Missed doses this week:
{chr(10).join(missed_details) if missed_details else '  None - great job!'}

Please provide:
1. A brief assessment of their adherence pattern
2. 2-3 specific, actionable tips to improve consistency
3. Encouragement tailored to their situation
4. Any timing strategies that might help

Be supportive and motivating, not judgmental."""


def ai_ocr_enhance(raw_text: str) -> str:
    return f"""You are a medical prescription parser. Extract structured information from this OCR-scanned prescription text.

RAW OCR TEXT:
---
{raw_text[:3000]}
---

Extract and return a JSON object with this exact structure:
{{
  "medicines": [
    {{
      "name": "medicine name",
      "dosage": "e.g. 500mg",
      "frequency": "e.g. Twice daily",
      "duration": "e.g. 7 days",
      "instructions": "e.g. Take after meals"
    }}
  ],
  "patient_name": "if found or null",
  "doctor_name": "if found or null",
  "date": "if found or null",
  "notes": "any other relevant info or null"
}}

Return ONLY the JSON, no explanation, no markdown fences. If a field is not found, use null."""


def parse_ai_ocr_json(text: str) -> Optional[dict]:
    """Try to parse JSON from AI OCR response."""
    # Strip markdown code fences
    text = re.sub(r"```(?:json)?", "", text).strip().rstrip("`").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    return None


def ai_suggest_schedule(medicines: list[dict]) -> str:
    med_list = "\n".join(
        f"- {m['name']} {m['dosage']} ({m['frequency']}) - current times: {', '.join(m.get('times', []))}"
        for m in medicines
    )
    return f"""Suggest an optimized daily medication schedule for this patient:

{med_list}

Consider:
- Minimizing drug interactions by spacing doses appropriately
- Aligning with meal times where beneficial
- Grouping doses when safe to improve adherence
- Sleep/wake cycle (assume 7am wake, 11pm sleep)

Provide a practical hour-by-hour schedule and brief reasoning for each grouping.
Keep it concise and actionable."""
