# Real-Time Sentiment Analysis ML Deployment

## 🎯 Project Overview

A **production-ready ML deployment system** for real-time sentiment analysis of social media content (Twitter/X). The system deploys **two machine learning models** in a scalable, event-driven microservice architecture using **Docker Compose**.

- **XGBoost** — Bulk tweet sentiment analysis (TF-IDF + binary classifier)
- **TinyBERT** — Influential user tweet analysis (transformer-based, for verified / high-follower accounts)

### Key Features

✅ **Dual Model Deployment** — Smart routing based on user influence  
✅ **Event-Driven Architecture** — Apache Kafka (KRaft mode, no Zookeeper) for async processing  
✅ **Fully Dockerized** — Single `docker compose up` brings up all 10 services  
✅ **Health-Checked Dependencies** — Containers wait for Postgres & Kafka to be ready  
✅ **Async End-to-End** — FastAPI + FastKafka + asyncpg for high throughput  
✅ **Statistical Analysis** — KDE-based modal sentiment calculation  
✅ **Training Data Collection** — Continuous improvement pipeline  

---

## 🏗️ Architecture

```
                    ┌─────────────────┐
                    │   External API  │ :8000
                    └────────┬────────┘
                             │  POST /api/external/new
                             ▼
                    ┌─────────────────┐
                    │  Apache Kafka   │ :9092  (KRaft, 3 partitions)
                    └────────┬────────┘
           ┌─────────────────┼─────────────────┐
           ▼                 ▼                  ▼
    ┌─────────────┐   ┌────────────┐   ┌──────────────┐
    │  Collector  │──▶│ Processor  │──▶│  Dispatcher   │
    │   Worker    │   │   Worker   │   │    Worker     │
    └─────────────┘   └────────────┘   └──────┬───────┘
                                        ┌─────┴──────┐
                                        ▼            ▼
                                  ┌──────────┐ ┌──────────┐
                                  │ TinyBERT │ │ XGBoost  │
                                  │  Model   │ │  Model   │
                                  └─────┬────┘ └─────┬────┘
                                        ▼            ▼
                                  ┌──────────────────────┐
                                  │    Results Worker     │
                                  └──────────┬───────────┘
                                             ▼
                            ┌─────────────────────────────┐
                            │   Internal API  :8001       │
                            │  (status, results, training)│
                            └──────────────┬──────────────┘
                                           ▼
                                  ┌─────────────────┐
                                  │   PostgreSQL     │ :5432
                                  └─────────────────┘
```

### Pipeline Flow

| Step | Service | Kafka Topic | Description |
|------|---------|-------------|-------------|
| 1 | **External API** | `NEW_TASK` | Receives task (topic + region), creates DB record, publishes to Kafka |
| 2 | **Collector Worker** | `NEW_TASK` → `META_DATA` | Fetches recent tweets from Twitter/X API |
| 3 | **Processor Worker** | `META_DATA` → `TASK_DATA` | Cleans and normalizes tweet text |
| 4 | **Dispatcher Worker** | `TASK_DATA` → `INFLUENTIAL_TASK` / `BULK_TASK` | Splits tweets by user influence (verified OR >1k followers) |
| 5a | **TinyBERT Model** | `INFLUENTIAL_TASK` → `COMPLETED_INFLUENTIAL_TASK` | Transformer inference on influential tweets |
| 5b | **XGBoost Model** | `BULK_TASK` → `COMPLETED_BULK_TASK` | TF-IDF + XGBoost inference on bulk tweets |
| 6 | **Results Worker** | `COMPLETED_*` → Internal API | Aggregates results (KDE modal sentiment) and persists to DB |

---

## 📦 Project Structure

