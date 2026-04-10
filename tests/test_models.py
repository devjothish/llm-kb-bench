from benchmarks.models import (
    SetupResult, CompileResult, QueryResult, LintResult, BenchmarkRun, JudgeGrade
)

def test_setup_result_creation():
    r = SetupResult(elapsed_seconds=12.5, success=True)
    assert r.elapsed_seconds == 12.5
    assert r.success is True
    assert r.error is None

def test_compile_result_creation():
    r = CompileResult(
        elapsed_seconds=45.0, input_tokens=5000, output_tokens=3000,
        output_size_bytes=102400, success=True
    )
    assert r.input_tokens == 5000
    assert r.total_tokens == 8000

def test_query_result_creation():
    r = QueryResult(
        elapsed_seconds=2.1, input_tokens=1000, output_tokens=500,
        answer="The loss function is cross_entropy",
        cited_sources=["nanoGPT/train.py"], success=True
    )
    assert r.total_tokens == 1500
    assert len(r.cited_sources) == 1

def test_lint_result_unsupported():
    r = LintResult(elapsed_seconds=0, issues_found=0, issues=[], success=True, supported=False)
    assert r.supported is False

def test_benchmark_run_to_dict():
    run = BenchmarkRun(
        tool_name="test-tool",
        tool_version="1.0.0",
        setup=SetupResult(elapsed_seconds=1.0, success=True),
        compile=CompileResult(
            elapsed_seconds=10.0, input_tokens=100, output_tokens=50,
            output_size_bytes=1024, success=True
        ),
        queries=[],
        lint=None,
        drift_detection_supported=False,
        output_portable=True,
        operational_complexity=2,
        operational_complexity_rationale="pip install + API key"
    )
    d = run.to_dict()
    assert d["tool_name"] == "test-tool"
    assert d["compile"]["total_tokens"] == 150
