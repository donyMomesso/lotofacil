from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from statistics import mean
from typing import Iterable, Sequence

TOTAL_NUMBERS = 25
DRAW_SIZE = 15
BASE_RATE = DRAW_SIZE / TOTAL_NUMBERS
BASELINE_BRIER = BASE_RATE * (1 - BASE_RATE)
BASELINE_LOG_LOSS = -(BASE_RATE * math.log(BASE_RATE) + (1 - BASE_RATE) * math.log(1 - BASE_RATE))
THEORETICAL_TOP21 = 21 * BASE_RATE
CHECKPOINT_SIZE = 5
MIN_TRAINING = 30
BRAIN_VERSION = "python-historical-brain-v1.0.0"

MODEL_WEIGHTS = {
    "stable": {"freq10": 0.32, "freq30": 0.24, "trend": 0.14, "repeat": 0.14, "delay": 0.10, "cycle": 0.06},
    "adaptive": {"freq10": 0.42, "freq30": 0.16, "trend": 0.20, "repeat": 0.10, "delay": 0.08, "cycle": 0.04},
    "python_v4": {"freq10": 0.19, "freq30": 0.12, "trend": 0.14, "repeat": 0.15, "delay": 0.12, "cycle": 0.12, "neighbor": 0.08, "structure": 0.08},
}

FORBIDDEN_PUBLIC_KEYS = {
    "ranking", "rankings", "numbers", "dezenas", "base", "bases", "games", "jogos",
    "prediction", "predictions", "previsao", "previsoes", "next_contest", "proximo_concurso",
}


@dataclass(frozen=True)
class Draw:
    contest: int
    numbers: tuple[int, ...]
    date: str = ""

    @classmethod
    def from_value(cls, value: object) -> "Draw":
        if not isinstance(value, dict):
            raise ValueError("Cada concurso deve ser um objeto.")
        raw_numbers = value.get("dezenas", value.get("numbers", []))
        numbers = tuple(sorted({int(number) for number in raw_numbers}))
        contest = int(value.get("concurso", value.get("contest", 0)))
        if contest <= 0:
            raise ValueError("Número do concurso inválido.")
        if len(numbers) != DRAW_SIZE or any(number < 1 or number > TOTAL_NUMBERS for number in numbers):
            raise ValueError(f"Concurso {contest} deve conter 15 dezenas únicas entre 1 e 25.")
        return cls(contest=contest, numbers=numbers, date=str(value.get("data", value.get("date", "")) or ""))


def normalize_draws(values: Iterable[object]) -> list[Draw]:
    seen: set[int] = set()
    draws: list[Draw] = []
    for value in values:
        draw = Draw.from_value(value)
        if draw.contest in seen:
            raise ValueError(f"Concurso duplicado: {draw.contest}.")
        seen.add(draw.contest)
        draws.append(draw)
    draws.sort(key=lambda item: item.contest)
    return draws


def _frequency(history: Sequence[Draw], number: int, size: int) -> float:
    sample = history[-size:]
    if not sample:
        return BASE_RATE
    return sum(number in draw.numbers for draw in sample) / len(sample)


def _delay(history: Sequence[Draw], number: int) -> int:
    for distance, draw in enumerate(reversed(history)):
        if number in draw.numbers:
            return distance
    return len(history)


def _cycle_pending(history: Sequence[Draw]) -> set[int]:
    seen: set[int] = set()
    for draw in reversed(history):
        seen.update(draw.numbers)
        if len(seen) == TOTAL_NUMBERS:
            break
    return set(range(1, TOTAL_NUMBERS + 1)) - seen


