#!/usr/bin/env python3
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
PRICING = ROOT / "data" / "pricing.json"
SOURCES = ROOT / "data" / "sources.json"


def fetch_json(url, timeout=15):
    request = Request(url, headers={"User-Agent": "Chinese-AI-Model-Pricing/1.0"})
    with urlopen(request, timeout=timeout) as response:
        if response.status != 200:
            raise RuntimeError(f"{url}: HTTP {response.status}")
        return json.loads(response.read().decode("utf-8"))


def check_url(url):
    request = Request(url, headers={"User-Agent": "Chinese-AI-Model-Pricing/1.0"})
    try:
        with urlopen(request, timeout=15) as response:
            return {"reachable": 200 <= response.status < 400, "http_status": response.status}
    except Exception as exc:
        return {"reachable": False, "error": str(exc)}


def validate(data):
    required = {"provider", "name", "model_id", "source_url"}
    ids = set()
    for model in data["models"]:
        missing = required - model.keys()
        if missing:
            raise ValueError(f"Model {model.get('name', '<unnamed>')} missing fields: {sorted(missing)}")
        if model["model_id"] in ids:
            raise ValueError(f"Duplicate model_id: {model['model_id']}")
        ids.add(model["model_id"])
        for field in ("input_cny_per_million", "output_cny_per_million", "cache_input_cny_per_million"):
            value = model.get(field)
            if value is not None and (not isinstance(value, (int, float)) or value < 0):
                raise ValueError(f"Invalid {field} for {model['model_id']}: {value}")


def update_openrouter(pricing):
    try:
        payload = fetch_json("https://openrouter.ai/api/v1/models")
    except Exception as exc:
        print(f"OpenRouter check skipped: {exc}")
        return

    chinese_terms = (
        "deepseek", "qwen", "glm", "ernie", "hunyuan", "doubao",
        "moonshot", "kimi", "minimax", "yi-", "yi/", "baichuan",
    )
    existing = {model["model_id"] for model in pricing["models"]}
    added = 0
    for item in payload.get("data", []):
        model_id = item.get("id", "")
        name = item.get("name", "")
        haystack = f"{model_id} {name}".lower()
        if not any(term in haystack for term in chinese_terms):
            continue
        if model_id in existing:
            continue
        pricing["models"].append({
            "provider": "openrouter",
            "name": name or model_id,
            "model_id": model_id,
            "context_window": item.get("context_length"),
            "input_cny_per_million": None,
            "output_cny_per_million": None,
            "verified_at": None,
            "source_url": "https://openrouter.ai/models",
        })
        added += 1
    if added:
        print(f"Added {added} unpriced Chinese-model entries from OpenRouter")


def main():
    pricing = json.loads(PRICING.read_text(encoding="utf-8"))
    sources = json.loads(SOURCES.read_text(encoding="utf-8"))
    now = datetime.now(timezone.utc)
    pricing["last_checked"] = now.date().isoformat()

    update_openrouter(pricing)
    validate(pricing)

    checked_at = now.isoformat(timespec="seconds").replace("+00:00", "Z")
    for source in sources["sources"]:
        result = check_url(source["check_url"])
        source["last_checked"] = checked_at
        source.update(result)

    PRICING.write_text(json.dumps(pricing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    SOURCES.write_text(json.dumps(sources, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Validated {len(pricing['models'])} model entries; checked {len(sources['sources'])} sources")


if __name__ == "__main__":
    main()
