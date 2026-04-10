import yaml
from pathlib import Path

def test_qa_set_loads():
    qa_path = Path("benchmarks/qa_set.yaml")
    assert qa_path.exists()
    with open(qa_path) as f:
        data = yaml.safe_load(f)
    assert "questions" in data
    assert len(data["questions"]) >= 10

def test_qa_set_questions_have_required_fields():
    with open("benchmarks/qa_set.yaml") as f:
        data = yaml.safe_load(f)
    for q in data["questions"]:
        assert "question" in q
        assert "expected_concepts" in q
        assert "source_files" in q
        assert "difficulty" in q
        assert q["difficulty"] in [
            "factual_recall", "cross_document_synthesis",
            "conceptual_inference", "cross_format"
        ]

def test_judge_prompt_exists():
    assert Path("benchmarks/judge_prompt.md").exists()
