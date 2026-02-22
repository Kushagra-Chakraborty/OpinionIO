from General.kafkaHelper import kafka_app
from Models.kafka_helper import consumers as _consumers  # noqa: F401
from Models.kafka_helper import tinybert_producer as _tinybert_producer  # noqa: F401
from Models.kafka_helper import xgboost_producer as _xgboost_producer  # noqa: F401

if __name__ == "__main__":
    kafka_app.run()