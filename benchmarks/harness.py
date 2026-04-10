"""Core benchmark runner."""

import json
import time
from datetime import datetime, timezone
from pathlib import Path

from benchmarks.models import BenchmarkRun, JudgeGrade, CompileResult
from benchmarks.judge import load_qa_set, grade_answer
from tools.base import ToolWrapper
from tools.graphify.wrapper import GraphifyWrapper
from tools.claude_memory_compiler.wrapper import ClaudeMemoryCompilerWrapper

TOOL_REGISTRY: dict[str, type[ToolWrapper]] = {
    "graphify": GraphifyWrapper,
    "claude-memory-compiler": ClaudeMemoryCompilerWrapper,
}

CORPUS_RAW_DIR = Path("corpus/raw")
RESULTS_DIR = Path("results")


def discover_tools() -> list[ToolWrapper]:
    return [cls() for cls in TOOL_REGISTRY.values()]


def run_benchmark(tool: ToolWrapper, run_dir: Path) -> BenchmarkRun:
    print(f"\n{'='*60}")
    print(f"Benchmarking: {tool.name}")
    print(f"{'='*60}")

    wiki_dir = run_dir / "wiki" / tool.name
    wiki_dir.mkdir(parents=True, exist_ok=True)

    # 1. Setup
    print(f"  [setup] Installing {tool.name}...")
    setup_result = tool.setup()
    print(f"  [setup] {'OK' if setup_result.success else 'FAILED'} ({setup_result.elapsed_seconds:.1f}s)")

    if not setup_result.success:
        print(f"  [setup] Error: {setup_result.error}")
        return BenchmarkRun(
            tool_name=tool.name, tool_version=tool.version,
            setup=setup_result,
            compile=CompileResult(0, 0, 0, 0, False, "Setup failed"),
            queries=[], lint=None, drift_detection_supported=False,
            output_portable=False, operational_complexity=0,
            operational_complexity_rationale="Setup failed",
        )

    # 2. Compile
    print(f"  [compile] Compiling corpus...")
    compile_result = tool.compile(CORPUS_RAW_DIR, wiki_dir)
    print(f"  [compile] {'OK' if compile_result.success else 'FAILED'} "
          f"({compile_result.elapsed_seconds:.1f}s, {compile_result.total_tokens} tokens)")

    # 3. Query
    qa_set = load_qa_set()
    query_results = []
    grades = []
    print(f"  [query] Running {len(qa_set)} questions...")

    for i, q in enumerate(qa_set):
        qr = tool.query(q["question"])
        query_results.append(qr)

        if qr.success and qr.answer:
            grade = grade_answer(q, qr.answer)
            grades.append(JudgeGrade(
                question=q["question"], tool_answer=qr.answer,
                grade=grade["grade"], rationale=grade["rationale"],
                difficulty=q["difficulty"],
            ))
            print(f"    Q{i+1}: grade={grade['grade']}/3 ({qr.elapsed_seconds:.1f}s)")
        else:
            grades.append(JudgeGrade(
                question=q["question"], tool_answer="",
                grade=0, rationale="Query failed", difficulty=q["difficulty"],
            ))
            print(f"    Q{i+1}: FAILED")

    # 4. Lint
    print(f"  [lint] Running lint pass...")
    lint_result = tool.lint()
    print(f"  [lint] {'Supported' if lint_result.supported else 'Not supported'}")

    return BenchmarkRun(
        tool_name=tool.name, tool_version=tool.version,
        setup=setup_result, compile=compile_result,
        queries=query_results, lint=lint_result,
        drift_detection_supported=lint_result.supported,
        output_portable=True, operational_complexity=2,
        operational_complexity_rationale="pip install + API key",
        grades=grades,
    )


def run_all() -> None:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    run_dir = RESULTS_DIR / today
    run_dir.mkdir(parents=True, exist_ok=True)

    tools = discover_tools()
    results = []

    for tool in tools:
        run = run_benchmark(tool, run_dir)
        results.append(run)

        result_path = run_dir / f"{tool.name}.json"
        with open(result_path, "w") as f:
            json.dump(run.to_dict(), f, indent=2)
        print(f"\n  [saved] {result_path}")

    summary = {"date": today, "tools": [r.to_dict() for r in results]}
    summary_path = run_dir / "summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    latest = RESULTS_DIR / "latest"
    if latest.is_symlink():
        latest.unlink()
    latest.symlink_to(today)

    print(f"\n{'='*60}")
    print(f"Benchmark complete. Results in {run_dir}")
    print(f"{'='*60}")