```
MajorProjectSem6/
├── docker-compose.yml          # Full stack: Postgres + Kafka + all services
├── requirements.txt            # Global Python dependencies (for local dev)
├── Procfile                    # Local dev process definitions
│
├── Apis/
│   ├── external/               # Public-facing API  (:8000)
│   │   ├── dockerfile
│   │   ├── main.py             # FastAPI app entry
│   │   ├── routes/
│   │   │   ├── new.py          # POST /api/external/new/
│   │   │   └── status.py       # GET  /api/external/status/{task_id}
│   │   └── kafka_helper/       # Kafka producer for NEW_TASK
│   │
│   └── internal/               # Internal API (:8001)
│       ├── dockerfile
│       ├── main.py
│       ├── routes/
│       │   ├── status.py       # POST /api/internal/status/{task_id}
│       │   ├── results.py      # POST /api/internal/results/influential|bulk
│       │   └── training.py     # POST /api/internal/save/influential
│       ├── Result_handler/     # KDE statistical filtering
│       └── kafka_helper/
│
├── Workers/
│   ├── send_status.py          # Shared HTTP helper for status updates
│   ├── Collector/              # Tweet data collection worker
│   │   ├── dockerfile
│   │   ├── main.py, consumer.py, producer.py, logic.py
│   │   └── Xhandler.py        # Twitter/X API handler
│   ├── Processor/              # Text preprocessing worker
│   ├── Dispatcher/             # Influential/bulk routing worker
│   └── Results/                # Result aggregation worker
│
├── Models/
│   ├── models/                 # Model artifacts (mounted as volume)
│   │   ├── macro_model.ubj     # XGBoost binary model
│   │   ├── vectorizer.pkl      # TF-IDF vectorizer
│   │   ├── config.json         # TinyBERT config
│   │   └── model.safetensors   # TinyBERT weights
│   ├── kafka_helper/           # Shared Kafka contracts for models
│   ├── XGBoost/                # XGBoost inference worker
│   │   ├── dockerfile
│   │   ├── main.py, consumer.py, producer.py, logic.py
│   └── TinyBert/               # TinyBERT inference worker
│       ├── dockerfile
│       ├── main.py, consumers.py, producer.py, logic.py
│
└── General/                    # Shared library (copied into every container)
    ├── config.py               # Pydantic Settings (reads env vars)
    ├── database.py             # SQLAlchemy async engine + ORM models
    ├── kafkaHelper.py          # FastKafka app factory
    ├── kafkaContracts.py       # Pydantic data contracts
    └── logger.py               # Custom logger
```

---

## 🚀 Quick Start (Docker — Recommended)

### Prerequisites

| Requirement | Minimum |
|---|---|
| **Docker** | 20.10+ |
| **Docker Compose** | v2.0+ (or `docker compose` plugin) |
| **RAM** | 4 GB+ (TinyBERT + XGBoost load into memory) |
| **Disk** | ~3 GB (Docker images + model artifacts) |

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd MajorProjectSem6
```

### 2. Place Model Artifacts

Ensure these files exist in `Models/models/`:

```
Models/models/
├── macro_model.ubj       # XGBoost model
├── vectorizer.pkl        # TF-IDF vectorizer
├── config.json           # TinyBERT config
└── model.safetensors     # TinyBERT weights
```

> ⚠️ Without these files the `xgboost` and `tinybert` containers will crash on startup.

### 3. Start the entire stack

```bash
docker compose up --build
```

This single command will:

1. **Pull** `postgres:15-alpine` and `apache/kafka:latest`
2. **Build** 8 service images (2 APIs + 4 workers + 2 models)
3. **Start** everything in dependency order:
   - PostgreSQL starts first (with health check)
   - Kafka starts next (with health check — waits up to 40s for broker readiness)
   - APIs start after both are healthy
   - Workers & models start after APIs are available
4. **Auto-create** database tables on first API startup

> 💡 Add `-d` to run in detached mode: `docker compose up --build -d`

### 4. Verify all services are running

```bash
docker compose ps
```

You should see **10 containers** all in `Up` / `Up (healthy)` state:

| Container | Service | Port |
|---|---|---|
| `postgres_db` | PostgreSQL | `5432` |
| `kafka` | Apache Kafka (KRaft) | `9092` |
| `external_api` | External API | `8000` |
| `internal_api` | Internal API | `8001` |
| `collector_worker` | Collector Worker | — |
| `processor_worker` | Processor Worker | — |
| `dispatcher_worker` | Dispatcher Worker | — |
| `xgboost-model` | XGBoost Model | — |
| `tinybert-model` | TinyBERT Model | — |
| `results_worker` | Results Worker | — |

### 5. Submit a test task

```bash
curl -X POST http://localhost:8000/api/external/new/ \
  -H "Content-Type: application/json" \
  -d '{"id": 1001, "topic": "artificial intelligence", "region": "India"}'
