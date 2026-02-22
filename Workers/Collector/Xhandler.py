import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


URL = "https://api.twitter.com/2/tweets/search/recent"
DEFAULT_MAX_RESULTS = 50


def _sample_payload() -> dict:
    return {
        "data": [
        {
            "id": "2026600000000000001",
            "author_id": "991000000000000001",
            "text": "India AI startup launches edge model for rural telemedicine pilots.",
            "lang": "en",
            "created_at": "2026-02-18T09:00:00.000Z",
            "public_metrics": {
                "retweet_count": 12,
                "reply_count": 3,
                "like_count": 55,
                "quote_count": 1,
            },
        },
        {
            "id": "2026600000000000002",
            "author_id": "991000000000000002",
            "text": "New open-source AI benchmark released for low-resource Indian languages.",
            "lang": "en",
            "created_at": "2026-02-18T09:02:00.000Z",
            "public_metrics": {
                "retweet_count": 4,
                "reply_count": 2,
                "like_count": 19,
                "quote_count": 0,
            },
        },
        {
            "id": "2026600000000000003",
            "author_id": "991000000000000003",
            "text": "AI policy roundtable in Bengaluru discusses safety evaluations and audits.",
            "lang": "en",
            "created_at": "2026-02-18T09:05:00.000Z",
            "public_metrics": {
                "retweet_count": 2,
                "reply_count": 0,
                "like_count": 8,
                "quote_count": 0,
            },
        },
        {
            "id": "2026600000000000004",
            "author_id": "991000000000000004",
            "text": "Prototype detects crop disease from smartphone images with 92 percent accuracy.",
            "lang": "en",
            "created_at": "2026-02-18T09:08:00.000Z",
            "public_metrics": {
                "retweet_count": 7,
                "reply_count": 1,
                "like_count": 33,
                "quote_count": 2,
            },
        },
        {
            "id": "2026600000000000005",
            "author_id": "991000000000000005",
            "text": "Hiring now for MLOps engineers to scale real-time fraud detection systems.",
            "lang": "en",
            "created_at": "2026-02-18T09:11:00.000Z",
            "public_metrics": {
                "retweet_count": 1,
                "reply_count": 0,
                "like_count": 5,
                "quote_count": 0,
            },
        },
        {
            "id": "2026600000000000006",
            "author_id": "991000000000000006",
            "text": "Today we tested multilingual speech models for call-center automation.",
            "lang": "en",
            "created_at": "2026-02-18T09:14:00.000Z",
            "public_metrics": {
                "retweet_count": 5,
                "reply_count": 1,
                "like_count": 14,
                "quote_count": 0,
            },
        },
        {
            "id": "2026600000000000007",
            "author_id": "991000000000000007",
            "text": "Open datasets and stronger labeling standards are overdue for healthcare AI.",
            "lang": "en",
            "created_at": "2026-02-18T09:17:00.000Z",
            "public_metrics": {
                "retweet_count": 3,
                "reply_count": 2,
                "like_count": 11,
                "quote_count": 1,
            },
        },
        {
            "id": "2026600000000000008",
            "author_id": "991000000000000008",
            "text": "Investor note: compute costs are falling but inference optimization still matters.",
            "lang": "en",
            "created_at": "2026-02-18T09:20:00.000Z",
            "public_metrics": {
                "retweet_count": 6,
                "reply_count": 1,
                "like_count": 21,
                "quote_count": 0,
            },
        },
    ],
    "includes": {
        "users": [
            {
                "id": "991000000000000001",
                "username": "AIHealthIndia",
                "name": "AI Health India",
                "verified": True,
                "public_metrics": {"followers_count": 15420},
            },
            {
                "id": "991000000000000002",
                "username": "IndicBench",
                "name": "Indic Benchmark Lab",
                "verified": False,
                "public_metrics": {"followers_count": 189},
            },
            {
                "id": "991000000000000003",
                "username": "PolicySignals",
                "name": "Policy Signals",
                "verified": False,
                "public_metrics": {"followers_count": 340},
            },
            {
                "id": "991000000000000004",
                "username": "AgriVisionAI",
                "name": "AgriVision AI",
                "verified": False,
                "public_metrics": {"followers_count": 98},
            },
            {
                "id": "991000000000000005",
                "username": "MLJobsNow",
                "name": "ML Jobs Now",
                "verified": False,
                "public_metrics": {"followers_count": 67},
            },
            {
                "id": "991000000000000006",
                "username": "VoiceOpsLab",
                "name": "VoiceOps Lab",
                "verified": "False",
                "public_metrics": {"followers_count": "215"},
            },
            {
                "id": "991000000000000007",
                "username": "OpenDataClinic",
                "name": "Open Data Clinic",
                "verified": "True",
                "public_metrics": {"followers_count": "4200"},
            },
            {
                "id": "991000000000000008",
                "username": "MacroAIToday",
                "name": "Macro AI Today",
                "verified": False,
                "public_metrics": {"followers_count": 512},
            },
        ]
    },
    "meta": {"result_count": "8"},
    }


def _get_bearer_token() -> str:
    token = os.getenv("TWITTER_BEARER_TOKEN") or os.getenv("bearertoken")
    return token.strip() if token else ""


def _build_query(topic: str, region: str) -> str:
    topic_part = topic.strip() if topic else "ai"
    region_part = f" ({region.strip()})" if region else ""
    return f"({topic_part}{region_part}) -is:retweet lang:en"


def fetch_recent_tweets(topic: str, region: str, max_results: int = DEFAULT_MAX_RESULTS) -> dict:
    token = _get_bearer_token()
    if not token:
        return _sample_payload()

    params = {
        "query": _build_query(topic=topic, region=region),
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
        return _sample_payload()