def _feature_rows(history: Sequence[Draw]) -> dict[int, dict[str, float]]:
    last = set(history[-1].numbers) if history else set()
    pending = _cycle_pending(history)
    delays = {number: _delay(history, number) for number in range(1, TOTAL_NUMBERS + 1)}
    max_delay = max(delays.values(), default=1)
    rows: dict[int, dict[str, float]] = {}
    for number in range(1, TOTAL_NUMBERS + 1):
        freq10 = _frequency(history, number, 10)
        freq30 = _frequency(history, number, 30)
        neighbors = sum(candidate in last for candidate in (number - 1, number + 1))
        row = (number - 1) // 5
        column = (number - 1) % 5
        row_occupancy = sum((candidate - 1) // 5 == row for candidate in last) / 5 if last else BASE_RATE
        column_occupancy = sum((candidate - 1) % 5 == column for candidate in last) / 5 if last else BASE_RATE
        rows[number] = {
            "freq10": freq10 - BASE_RATE,
            "freq30": freq30 - BASE_RATE,
            "trend": freq10 - freq30,
            "repeat": (1.0 if number in last else 0.0) - BASE_RATE,
            "delay": (delays[number] / max_delay) - 0.45 if max_delay else 0.0,
            "cycle": (1.0 if number in pending else 0.55) - BASE_RATE,
            "neighbor": (0.35 + 0.325 * neighbors) - BASE_RATE,
            "structure": (1 - abs(((row_occupancy + column_occupancy) / 2) - BASE_RATE)) - BASE_RATE,
        }
    return rows


def _sigmoid(value: float) -> float:
    if value >= 0:
        z = math.exp(-value)
        return 1 / (1 + z)
    z = math.exp(value)
    return z / (1 + z)


def _calibrate(logits: Sequence[float]) -> list[float]:
    low, high = -12.0, 12.0
    for _ in range(100):
        middle = (low + high) / 2
        probabilities = [min(0.92, max(0.18, _sigmoid(logit + middle))) for logit in logits]
        if sum(probabilities) > DRAW_SIZE:
            high = middle
        else:
            low = middle
    shift = (low + high) / 2
    return [min(0.92, max(0.18, _sigmoid(logit + shift))) for logit in logits]


def score_history(history: Sequence[Draw], model: str) -> list[tuple[int, float]]:
    if len(history) < 8:
        raise ValueError("Histórico insuficiente.")
    weights = MODEL_WEIGHTS.get(model)
    if weights is None:
        raise ValueError(f"Modelo desconhecido: {model}.")
    features = _feature_rows(history)
    base_logit = math.log(BASE_RATE / (1 - BASE_RATE))
    numbers = list(range(1, TOTAL_NUMBERS + 1))
    logits = [base_logit + sum(features[number].get(key, 0.0) * weight for key, weight in weights.items()) for number in numbers]
    probabilities = _calibrate(logits)
    return list(zip(numbers, probabilities, strict=True))


def evaluate(history: Sequence[Draw], target: Draw, model: str) -> dict[str, float | int]:
    training_through = history[-1].contest
    if training_through >= target.contest:
        raise ValueError(f"Vazamento temporal no concurso {target.contest}.")
    probabilities = score_history(history, model)
    actual = set(target.numbers)
    brier = mean((probability - (1 if number in actual else 0)) ** 2 for number, probability in probabilities)
    log_loss = mean(-math.log(max(1e-12, probability if number in actual else 1 - probability)) for number, probability in probabilities)
    ordered = sorted(probabilities, key=lambda item: (-item[1], item[0]))
    top21 = sum(number in actual for number, _ in ordered[:21])
    return {
        "contest": target.contest,
        "training_through": training_through,
        "training_count": len(history),
        "brier": round(brier, 8),
        "log_loss": round(log_loss, 8),
        "top21": int(top21),
    }


def walk_forward(values: Iterable[object], min_training: int = MIN_TRAINING) -> list[dict[str, object]]:
    draws = normalize_draws(values)
    if len(draws) <= min_training:
        return []
    rows: list[dict[str, object]] = []
    for target_index in range(max(8, min_training), len(draws)):
        history = draws[:target_index]
        target = draws[target_index]
        for model in MODEL_WEIGHTS:
            rows.append({"model": model, **evaluate(history, target, model)})
    return rows


def _model_summary(rows: Sequence[dict[str, object]]) -> dict[str, object]:
    return {
        "samples": len(rows),
        "brier": round(mean(float(row["brier"]) for row in rows), 8),
        "log_loss": round(mean(float(row["log_loss"]) for row in rows), 8),
        "avg_top21": round(mean(float(row["top21"]) for row in rows), 4),
    }


def _drift(rows: Sequence[dict[str, object]]) -> dict[str, object]:
    if len(rows) < 10:
        return {"level": "insufficient", "brier_delta": 0.0, "top21_delta": 0.0}
    recent = rows[-5:]
    previous = rows[-10:-5]
    brier_delta = mean(float(row["brier"]) for row in recent) - mean(float(row["brier"]) for row in previous)
    top21_delta = mean(float(row["top21"]) for row in recent) - mean(float(row["top21"]) for row in previous)
    level = "none"
    if brier_delta > 0.02 or top21_delta < -0.8:
        level = "high"
    elif brier_delta > 0.01 or top21_delta < -0.4:
        level = "moderate"
    return {"level": level, "brier_delta": round(brier_delta, 8), "top21_delta": round(top21_delta, 4)}


def _report_hash(payload: object) -> str:
    serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def build_report(values: Iterable[object], min_training: int = MIN_TRAINING) -> dict[str, object]:
    draws = normalize_draws(values)
    serialized_draws = [{"concurso": draw.contest, "data": draw.date, "dezenas": list(draw.numbers)} for draw in draws]
    rows = walk_forward(serialized_draws, min_training)
    evaluated_contests = sorted({int(row["contest"]) for row in rows})
    completed = (len(evaluated_contests) // CHECKPOINT_SIZE) * CHECKPOINT_SIZE
    completed_contests = set(evaluated_contests[:completed])
    completed_rows = [row for row in rows if int(row["contest"]) in completed_contests]
    checkpoints: list[dict[str, object]] = []
    for end in range(CHECKPOINT_SIZE, completed + 1, CHECKPOINT_SIZE):
        contests = evaluated_contests[:end]
        contest_set = set(contests)
        model_summaries: dict[str, object] = {}
        for model in MODEL_WEIGHTS:
            model_rows = [row for row in rows if row["model"] == model and int(row["contest"]) in contest_set]
            recent_rows = model_rows[-CHECKPOINT_SIZE:]
            model_summaries[model] = {
                "cumulative": _model_summary(model_rows),
                "recent_5": _model_summary(recent_rows),
                "drift": _drift(model_rows),
            }
        champion = min(model_summaries, key=lambda key: float(model_summaries[key]["cumulative"]["brier"]))
        checkpoint = {
            "index": end // CHECKPOINT_SIZE,
            "first_contest": contests[0],
            "last_contest": contests[-1],
            "evaluated_contests": end,
            "historical_champion": champion if end >= 30 else None,
            "status": "comparable" if end >= 30 else "collecting_evidence",
            "models": model_summaries,
        }
        checkpoint["hash"] = _report_hash(checkpoint)
        checkpoints.append(checkpoint)
    integrity = {
        "temporal_violations": sum(int(row["training_through"]) >= int(row["contest"]) for row in completed_rows),
        "duplicate_contests": 0,
        "checkpoint_size": CHECKPOINT_SIZE,
        "ok": True,
    }
    integrity["ok"] = integrity["temporal_violations"] == 0
    report = {
        "ok": True,
        "purpose": "historical_education_only",
        "brain_version": BRAIN_VERSION,
        "source_of_truth": "python",
        "baselines": {"brier": BASELINE_BRIER, "log_loss": BASELINE_LOG_LOSS, "top21": THEORETICAL_TOP21},
        "total_draws_received": len(draws),
        "evaluated_contests": len(evaluated_contests),
        "completed_checkpoint_contests": completed,
        "pending_until_next_checkpoint": (CHECKPOINT_SIZE - (len(evaluated_contests) % CHECKPOINT_SIZE)) % CHECKPOINT_SIZE,
        "latest_checkpoint": checkpoints[-1] if checkpoints else None,
        "checkpoints": checkpoints,
        "integrity": integrity,
    }
    assert_safe_report(report)
    report["report_hash"] = _report_hash(report)
    return report


def assert_safe_report(value: object, path: str = "root") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).lower()
            if normalized in FORBIDDEN_PUBLIC_KEYS:
                raise ValueError(f"Campo acionável proibido no relatório: {path}.{key}")
            assert_safe_report(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            assert_safe_report(child, f"{path}[{index}]")
