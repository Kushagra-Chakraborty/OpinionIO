# Real-Time Sentiment Analysis ML Deployment

## 🎯 Project Overview

A **production-ready ML deployment system** for real-time sentiment analysis of social media content (Twitter/X). The system deploys **two machine learning models** in a scalable, event-driven architecture:

- **XGBoost**: For bulk tweet sentiment analysis
- **TinyBERT**: For influential user tweet analysis (verified accounts, high followers)

### Key Features

✅ **Dual Model Deployment** - Smart routing based on user influence  
✅ **Event-Driven Architecture** - Apache Kafka for asynchronous processing  
✅ **Scalable Microservices** - Independent worker services  
✅ **Async Processing** - FastAPI + FastKafka for high throughput  
✅ **Statistical Analysis** - KDE-based modal sentiment calculation  
✅ **Training Data Collection** - Continuous improvement pipeline  

---

## 🏗️ Architecture

```
┌─────────────┐
│ External API│──┐
└─────────────┘  │
                 ▼
         ┌───────────────┐
         │  Kafka Broker │
         └───────────────┘
                 │
         ┌───────┴───────┬──────────┬──────────┐
         ▼               ▼          ▼          ▼
    ┌──────────┐  ┌───────────┐ ┌─────────┐ ┌─────────┐
    │Collector │→ │ Processor │→│Dispatch │→│ Models  │
    │  Worker  │  │  Worker   │ │  Worker │ │XGB/BERT │
    └──────────┘  └───────────┘ └─────────┘ └─────────┘
                                                   │
                                                   ▼
                                            ┌──────────┐
                                            │PostgreSQL│
                                            └──────────┘
```

### Pipeline Flow

1. **Task Submission** → External API receives task (topic + region)
2. **Data Collection** → Collector fetches recent tweets from Twitter API
3. **Preprocessing** → Processor cleans and normalizes text
4. **Smart Dispatch** → Splits tweets into influential/bulk categories
5. **Model Inference** → TinyBERT for influential, XGBoost for bulk
6. **Result Aggregation** → Statistical analysis (KDE for modal sentiment)
7. **Storage** → Results persisted to PostgreSQL

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Docker & Docker Compose
- PostgreSQL 15+
- 4GB+ RAM (for model loading)

### Installation

1. **Clone the repository**
```bash
git clone <your-repo>
cd MajorProjectSem6
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
.\venv\Scripts\activate   # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Create `.env` file**
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
# Environment
environment=development

# Database
database_url=postgresql+asyncpg://postgres:root@localhost:5433/major

# Kafka
kafka_broker_url=localhost
kafka_broker_port=9092
KAFKA_CONTAINER_NAME=kafka

# API Ports
external_api_port=8000
internal_api_port=8001

# Worker Ports
tinybert_worker_port=8002
xgboost_worker_port=8003

# API URLs
EXTERNAL_API_URL=http://localhost:8000
INTERNAL_API_URL=http://localhost:8001
```

5. **Start Kafka**
```bash
docker-compose up -d
```

6. **Initialize Database**
```bash
# Database will auto-initialize on first API startup
```

7. **Place Model Artifacts**

Ensure model files are in `Models/models/`:
- `models/macro_model.ubj` (XGBoost model)
- `models/vectorizer.pkl` (TF-IDF vectorizer)
- `models/config.json` (TinyBERT config)
- `models/model.safetensors` (TinyBERT weights)

---

## 🏃 Running the System

### Option 1: Using Procfile (Recommended)

```bash
# Start all services
./start.bat  # Windows
# OR
foreman start  # Linux/Mac (requires foreman gem)
```

### Option 2: Manual Service Startup

**Terminal 1 - External API:**
```bash
uvicorn Apis.external.main:external --port 8000 --reload
```

**Terminal 2 - Collector Worker:**
```bash
fastkafka run --num-workers 1 Workers.Collector.main:kafka_app
```

**Terminal 3 - Processor Worker:**
```bash
fastkafka run --num-workers 1 Workers.Processor.main:kafka_app
```

**Terminal 4 - Dispatcher Worker:**
```bash
fastkafka run --num-workers 1 Workers.Dispatcher.main:kafka_app
```

**Terminal 5 - XGBoost Model:**
```bash
fastkafka run --num-workers 1 Models.XGBoost.main:kafka_app
```

**Terminal 6 - TinyBERT Model:**
```bash
fastkafka run --num-workers 1 Models.TinyBert.main:kafka_app
```

**Terminal 7 - Internal API (optional):**
```bash
uvicorn Apis.internal.main:internal --port 8001 --reload
```

---

## 📡 API Usage

### Submit Analysis Task

```bash
POST http://localhost:8000/api/external/new
Content-Type: application/json

{
  "id": 12345,
  "topic": "artificial intelligence",
  "region": "India"
}
```

