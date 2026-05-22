import json
import os
from pathlib import Path

import requests
from sklearn.metrics import accuracy_score


EVAL_PATH = Path("evals/bank_policy_eval.jsonl")
REPORT_PATH = Path("evals/metrics_report.json")
API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1/ask")


def load_cases():
    with EVAL_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def map_status_to_behavior(status: str, answer: str) -> str:
    answer_lower = (answer or "").lower()

    if status == "refused":
        return "refuse"

    if status == "needs_human_review":
        if "draft" in answer_lower or "черновик" in answer_lower:
            return "draft_with_human_review"
        return "escalate"

    if status == "answered":
        return "answer_with_sources"

    return "unknown"


def is_match(expected: str, predicted: str) -> bool:
    if expected == predicted:
        return True
    if expected == "refuse_or_escalate" and predicted in ("refuse", "escalate", "draft_with_human_review"):
        return True
    return False


def main():
    y_true = []
    y_pred = []
    results = []

    for case in load_cases():
        payload = {"user_id": "eval_runner", "question": case["question"], "channel": "eval"}
        try:
            res = requests.post(API_URL, json=payload, timeout=180)
            res.raise_for_status()
            data = res.json()
        except requests.RequestException as e:
            data = {"status": "error", "answer": str(e), "risk": None, "judge_score": None}

        predicted = map_status_to_behavior(data.get("status", ""), data.get("answer", ""))
        expected = case["expected_behavior"]

        y_true.append("match" if is_match(expected, predicted) else "miss")
        y_pred.append("match")

        results.append(
            {
                "id": case["id"],
                "question": case["question"],
                "expected": expected,
                "predicted": predicted,
                "status": data.get("status"),
                "judge_score": data.get("judge_score"),
            }
        )

    exact_match = accuracy_score(y_true, y_pred)

    report = {
        "exact_match": exact_match,
        "total_cases": len(results),
        "results": results,
    }

    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
