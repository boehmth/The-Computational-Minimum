"""
common/llm.py — one small chat() function.

Two backends supported:

    LLM_BACKEND=sap      SAP GenAI Hub  (OpenAI / Anthropic / Gemini deployments
                                          — reuses AICORE_* from the RPT Agent .env)
    LLM_BACKEND=gemini   Google Gemini via the google-genai SDK  (fallback)

Both return the same shape:

    Response(text, thinking, tokens_in, tokens_out, tokens_thinking,
             raw, backend, model)

Kept deliberately dependency-light: only `requests` and the Python
standard library on the SAP path.  Gemini is imported lazily so the
module loads even if google-genai is not installed.
"""

from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

try:
    from dotenv import load_dotenv
    # Look for a .env starting at the RPT Agent repo root (two levels up
    # from this file: Agentic Systems/common/llm.py -> RPT Agent/.env)
    _ROOT = Path(__file__).resolve().parent.parent.parent
    _ENV = _ROOT / ".env"
    if _ENV.exists():
        load_dotenv(_ENV)
    else:
        load_dotenv()  # fall back to CWD
except Exception:
    pass


# ---------------------------------------------------------------------------
# Response shape
# ---------------------------------------------------------------------------

@dataclass
class Response:
    text: str
    thinking: Optional[str] = None
    tokens_in:  int = 0
    tokens_out: int = 0
    tokens_thinking: int = 0
    raw: Dict[str, Any] = field(default_factory=dict)
    backend: str = ""
    model:   str = ""

    @property
    def tokens(self) -> int:
        return self.tokens_in + self.tokens_out

    @property
    def tokens_answer(self) -> int:
        return max(self.tokens_out - self.tokens_thinking, 0)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def chat(
    system: str,
    user: str,
    *,
    reasoning: Optional[str] = None,     # None | "minimal" | "medium" | "high"
    want_json: bool = False,
    model: Optional[str] = None,
    temperature: float = 0.2,
    max_tokens: int = 2048,
) -> Response:
    backend = (os.getenv("LLM_BACKEND") or "sap").strip().lower()
    if reasoning and not model:
        model = os.getenv("LLM_REASONING_MODEL")

    if backend == "gemini":
        return _chat_gemini(system, user, reasoning=reasoning,
                            want_json=want_json, model=model,
                            temperature=temperature, max_tokens=max_tokens)
    if backend == "sap":
        return _chat_sap(system, user, reasoning=reasoning,
                         want_json=want_json, model=model,
                         temperature=temperature, max_tokens=max_tokens)
    raise RuntimeError(f"Unknown LLM_BACKEND: {backend!r}")


# ---------------------------------------------------------------------------
# SAP GenAI Hub  — uses the same AICORE_* env vars as rpt_agent
# ---------------------------------------------------------------------------

_SAP_TOKEN: Dict[str, Any] = {"token": None, "expires_at": 0.0}
_SAP_DEPLOYMENTS: Dict[str, str] = {}


def _sap_env() -> Dict[str, str]:
    missing = []
    def _need(k):
        v = os.getenv(k)
        if not v:
            missing.append(k)
        return v
    env = {
        "AICORE_API_URL":       _need("AICORE_API_URL"),
        "AICORE_AUTH_URL":      _need("AICORE_AUTH_URL"),
        "AICORE_CLIENT_ID":     _need("AICORE_CLIENT_ID"),
        "AICORE_CLIENT_SECRET": _need("AICORE_CLIENT_SECRET"),
        "AICORE_RESOURCE_GROUP": os.getenv("AICORE_RESOURCE_GROUP", "default"),
    }
    if missing:
        raise RuntimeError(
            "SAP GenAI Hub is not configured.  Missing env vars: "
            + ", ".join(missing)
            + "\nSee ../README.md or ../.env.example for the required keys."
        )
    return env


