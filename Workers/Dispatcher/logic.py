from General.kafkaContracts import BulkTaskContract, InfluentialTaskContract, TaskDataContract, ToPredictTweet


INFLUENTIAL_FOLLOWERS_THRESHOLD = 1000


def split_tasks(task_data: TaskDataContract) -> tuple[InfluentialTaskContract, BulkTaskContract]:
    influential_X: list[ToPredictTweet] = []
    bulk_X: list[ToPredictTweet] = []

    for tweet in task_data.tweets:
        item = ToPredictTweet(tweet_id=tweet.tweet_id, text=tweet.text)
        is_influential = bool(tweet.metrics.user.verified) or (
            tweet.metrics.user.followers > INFLUENTIAL_FOLLOWERS_THRESHOLD
        )
        if is_influential:
            influential_X.append(item)
        else:
            bulk_X.append(item)

    return (
        InfluentialTaskContract(id=task_data.id, X=influential_X),
        BulkTaskContract(id=task_data.id, X=bulk_X),
    )