**Response:**
```json
{
  "status": "queued",
  "id": 12345
}
```

### Check Task Status

```bash
GET http://localhost:8001/api/internal/status/{task_id}
```

### Get Results

Results are automatically stored in PostgreSQL tables:
- `influential_results` - TinyBERT predictions
- `bulk_results` - XGBoost predictions

---

## 🔬 Model Details

### XGBoost Model
- **Purpose**: Bulk sentiment analysis
- **Input**: Preprocessed tweet text (TF-IDF vectorized)
- **Output**: Binary sentiment (positive/negative) with probabilities
- **Artifact**: `macro_model.ubj` + `vectorizer.pkl`

### TinyBERT Model
- **Purpose**: Influential user sentiment analysis
- **Base**: `huawei-noah/TinyBERT_General_4L_312D`
- **Input**: Raw text (auto-tokenized)
- **Output**: Binary sentiment with softmax probabilities
- **Artifact**: `config.json` + `model.safetensors`

### Influential Tweet Criteria
- Verified user account, **OR**
- Follower count > 1,000

---

## 📊 Database Schema

### tasks_status
```sql
id              INTEGER PRIMARY KEY
status          VARCHAR
influential_ready BOOLEAN
bulk_ready      BOOLEAN
created_at      TIMESTAMP
updated_at      TIMESTAMP
```

### influential_results / bulk_results
```sql
id              INTEGER PRIMARY KEY
location        VARCHAR
mode_sentiment  FLOAT
most_positive   FLOAT
most_negative   FLOAT
created_at      TIMESTAMP
updated_at      TIMESTAMP
```

### training_influential / training_Bulk
```sql
tweet_id        INTEGER PRIMARY KEY
tweet           VARCHAR
sentiment       INTEGER (0 or 1)
```

---

## 🧪 Testing

### Smoke Test
```bash
python smoke_test_pipeline.py
```

This submits 1000 test requests to stress-test the pipeline.

---

## 📈 Scalability

### Horizontal Scaling

Each worker can be scaled independently:

```bash
# Scale XGBoost workers
fastkafka run --num-workers 3 Models.XGBoost.main:kafka_app

# Scale Collector workers
fastkafka run --num-workers 2 Workers.Collector.main:kafka_app
```

### Kafka Partitioning

Current configuration: **3 partitions** per topic (see `docker-compose.yml`)

Increase partitions for higher throughput:
```bash
docker exec -it kafka kafka-topics.sh --alter \
  --topic BULK_TASK --partitions 6 \
  --bootstrap-server localhost:9092
```

---

## 🐛 Troubleshooting

### Model Loading Errors
- Ensure model files are in `Models/models/` directory
- Check file permissions
- Verify model format compatibility

### Kafka Connection Issues
```bash
# Check Kafka status
docker ps | grep kafka

# View Kafka logs
docker logs kafka

# Restart Kafka
docker-compose restart
```

### Database Connection Errors
- Verify PostgreSQL is running on port 5433
- Check `database_url` in `.env`
- Ensure database `major` exists

---

## 📦 Project Structure

```
MajorProjectSem6/
├── Apis/
│   ├── external/          # Public API for task submission
│   └── internal/          # Internal API for results/training
├── Workers/
│   ├── Collector/         # Tweet data collection
│   ├── Processor/         # Text preprocessing
│   └── Dispatcher/        # Task routing
├── Models/
│   ├── XGBoost/           # Bulk sentiment model
│   ├── TinyBert/          # Influential sentiment model
│   └── models/            # Model artifacts
├── General/
│   ├── config.py          # Environment configuration
│   ├── database.py        # SQLAlchemy models
│   ├── kafkaHelper.py     # Kafka setup
│   └── kafkaContracts.py  # Pydantic contracts
├── docker-compose.yml     # Kafka infrastructure
├── Procfile               # Service definitions
└── requirements.txt       # Python dependencies
```

---

## 🔧 Configuration

### Kafka Topics

- `TASK_NEW` - New task submissions
- `TASK_METADATA` - Collected tweet data
- `TASK_DATA` - Preprocessed tweets
- `INFLUENTIAL_TASK` - Influential user tweets
- `BULK_TASK` - Bulk tweets
- `COMPLETED_INFLUENTIAL_TASK` - TinyBERT results
- `COMPLETED_BULK_TASK` - XGBoost results

### Environment Variables

See `.env.example` for full configuration options.

---

## 📝 License

[Add your license here]

---

## 👥 Contributors

[Add contributors here]

---

## 🙏 Acknowledgments

- FastAPI framework
- FastKafka for Kafka integration
- Hugging Face Transformers
- XGBoost library

---

## 📞 Support

For issues or questions, please open a GitHub issue.

---

**Built with ❤️ for ML Deployment**
