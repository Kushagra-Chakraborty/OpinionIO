import json
from pathlib import Path

from General.kafkaContracts import TaskContract
from Models.XGBoost.logic import predict_bulk_task
from Workers.Collector.logic import collect_metadata
from Workers.Dispatcher.logic import split_tasks
from Workers.Processor.logic import preprocess_task_data


def run_smoke_test() -> None:
    task = TaskContract(id=1001, topic="ai", region="india")

    meta = collect_metadata(task)
    task_data = preprocess_task_data(meta)
    influential_task, bulk_task = split_tasks(task_data)
    completed_bulk = predict_bulk_task(bulk_task)

    if completed_bulk.id != task.id:
        raise AssertionError("Task id mismatch in completed bulk result")

    if len(completed_bulk.y) != len(bulk_task.X):
        raise AssertionError("Prediction count does not match bulk input size")

    for prediction in completed_bulk.y:
        if not (0.0 <= prediction.negative <= 1.0):
            raise AssertionError("Negative probability out of range")
        if not (0.0 <= prediction.positive <= 1.0):
            raise AssertionError("Positive probability out of range")
        if abs((prediction.negative + prediction.positive) - 1.0) > 1e-6:
            raise AssertionError("Probabilities must sum to 1")

    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "smoke_output.json"

    output_payload = {
        "summary": {
            "task_id": task.id,
            "meta_tweets": len(meta.tweets),
            "task_data_tweets": len(task_data.tweets),
            "influential_count": len(influential_task.X),
            "bulk_count": len(bulk_task.X),
            "bulk_predictions": len(completed_bulk.y),
        },
        "meta_data": meta.model_dump(),
        "task_data": task_data.model_dump(),
        "influential_task": influential_task.model_dump(),
        "bulk_task": bulk_task.model_dump(),
        "completed_bulk_task": completed_bulk.model_dump(),
    }
    output_path.write_text(json.dumps(output_payload, indent=2), encoding="utf-8")

    print("Smoke test passed.")
    print(output_payload["summary"])
    print(f"Wrote output: {output_path}")


if __name__ == "__main__":
    run_smoke_test()
