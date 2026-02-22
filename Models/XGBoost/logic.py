from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any

import xgboost as xgb

from General.kafkaContracts import BulkTaskContract, CompletedBulkTaskContract, Results


_BASE_DIR = Path(__file__).resolve().parent
_MODEL_DIR_CANDIDATES = [
    _BASE_DIR / "models",
    _BASE_DIR.parent / "models",
    _BASE_DIR.parent.parent / "models",
]


def _load_pickle(filename: str) -> Any:
    for model_dir in _MODEL_DIR_CANDIDATES:
        file_path = model_dir / filename
        if file_path.exists():
            with file_path.open("rb") as fp:
                return pickle.load(fp)
    attempted = ", ".join(str(p / filename) for p in _MODEL_DIR_CANDIDATES)
    raise FileNotFoundError(f"Could not find pickle artifact '{filename}'. Tried: {attempted}")


def _candidate_paths(filenames: tuple[str, ...]) -> list[Path]:
    return [model_dir / name for model_dir in _MODEL_DIR_CANDIDATES for name in filenames]


def _load_xgb_model() -> Any:
    try:
        return _load_pickle("xgb_model.pkl")
    except FileNotFoundError:
        pass

    native_candidates = ("macro_model.ubj", "xgb_model.ubj", "xgb_model.json", "xgb_model.bin")
    for path in _candidate_paths(native_candidates):
        if path.exists():
            model = xgb.XGBClassifier()
            model.load_model(path)
            return model

    attempted = ", ".join(str(p) for p in _candidate_paths(("xgb_model.pkl",) + native_candidates))
    raise FileNotFoundError(f"Could not find XGBoost model artifact. Tried: {attempted}")


def _load_vectorizer() -> Any:
    return _load_pickle("vectorizer.pkl")


model = _load_xgb_model()
vectorizer = _load_vectorizer()


def predict_bulk_task(task: BulkTaskContract) -> CompletedBulkTaskContract:
    texts = [item.text for item in task.X]
    if not texts:
        return CompletedBulkTaskContract(id=task.id, X=task.X, y=[])

    transformed = vectorizer.transform(texts)
    probs = model.predict_proba(transformed)

    results: list[Results] = []
    for item, row in zip(task.X, probs):
        results.append(
            Results(
                tweet_id=item.tweet_id,
                negative=float(row[0]),
                positive=float(row[1]),
            )
        )

    return CompletedBulkTaskContract(id=task.id, X=task.X, y=results)
