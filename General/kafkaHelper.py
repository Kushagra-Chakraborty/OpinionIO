from fastkafka import FastKafka
import socket
from General.config import settings  # <-- Import your central config

# Define your dynamic broker config
kafka_brokers = {
    settings.environment: {  # <-- Use environment name (e.g., 'development')
        "url": settings.kafka_broker_url,
        "description": f"{settings.environment} Kafka broker",
        "port": settings.kafka_broker_port,
    }, "localhost": {
        "url": "127.0.0.1",
        "port": 9092,
    }
}

# Initialize the FastKafka app
# We will tie this to the FastAPI lifespan later
kafka_app = FastKafka(
    kafka_brokers=kafka_brokers,
    client_id=socket.gethostname()
)
