from General.kafkaHelper import kafka_app
from Workers.Processor import consumer as _consumer  # noqa: F401
from Workers.Processor import producer as _producer  # noqa: F401


if __name__ == "__main__":
    kafka_app.run()
