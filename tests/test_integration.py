"""Integration test: verify the full pipeline runs end-to-end."""

import subprocess
import json
from pathlib import Path
import pytest

@pytest.mark.integration
def test_corpus_download():
    """Verify corpus download produces files."""
    result = subprocess.run(
        ["python", "-m", "corpus.download"],
        capture_output=True, text=True, timeout=300,
        cwd="/Users/jothish/Jo-github-revstar/LinkedIN newsletter/projects/llm-kb-bench"
    )
    assert result.returncode == 0, f"Download failed: {result.stderr}"
    assert Path("corpus/raw").exists()
    raw_files = list(Path("corpus/raw").rglob("*"))
    assert len([f for f in raw_files if f.is_file()]) > 5

@pytest.mark.integration
def test_full_run_produces_results():
    """Run the full benchmark and verify output structure."""
    result = subprocess.run(
        ["bash", "scripts/run_all.sh"],
        capture_output=True, text=True, timeout=1800,
        cwd="/Users/jothish/Jo-github-revstar/LinkedIN newsletter/projects/llm-kb-bench"
    )
    latest = Path("results/latest")
    assert latest.exists() or latest.is_symlink()
    summary = latest / "summary.json"
    assert summary.exists()

    with open(summary) as f:
        data = json.load(f)
    assert "tools" in data
    assert len(data["tools"]) >= 1

    assert Path("reports/charts/compile_comparison.png").exists()
    assert Path("reports/charts/accuracy_comparison.png").exists()
