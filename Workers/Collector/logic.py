from General.kafkaContracts import (
    MetaDataContract,
    Metrics,
    TaskContract,
    Tweet,
    TweetMetrics,
    UserMetrics,
)

from .Xhandler import fetch_recent_tweets


def _safe_int(value, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _safe_bool_to_int(value) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, str):
        return int(value.strip().lower() in {"true", "1", "yes", "y"})
    return int(bool(value))


def _resolve_user(author_id: str, users: dict[str, dict]) -> dict:
    if not author_id:
        return {}

    if author_id in users:
        return users[author_id]

    for uid, candidate in users.items():
        if author_id.startswith(uid) or uid.startswith(author_id):
            return candidate
    return {}


def _to_tweet(raw_tweet: dict, users: dict[str, dict]) -> Tweet | None:
    tweet_id = _safe_int(raw_tweet.get("id"), default=-1)
    if tweet_id < 0:
        return None

    text = str(raw_tweet.get("text", "")).strip()
    if not text:
        return None

    author_id = str(raw_tweet.get("author_id", ""))
    user = _resolve_user(author_id, users)
    user_metrics = user.get("public_metrics", {})
    tweet_metrics = raw_tweet.get("public_metrics", {})

    return Tweet(
        tweet_id=tweet_id,
        text=text,
        lang=str(raw_tweet.get("lang", "und")),
        metrics=Metrics(
            user=UserMetrics(
                user_id=_safe_int(author_id),
                followers=_safe_int(user_metrics.get("followers_count")),
                verified=_safe_bool_to_int(user.get("verified", False)),
            ),
            tweet=TweetMetrics(
                tweet_id=tweet_id,
                retweet_count=_safe_int(tweet_metrics.get("retweet_count")),
                reply_count=_safe_int(tweet_metrics.get("reply_count")),
                like_count=_safe_int(tweet_metrics.get("like_count")),
                quote_count=_safe_int(tweet_metrics.get("quote_count")),
            ),
        ),
    )


def collect_metadata(task: TaskContract) -> MetaDataContract:
    payload = fetch_recent_tweets(topic=task.topic, region=task.region)
    users = {
        str(user.get("id")): user
        for user in payload.get("includes", {}).get("users", [])
        if user.get("id")
    }

    tweets: list[Tweet] = []
    for raw_tweet in payload.get("data", []):
        tweet = _to_tweet(raw_tweet, users)
        if tweet is not None:
            tweets.append(tweet)

    return MetaDataContract(id=task.id, tweets=tweets)
