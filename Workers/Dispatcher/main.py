from General.kafkaHelper import kafka_app
from Workers.Dispatcher import consumer as _consumer  # noqa: F401
from Workers.Dispatcher import producer as _producer  # noqa: F401


if __name__ == "__main__":
    kafka_app.run()
