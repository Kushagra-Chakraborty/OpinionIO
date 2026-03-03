import uuid
from pydantic import BaseModel, Field


class RequestContract(BaseModel):
    topic: str


class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    topic: str


class TaskContract(Task):
    ...


class BaseContract(BaseModel):
    id: str


class UserMetrics(BaseModel):
    user_id: int
    followers: int
    verified: int


class TweetMetrics(BaseModel):
    tweet_id: int
    retweet_count: int
    reply_count: int
    like_count: int
    quote_count: int


class Metrics(BaseModel):
    user: UserMetrics
    tweet: TweetMetrics


class Tweet(BaseModel):
    tweet_id: int
    text: str
    lang: str
    metrics: Metrics


class MetaDataContract(BaseContract):
    tweets: list[Tweet]


class TaskDataContract(MetaDataContract):
    ...


class ToPredictTweet(BaseModel):
    tweet_id: int
    text: str


class InfluentialTaskContract(BaseContract):
    X: list[ToPredictTweet]


class BulkTaskContract(InfluentialTaskContract):
    ...


class Results(BaseModel):
    tweet_id: int
    negative: float
    positive: float


class CompletedInfluentialTaskContract(InfluentialTaskContract):
    y: list[Results]


class CompletedBulkTaskContract(CompletedInfluentialTaskContract):
    ...


class Output(BaseContract):
    most_positive: float
    most_negative: float
    modal_sentiment: float


class ResearchMetrics(BaseContract):
    process: str
    start_time: int
    end_time: int
    total_time: int