def _sap_token() -> str:
    now = time.time()
    if _SAP_TOKEN["token"] and _SAP_TOKEN["expires_at"] - 60 > now:
        return _SAP_TOKEN["token"]
    env = _sap_env()
    r = requests.post(
        env["AICORE_AUTH_URL"].rstrip("/") + "/oauth/token",
        data={"grant_type": "client_credentials"},
        auth=(env["AICORE_CLIENT_ID"], env["AICORE_CLIENT_SECRET"]),
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    _SAP_TOKEN["token"] = data["access_token"]
    _SAP_TOKEN["expires_at"] = now + float(data.get("expires_in", 3600))
    return _SAP_TOKEN["token"]


def _sap_headers() -> Dict[str, str]:
    env = _sap_env()
    return {
        "Authorization": f"Bearer {_sap_token()}",
        "AI-Resource-Group": env["AICORE_RESOURCE_GROUP"],
        "Content-Type": "application/json",
    }


def _sap_api_url() -> str:
    url = _sap_env()["AICORE_API_URL"].rstrip("/")
    # tolerate both '.../v2' and '.../' — we always want /v2 at the end
    if not url.endswith("/v2"):
        url = url + "/v2"
    return url


def _sap_resolve_deployment(model: str) -> str:
    if model in _SAP_DEPLOYMENTS:
        return _SAP_DEPLOYMENTS[model]
    r = requests.get(
        f"{_sap_api_url()}/lm/deployments",
        headers=_sap_headers(),
        params={"scenarioId": "foundation-models", "status": "RUNNING"},
        timeout=30,
    )
    r.raise_for_status()
    for dep in r.json().get("resources", []) or []:
        details = dep.get("details") or {}
        m_name = (
            ((details.get("resources") or {}).get("backend_details") or {})
            .get("model", {})
            .get("name")
            or details.get("modelName")
        )
        if m_name == model:
            _SAP_DEPLOYMENTS[model] = dep["id"]
            return dep["id"]
    raise RuntimeError(
        f"No running SAP GenAI Hub deployment for model {model!r}.\n"
        "Discover deployed models with:  python -m rpt_agent.list_rpt_deployments"
    )


def _chat_sap(system, user, *, reasoning, want_json,
              model, temperature, max_tokens) -> Response:
    model = model or os.getenv("SAP_GENAI_MODEL") \
                  or os.getenv("LLM_MODEL", "gpt-4o")
    dep_id = _sap_resolve_deployment(model)
    base = f"{_sap_api_url()}/inference/deployments/{dep_id}"

    if model.startswith("anthropic--"):
        body: Dict[str, Any] = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        }
        if reasoning:
            budget = _reasoning_budget(reasoning)
            body["thinking"] = {"type": "enabled",
                                "budget_tokens": budget}
            body["max_tokens"] = max(max_tokens, budget + 2048)
        path = "/invoke"
    else:
        messages = [
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ]
        body = {"messages": messages, "temperature": temperature,
                "max_tokens": max_tokens}
        if reasoning and (model.startswith("o1") or model.startswith("o3")
                          or model.startswith("o4")):
            body["reasoning_effort"] = reasoning
        if want_json:
            body["response_format"] = {"type": "json_object"}
        api_version = os.getenv("SAP_GENAI_OPENAI_API_VERSION", "2023-05-15")
        path = f"/chat/completions?api-version={api_version}"

    r = requests.post(base + path, headers=_sap_headers(),
                      json=body, timeout=180)
    if r.status_code >= 400:
        raise RuntimeError(
            f"SAP GenAI Hub returned HTTP {r.status_code} for {model!r}\n"
            f"  URL:  {base + path}\n"
            f"  Body: {r.text[:800]}"
        )
    return _sap_response(r.json(), model=model)


def _reasoning_budget(level: str) -> int:
    return {"minimal": 512, "medium": 2048, "high": 8192}.get(level, 2048)


