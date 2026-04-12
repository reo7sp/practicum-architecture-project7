import os
import sys
import json
import yaml
import datetime
import pytest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "Task4"))
os.chdir(ROOT / "Task4")

from rag import RAGBot

HERE = Path(__file__).resolve().parent
LOGS_FILE = HERE / "logs" / "logs.jsonl"
QUESTIONS = yaml.safe_load((HERE / "golden_questions.yaml").read_text(encoding="utf-8"))
MAX_RETRIES = 3


@pytest.fixture(scope="session")
def bot():
    return RAGBot()


@pytest.mark.parametrize("item", QUESTIONS, ids=[q["id"] for q in QUESTIONS])
def test_question(bot, item):
    attempts = MAX_RETRIES if item["expected_answer"] else 1
    answer, sources, success = "", [], False
    for _ in range(attempts):
        r = bot.generate_response(item["question"])
        answer = r.get("answer", "")
        sources = [s.get("source", "") for s in r.get("sources", [])]
        success = is_success(answer, item["expected_answer"], item.get("keywords", []))
        if success:
            break

    write_log({
        "id": item["id"],
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
        "query": item["question"],
        "coverage_status": item["coverage_status"],
        "expected_answer": item["expected_answer"],
        "chunks_found": bool(sources),
        "answer_length": len(answer),
        "success": success,
        "sources": sources,
        "answer_preview": answer[:300],
    })

    assert success, (
        f"coverage_status={item['coverage_status']} expected_answer={item['expected_answer']}\n"
        f"answer: {answer[:300]}"
    )


def is_success(answer: str, expected: bool, keywords: list) -> bool:
    if expected:
        return not is_refusal(answer) and (
            not keywords or any(kw.lower() in answer.lower() for kw in keywords)
        )
    return is_refusal(answer)


REFUSALS = ["не знаю", "нет информации", "не могу ответить", "нет данных"]


def is_refusal(answer: str) -> bool:
    return len(answer.strip()) < 80 or any(p in answer.lower() for p in REFUSALS)


def write_log(entry: dict) -> None:
    LOGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOGS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


