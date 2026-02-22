import re

from General.kafkaContracts import Metrics, TaskDataContract, Tweet, TweetMetrics, UserMetrics


def _preprocess_text(text: str) -> str:
    cleaned = re.sub(r"[@#$%+_()^&*\-=.]", "", text)

    if cleaned.endswith(".tar.gz"):
        cleaned = cleaned[:-7]
    elif cleaned.endswith(".zip"):
        cleaned = cleaned[:-4]
    elif cleaned.endswith(".tar"):
        cleaned = cleaned[:-4]

    return cleaned.lower().strip()


def preprocess_task_data(meta_data) -> TaskDataContract:
    processed_tweets: list[Tweet] = []

    for tweet in meta_data.tweets:
        processed_tweets.append(
            Tweet(
                tweet_id=tweet.tweet_id,
                text=_preprocess_text(tweet.text),
                lang=tweet.lang,
                metrics=Metrics(
                    user=UserMetrics(
                        user_id=tweet.metrics.user.user_id,
                        followers=tweet.metrics.user.followers,
                        verified=tweet.metrics.user.verified,
                    ),
                    tweet=TweetMetrics(
                        tweet_id=tweet.metrics.tweet.tweet_id,
                        retweet_count=tweet.metrics.tweet.retweet_count,
                        reply_count=tweet.metrics.tweet.reply_count,
                        like_count=tweet.metrics.tweet.like_count,
                        quote_count=tweet.metrics.tweet.quote_count,
                    ),
                ),
            )
        )

    return TaskDataContract(id=meta_data.id, tweets=processed_tweets)
