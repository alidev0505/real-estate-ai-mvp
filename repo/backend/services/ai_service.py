"""LLM access. Provider is selected with AI_PROVIDER (anthropic | openai | gemini)."""
import json
import logging
import os
import requests
from config import Config

log = logging.getLogger(__name__)
PROMPT_PATH = os.path.join(os.path.dirname(__file__), "..", "prompts", "real_estate_agent.txt")
TIMEOUT = 45


class AIError(Exception):
    pass


def _system_prompt(profile):
    with open(PROMPT_PATH, encoding="utf-8") as f:
        base = f.read()
    return base + "\n\nCURRENT LEAD PROFILE (already collected):\n" + json.dumps(profile)


def _clean_history(history):
    """Providers need user-first, alternating roles."""
    out = []
    for m in history:
        if not out and m["role"] != "user":
            continue
        if out and out[-1]["role"] == m["role"]:
            out[-1]["content"] += "\n" + m["content"]
        else:
            out.append({"role": m["role"], "content": m["content"]})
    return out


def call_llm(system, messages):
    key, model = Config.AI_API_KEY, Config.AI_MODEL
    p = Config.AI_PROVIDER
    if p == "anthropic":
        r = requests.post("https://api.anthropic.com/v1/messages", timeout=TIMEOUT,
                          headers={"x-api-key": key, "anthropic-version": "2023-06-01"},
                          json={"model": model, "max_tokens": 800, "system": system, "messages": messages})
        r.raise_for_status()
        return "".join(b.get("text", "") for b in r.json()["content"])
    if p == "openai":
        r = requests.post("https://api.openai.com/v1/chat/completions", timeout=TIMEOUT,
                          headers={"Authorization": f"Bearer {key}"},
                          json={"model": model, "response_format": {"type": "json_object"},
                                "messages": [{"role": "system", "content": system}] + messages})
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    if p == "gemini":
        r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                          timeout=TIMEOUT, headers={"x-goog-api-key": key},
                          json={"systemInstruction": {"parts": [{"text": system}]},
                                "generationConfig": {"responseMimeType": "application/json"},
                                "contents": [{"role": "model" if m["role"] == "assistant" else "user",
                                              "parts": [{"text": m["content"]}]} for m in messages]})
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]
    raise AIError(f"Unknown AI_PROVIDER '{p}'")


def _parse(raw):
    start, end = raw.find("{"), raw.rfind("}")
    if start < 0 or end < 0:
        raise AIError("Model did not return JSON")
    data = json.loads(raw[start:end + 1])
    if not isinstance(data.get("reply"), str) or not data["reply"].strip():
        raise AIError("Model returned no reply")
    data["extracted_data"] = data.get("extracted_data") or {}
    return data


def chat_turn(history, profile):
    """history: [{'role','content'}] ending with the new user message. Returns parsed dict."""
    if not Config.ai_configured():
        raise AIError("AI_API_KEY / AI_MODEL are not configured")
    try:
        raw = call_llm(_system_prompt(profile), _clean_history(history))
        return _parse(raw)
    except (requests.RequestException, KeyError, IndexError, ValueError) as e:
        log.exception("AI call failed")
        raise AIError(str(e)) from e
