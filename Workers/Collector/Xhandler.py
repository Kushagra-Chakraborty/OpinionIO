import json
import os
from copy import deepcopy
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


URL = "https://api.twitter.com/2/tweets/search/recent"
DEFAULT_MAX_RESULTS = 50
SAMPLE_PAYLOAD_PATH = Path(__file__).resolve().parent / "data" / "tweets_sample_500.json"
_SAMPLE_PAYLOAD_CACHE: dict | None = None


def _read_sample_payload() -> dict:
    global _SAMPLE_PAYLOAD_CACHE
    if _SAMPLE_PAYLOAD_CACHE is not None:
        return _SAMPLE_PAYLOAD_CACHE

    with SAMPLE_PAYLOAD_PATH.open("r", encoding="utf-8-sig") as f:
        _SAMPLE_PAYLOAD_CACHE = json.load(f)
    return _SAMPLE_PAYLOAD_CACHE


def _sample_payload(max_results: int = DEFAULT_MAX_RESULTS) -> dict:
    try:
        payload = deepcopy(_read_sample_payload())
    except (OSError, json.JSONDecodeError):
        return {"data": [], "includes": {"users": []}, "meta": {"result_count": "0"}}

    capped = max(10, min(max_results, 100))
    data = payload.get("data", [])
    users = payload.get("includes", {}).get("users", [])
    payload["data"] = data[:capped]
    payload["includes"] = {"users": users[:capped]}
    payload["meta"] = {"result_count": str(len(payload["data"]))}
    return payload


def _get_bearer_token() -> str:
    token = os.getenv("TWITTER_BEARER_TOKEN") or os.getenv("bearertoken")
    return token.strip() if token else ""


def _build_query(topic: str) -> str:
    topic_part = topic.strip() if topic else "ai"
    return f"({topic_part}) -is:retweet lang:en"


def fetch_recent_tweets(topic: str, max_results: int = DEFAULT_MAX_RESULTS) -> dict:
    token = _get_bearer_token()
    if not token:
        return _sample_payload(max_results=max_results)

    params = {
        "query": _build_query(topic=topic),
        "max_results": max(10, min(max_results, 100)),
        "tweet.fields": "created_at,author_id,public_metrics,lang",
        "expansions": "author_id",
        "user.fields": "id,name,username,verified,public_metrics",
    }
    query = urlencode(params)
    req = Request(
        f"{URL}?{query}",
        headers={"Authorization": f"Bearer {token}"},
        method="GET",
    )

    try:
        with urlopen(req, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return payload
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
        return _sample_payload(max_results=max_results)
