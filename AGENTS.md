# AGENTS.md - llm-kb-bench

Schema and workflow definition for any agent working on llm-kb-bench. Compatible with Claude Code, Codex, OpenCode, and other agent harnesses that read AGENTS.md.

## Agent Identity

You are working on `llm-kb-bench`, an open source benchmark repository that measures and compares existing Karpathy-style LLM knowledge base tools.

Read `CLAUDE.md` in this directory before doing any work. It contains project rules that override default behavior.

## Cardinal Rules

1. **This is a benchmark, not a tool.** Never propose building a new LLM KB compiler. The space already has 5+ implementations. Our differentiator is reproducible measurement.

2. **Reproducibility over cleverness.** A simple metric anyone can reproduce beats a sophisticated metric only we can compute.

3. **Honest charts only.** No truncated axes. No cherry-picked corpora. No hiding tool failures. If a tool crashes on our corpus, that's the result.

4. **One phase at a time.** Don't start Phase 2 work until Phase 1 ships. Don't half-finish phases.

5. **Don't modify the corpus to make a tool look better.** The corpus is fixed and SHA256-pinned. If a tool needs special handling, that goes in the wrapper, not the corpus.

## Workflow

When asked to add a new tool to the benchmark:

1. Read the tool's documentation
2. Install it locally and run a manual smoke test
3. Create `tools/<tool-name>/` with a wrapper that implements the `ToolWrapper` interface (see CLAUDE.md)
4. Add the tool to `benchmarks/harness.py`
5. Run the full benchmark
6. Verify results are reasonable (no obvious bugs)
7. Update the README with the new tool's row in the comparison tables

When asked to add a new metric:

1. Document why it matters and what it measures
2. Add it to `benchmarks/metrics.py`
3. Update the harness to capture it for every tool
4. Re-run the full benchmark on existing tools so all numbers come from the same metric set
5. Update the README

When asked to update the Q&A set:

1. New questions go in `benchmarks/qa_set.yaml` with difficulty tier, expected concepts, and source files
2. Re-run the accuracy benchmark
3. Spot-check at least 20% of new answers manually
4. Verify the LLM-as-judge isn't biased toward one tool's output style

## Tool Interface

```python
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass
class SetupResult:
    elapsed_seconds: float
    success: bool
    error: Optional[str] = None

@dataclass
class CompileResult:
    elapsed_seconds: float
    input_tokens: int
    output_tokens: int
    output_size_bytes: int
    success: bool
    error: Optional[str] = None

@dataclass
class QueryResult:
    elapsed_seconds: float
    input_tokens: int
    output_tokens: int
    answer: str
    cited_sources: list[str]
    success: bool
    error: Optional[str] = None

@dataclass
class LintResult:
    elapsed_seconds: float
    issues_found: int
    issues: list[dict]
    success: bool
    supported: bool
    error: Optional[str] = None

class ToolWrapper:
    name: str
    version: str

    def setup(self) -> SetupResult: ...
    def compile(self, raw_dir: Path, wiki_dir: Path) -> CompileResult: ...
    def query(self, question: str) -> QueryResult: ...
    def lint(self) -> LintResult: ...
```

Every tool wrapper must implement this exact interface. Do not subclass it differently.

## Forbidden Actions

- Do not commit corpus files to the repo. The download script fetches them at run time.
- Do not commit results from a single run as authoritative. Run the full benchmark at least twice.
- Do not modify a tool's source to make it work with our wrapper. Wrap around the tool, not into it.
- Do not add LangChain or vector DB dependencies to the core harness. Those belong only in the Phase 3 baselines.
- Do not delete results from older runs. They're the audit trail.

## Reference Files

- `CLAUDE.md` - project rules (this is enforced for Claude Code sessions)
- `README.md` - the public-facing pitch and current results
- `METHODOLOGY.md` - detailed metric definitions and reproducibility steps
- `../../docs/plans/2026-04-08-llm-kb-bench-design.md` - full design doc with rationale
