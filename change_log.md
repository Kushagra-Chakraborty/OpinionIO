# Change Log

## 2026-02-21

- Refactored model Kafka producers to reduce coupling by splitting shared producer definitions into model-specific modules:
  - Added `Cloned/Models/kafka_helper/xgboost_producer.py` for `COMPLETED_BULK_TASK`.
  - Added `Cloned/Models/kafka_helper/tinybert_producer.py` for `COMPLETED_INFLUENTIAL_TASK`.
  - Updated `Cloned/Models/kafka_helper/consumers.py` to import `submit_result_xgboost` from `xgboost_producer`.
  - Updated `Cloned/Models/XGBoost/main.py` to import both producer modules for decorator registration.
  - Converted `Cloned/Models/kafka_helper/producers.py` to compatibility re-exports to avoid breaking existing imports.

## 2026-02-22

- Completed TinyBERT inference logic in `Cloned/Models/TinyBert/logic.py`:
  - Added model artifact discovery for `config.json` + `model.safetensors`.
  - Added tokenizer loading with fallback to `huawei-noah/TinyBERT_General_4L_312D`.
  - Added device-aware inference (CPU/CUDA), softmax scoring, and contract output mapping to `CompletedInfluentialTaskContract`.
- Noted Kafka orchestration wiring point for influential flow in `Cloned/Models/kafka_helper/consumers.py` (`consume_influential_task`).