```

**Response:**
```json
{
  "status": "queued",
  "id": 1001
}
```

### 6. Check results

```bash
curl http://localhost:8000/api/external/status/1001
```

**Response (when complete):**
```json
{
  "status": "Completed",
  "influential": {
    "mode": 0.72,
    "positive": 0.95,
    "negative": 0.12
  },
  "bulk": {
    "mode": 0.61,
    "positive": 0.89,
    "negative": 0.08
  }
}
```

### 7. Stop everything

```bash
docker compose down
```

To also **wipe the database** (fresh start):

```bash
docker compose down -v
```

---

## 📡 API Reference

### External API (`:8000`)

#### `POST /api/external/new/` — Submit Analysis Task

```json
// Request
{
  "id": 12345,
  "topic": "artificial intelligence",
  "region": "India"
}

// Response
{ "status": "queued", "id": 12345 }
```

#### `GET /api/external/status/{task_id}` — Get Task Status & Results

```json
// Response (processing)
{ "query": "success", "status": "processing" }

// Response (completed)
{
  "status": "Completed",
  "influential": { "mode": 0.72, "positive": 0.95, "negative": 0.12 },
  "bulk":        { "mode": 0.61, "positive": 0.89, "negative": 0.08 }
}
```

### Internal API (`:8001`) — Used internally by workers

| Endpoint | Method | Description |
|---|---|---|
| `/api/internal/status/{task_id}?status=...` | POST | Update task status |
| `/api/internal/status/flag/bulk/{task_id}/{flag}` | POST | Set bulk-ready flag |
| `/api/internal/status/flag/influential/{task_id}/{flag}` | POST | Set influential-ready flag |
| `/api/internal/results/influential` | POST | Submit influential results (from Results Worker) |
| `/api/internal/results/bulk` | POST | Submit bulk results (from Results Worker) |
| `/api/internal/save/influential` | POST | Save training data for model retraining |

---

## 🔬 Model Details

### XGBoost Model
| | |
|---|---|
| **Purpose** | Bulk sentiment analysis |
| **Input** | Preprocessed tweet text → TF-IDF vectorized |
| **Output** | Binary sentiment (positive/negative) with probabilities |
| **Artifacts** | `macro_model.ubj` + `vectorizer.pkl` |

### TinyBERT Model
| | |
|---|---|
| **Purpose** | Influential user sentiment analysis |
| **Base Model** | `huawei-noah/TinyBERT_General_4L_312D` |
| **Input** | Raw text (auto-tokenized) |
| **Output** | Binary sentiment with softmax probabilities |
| **Artifacts** | `config.json` + `model.safetensors` |

### Influential Tweet Criteria
A tweet is classified as "influential" if:
- User is **verified**, **OR**
- User has **>1,000 followers**

All other tweets go to the **bulk** (XGBoost) pipeline.

---

## 📊 Database Schema

### `tasks_status`
| Column | Type | Description |
|---|---|---|
| `id` | INTEGER (PK) | Task ID |
| `status` | VARCHAR | `queued` → `processing` → `completed` |
| `influential_ready` | BOOLEAN | True when TinyBERT results are in |
| `bulk_ready` | BOOLEAN | True when XGBoost results are in |
| `created_at` | TIMESTAMP | Auto-set on creation |
| `updated_at` | TIMESTAMP | Auto-set on update |

### `influential_results` / `bulk_results`
| Column | Type | Description |
|---|---|---|
| `id` | INTEGER (PK) | Task ID (FK to tasks_status) |
| `location` | VARCHAR | Region/location |
| `mode_sentiment` | FLOAT | KDE modal sentiment score |
| `most_positive` | FLOAT | Highest positive probability |
| `most_negative` | FLOAT | Highest negative probability |
| `created_at` | TIMESTAMP | Auto-set |
| `updated_at` | TIMESTAMP | Auto-set |

### `training_influential` / `training_Bulk`
| Column | Type | Description |
|---|---|---|
| `tweet_id` | INTEGER (PK) | Unique tweet ID |
| `tweet` | VARCHAR | Raw tweet text |
| `sentiment` | INTEGER | `0` (negative) or `1` (positive) |

---

## 🔧 Configuration

### Environment Variables

All application containers share the same environment variables via the `x-common-env` YAML anchor in `docker-compose.yml`:

| Variable | Docker Value | Description |
|---|---|---|
| `ENVIRONMENT` | `docker` | Used as Kafka broker name in FastKafka |
| `DATABASE_URL` | `postgresql+asyncpg://postgres:root@postgres:5432/major` | Async SQLAlchemy connection string |
| `KAFKA_BROKER_URL` | `kafka` | Kafka hostname (Docker DNS) |
| `KAFKA_BROKER_PORT` | `9092` | Kafka broker port |
| `INTERNAL_API_URL` | `http://internal-api:8001` | Internal API base URL (Docker DNS) |
| `EXTERNAL_API_URL` | `http://external-api:8000` | External API base URL (Docker DNS) |
| `KAFKA_CONTAINER_NAME` | `kafka` | Kafka container name |
| `EXTERNAL_API_PORT` | `8000` | External API port |
| `INTERNAL_API_PORT` | `8001` | Internal API port |
| `TINYBERT_WORKER_PORT` | `8002` | TinyBERT worker port |
| `XGBOOST_WORKER_PORT` | `8003` | XGBoost worker port |

