"""LLM-as-judge for grading query accuracy."""

import json
import yaml
from pathlib import Path

import anthropic

JUDGE_PROMPT_PATH = Path("benchmarks/judge_prompt.md")
QA_SET_PATH = Path("benchmarks/qa_set.yaml")


def load_judge_prompt() -> str:
    return JUDGE_PROMPT_PATH.read_text()


def load_qa_set() -> list[dict]:
    with open(QA_SET_PATH) as f:
        data = yaml.safe_load(f)
    return data["questions"]


def grade_answer(
    question: dict,
    tool_answer: str,
    client: anthropic.Anthropic | None = None,
    model: str = "claude-haiku-4-5-20251001",
) -> dict:
    if client is None:
        client = anthropic.Anthropic()

    prompt_template = load_judge_prompt()
    prompt = prompt_template.replace("{question}", question["question"])
    prompt = prompt.replace("{expected_concepts}", ", ".join(question["expected_concepts"]))
    prompt = prompt.replace("{source_files}", ", ".join(question["source_files"]))
    prompt = prompt.replace("{tool_answer}", tool_answer)

    response = client.messages.create(
        model=model,
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text.strip()

    # Strip markdown code fences if present
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()

    try:
        result = json.loads(text)
        return {
            "grade": int(result["grade"]),
            "rationale": result["rationale"],
        }
    except (json.JSONDecodeError, KeyError, ValueError):
        return {
            "grade": 0,
            "rationale": f"Judge response not parseable: {text[:100]}",
        }
