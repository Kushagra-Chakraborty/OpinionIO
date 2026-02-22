from __future__ import annotations

from pathlib import Path

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from General.kafkaContracts import (
    CompletedInfluentialTaskContract,
    InfluentialTaskContract,
    Results,
)


BASE_TOKENIZER_NAME = "huawei-noah/TinyBERT_General_4L_312D"
_BASE_DIR = Path(__file__).resolve().parent
_MODEL_DIR_CANDIDATES = (
    _BASE_DIR / "models",
    _BASE_DIR.parent / "models",
    _BASE_DIR.parent.parent / "models",
)


def _resolve_model_dir() -> Path:
    for model_dir in _MODEL_DIR_CANDIDATES:
        if (model_dir / "config.json").exists() and (model_dir / "model.safetensors").exists():
            return model_dir
    attempted = ", ".join(str(p) for p in _MODEL_DIR_CANDIDATES)
    raise FileNotFoundError(
        "Could not find TinyBERT artifacts. Expected 'config.json' and 'model.safetensors' in one of: "
        f"{attempted}"
    )


def _resolve_device() -> torch.device:
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


_MODEL_DIR = _resolve_model_dir()
_DEVICE = _resolve_device()

try:
    tokenizer = AutoTokenizer.from_pretrained(_MODEL_DIR)
except OSError:
    # Training used base tokenizer name. Fallback handles setups where tokenizer files were not exported.
    tokenizer = AutoTokenizer.from_pretrained(BASE_TOKENIZER_NAME)

model = AutoModelForSequenceClassification.from_pretrained(_MODEL_DIR)
model.to(_DEVICE)
model.eval()


def predict_influential_task(task: InfluentialTaskContract) -> CompletedInfluentialTaskContract:
    if not task.X:
        return CompletedInfluentialTaskContract(id=task.id, X=task.X, y=[])

    texts = [item.text for item in task.X]
    encoded = tokenizer(
        texts,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=512,
    )
    encoded = {name: value.to(_DEVICE) for name, value in encoded.items()}

    with torch.no_grad():
        logits = model(**encoded).logits
        probs = torch.softmax(logits, dim=-1).cpu()

    results: list[Results] = []
    for item, row in zip(task.X, probs):
        if row.numel() < 2:
            raise ValueError(
                "TinyBERT model output must have at least 2 classes for negative/positive mapping."
            )
        results.append(
            Results(
                tweet_id=item.tweet_id,
                negative=float(row[0]),
                positive=float(row[1]),
            )
        )

    return CompletedInfluentialTaskContract(id=task.id, X=task.X, y=results)