> These are configured via `pydantic-settings` in `General/config.py` which reads from environment variables (in Docker) or a `.env` file (for local dev).

### Kafka Topics

| Topic | Producer | Consumer | Payload |
|---|---|---|---|
| `NEW_TASK` | External API | Collector | `TaskContract` (id, topic, region) |
| `META_DATA` | Collector | Processor | `MetaDataContract` (tweets with metrics) |
| `TASK_DATA` | Processor | Dispatcher | `TaskDataContract` (cleaned tweets) |
| `INFLUENTIAL_TASK` | Dispatcher | TinyBERT | `InfluentialTaskContract` (influential tweets) |
| `BULK_TASK` | Dispatcher | XGBoost | `BulkTaskContract` (bulk tweets) |
| `COMPLETED_INFLUENTIAL_TASK` | TinyBERT | Results Worker | `CompletedInfluentialTaskContract` (predictions) |
| `COMPLETED_BULK_TASK` | XGBoost | Results Worker | `CompletedBulkTaskContract` (predictions) |

Kafka is configured with **3 partitions** per topic for parallel consumption.

---

## 📈 Scalability

### Scaling Workers with Docker Compose

```bash
# Scale XGBoost to 3 replicas
docker compose up --scale xgboost=3 -d

# Scale Collector to 2 replicas
docker compose up --scale collector=2 -d
```

### Increase Kafka Partitions

```bash
docker exec -it kafka /opt/kafka/bin/kafka-topics.sh --alter \
  --topic BULK_TASK --partitions 6 \
  --bootstrap-server localhost:9092
```

> Match the number of partitions to the number of consumer replicas for optimal throughput.

---

## 🐳 Docker Commands Cheat Sheet