def _sap_response(payload: Dict[str, Any], *, model: str) -> Response:
    text = ""
    thinking = None
    tok_in = tok_out = tok_thinking = 0

    if "choices" in payload:                                # OpenAI shape
        msg = payload["choices"][0]["message"]
        text = msg.get("content") or ""
        thinking = msg.get("reasoning")
        usage = payload.get("usage") or {}
        tok_in = usage.get("prompt_tokens", 0)
        tok_out = usage.get("completion_tokens", 0)
        tok_thinking = usage.get("reasoning_tokens", 0)

    elif "content" in payload:                              # Anthropic shape
        parts: List[str] = []
        thought_parts: List[str] = []
        for b in payload["content"]:
            btype = b.get("type")
            if btype == "text":
                parts.append(b.get("text", ""))
            elif btype == "thinking":
                thought_parts.append(b.get("thinking", ""))
        text = "".join(parts)
        thinking = "\n".join(thought_parts) or None
        usage = payload.get("usage") or {}
        tok_in = usage.get("input_tokens", 0)
        tok_out = usage.get("output_tokens", 0)
        # Anthropic bundles thinking + answer tokens in output_tokens.
        # Estimate the thinking portion from character ratios.
        if thinking:
            th_chars = len(thinking)
            tx_chars = len(text)
            total    = th_chars + tx_chars
            if total > 0 and tok_out > 0:
                tok_thinking = round(tok_out * th_chars / total)

    elif "candidates" in payload:                           # Gemini shape (via Hub)
        try:
            text = "".join(p.get("text", "")
                           for p in payload["candidates"][0]["content"]["parts"])
        except Exception:
            text = ""
        usage = payload.get("usageMetadata") or {}
        tok_in = usage.get("promptTokenCount", 0)
        tok_out = usage.get("candidatesTokenCount", 0)

    return Response(text=text, thinking=thinking,
                    tokens_in=tok_in, tokens_out=tok_out,
                    tokens_thinking=tok_thinking,
                    raw=payload, backend="sap", model=model)


# ---------------------------------------------------------------------------
# Google Gemini fallback
# ---------------------------------------------------------------------------

_GEMINI_CLIENT = None


def _gemini_client():
    global _GEMINI_CLIENT
    if _GEMINI_CLIENT is not None:
        return _GEMINI_CLIENT
    key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError(
            "Set GOOGLE_API_KEY (or GEMINI_API_KEY) in .env "
            "to use LLM_BACKEND=gemini."
        )
    from google.genai import Client
    _GEMINI_CLIENT = Client(api_key=key)
    return _GEMINI_CLIENT


def _chat_gemini(system, user, *, reasoning, want_json,
                 model, temperature, max_tokens) -> Response:
    from google.genai.types import GenerateContentConfig
    model = model or os.getenv("GEMINI_MODEL", "models/gemini-flash-latest")

    cfg_kwargs: Dict[str, Any] = {
        "temperature": temperature,
        "max_output_tokens": max_tokens,
    }
    if want_json:
        cfg_kwargs["response_mime_type"] = "application/json"

    prompt = f"SYSTEM:\n{system}\n\nUSER:\n{user}"
    resp = _gemini_client().models.generate_content(
        model=model,
        contents=prompt,
        config=GenerateContentConfig(**cfg_kwargs),
    )

    text = resp.text or ""
    usage = getattr(resp, "usage_metadata", None)
    tok_in = getattr(usage, "prompt_token_count", 0) if usage else 0
    tok_out = getattr(usage, "candidates_token_count", 0) if usage else 0

    thinking = None
    try:
        for cand in getattr(resp, "candidates", []) or []:
            for part in cand.content.parts:
                if getattr(part, "thought", False):
                    thinking = (thinking or "") + (part.text or "")
    except Exception:
        pass

    return Response(text=text, thinking=thinking,
                    tokens_in=tok_in, tokens_out=tok_out,
                    raw={"gemini": True}, backend="gemini", model=model)


# ---------------------------------------------------------------------------
# Handy helper used across chapters
# ---------------------------------------------------------------------------

_JSON_FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)


def extract_json(text: str) -> Any:
    """Best-effort JSON extraction from a model's text output.

    Every chapter that parses tool calls goes through this helper.
    Kept small on purpose — Principle 3: the parser is your code.
    """
    if not text:
        raise ValueError("empty text")
    cleaned = _JSON_FENCE.sub("", text.strip()).strip()
    m = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not m:
        raise ValueError(f"no JSON object found in: {text[:200]}...")
    blob = m.group(0)
    opens, closes = blob.count("{"), blob.count("}")
    if opens > closes:
        blob += "}" * (opens - closes)
    return json.loads(blob)


if __name__ == "__main__":
    r = chat("Answer in one short sentence.",
             "Say hello and name yourself briefly.")
    print(f"[{r.backend} · {r.model}]  {r.text}")
    print(f"tokens: in={r.tokens_in} out={r.tokens_out}")