| Command | Description |
|---|---|
| `docker compose up --build` | Build & start all services (foreground) |
| `docker compose up --build -d` | Build & start all services (background) |
| `docker compose ps` | Check service status |
| `docker compose logs -f collector` | Tail logs for a specific service |
| `docker compose logs -f` | Tail logs for all services |
| `docker compose restart tinybert` | Restart a single service |
| `docker compose down` | Stop & remove all containers |
| `docker compose down -v` | Stop, remove containers, **and delete volumes** (DB data) |
| `docker compose build --no-cache` | Force full rebuild (no layer cache) |

---

## 🐛 Troubleshooting

### Containers exiting immediately
```bash
# Check logs for the failing container
docker compose logs xgboost-model
docker compose logs tinybert-model
```
Common causes:
- Missing model artifacts in `Models/models/`
- Missing environment variables (check `docker compose config` to verify)

### Kafka connection refused
```bash
# Verify Kafka is healthy
docker compose ps kafka

# Check Kafka logs
docker compose logs kafka

# Manually list topics to confirm broker is up
docker exec kafka /opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092
```
Kafka takes ~30–40s to fully start in KRaft mode. The health check handles this automatically.

### Database connection errors
```bash
# Verify Postgres is healthy
docker compose ps postgres

# Connect manually
docker exec -it postgres_db psql -U postgres -d major

# Check if tables exist
\dt
```

### Rebuilding from scratch
```bash
docker compose down -v          # Wipe everything
docker compose up --build       # Fresh start
```

---

## 🧪 Testing

### Quick test with `curl`

```bash
# Submit a task
curl -X POST http://localhost:8000/api/external/new/ \
  -H "Content-Type: application/json" \
  -d '{"id": 9999, "topic": "climate change", "region": "USA"}'

# Check status (wait 10-30s for pipeline to complete)
curl http://localhost:8000/api/external/status/9999
```

### Using `test.http` (VS Code REST Client)

Open `test.http` in VS Code with the [REST Client extension](https://marketplace.visualstudio.com/items?itemName=humao.rest-client) and click "Send Request" on any block.

### Smoke Test (load test)

```bash
python smoke_test_pipeline.py
```

Submits 1000 concurrent requests to stress-test the pipeline.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **API Framework** | FastAPI |
| **Kafka Client** | FastKafka |
| **Database** | PostgreSQL 15 + SQLAlchemy (async) |
| **ML Models** | XGBoost, HuggingFace Transformers (TinyBERT) |
| **Containerization** | Docker + Docker Compose |
| **Message Broker** | Apache Kafka (KRaft mode) |
| **Python** | 3.12 |
| **Config Management** | pydantic-settings |

---

## 🏃 How to Run — Summary

```bash
# 1. Clone
git clone <your-repo-url>
cd MajorProjectSem6

# 2. Ensure model files exist in Models/models/
#    (macro_model.ubj, vectorizer.pkl, config.json, model.safetensors)

# 3. Build & start everything
docker compose up --build

# 4. Wait for all 10 containers to be healthy (~60s first time)

# 5. Test it
curl -X POST http://localhost:8000/api/external/new/ \
  -H "Content-Type: application/json" \
  -d '{"id": 1, "topic": "elections", "region": "USA"}'

# 6. Check results
curl http://localhost:8000/api/external/status/1

# 7. Stop when done
docker compose down
```

---

## 📝 License

[Add your license here]

---

## 👥 Contributors
Divyansh
Kushagra 
Muskan
---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) — High-performance async API framework
- [FastKafka](https://github.com/airtai/fastkafka) — Kafka integration for Python
- [HuggingFace Transformers](https://huggingface.co/docs/transformers) — TinyBERT model serving
- [XGBoost](https://xgboost.readthedocs.io/) — Gradient boosting classifier
- [Apache Kafka](https://kafka.apache.org/) — Distributed event streaming
- [PostgreSQL](https://www.postgresql.org/) — Relational database

---

**Built with ❤️ for ML Deployment**
