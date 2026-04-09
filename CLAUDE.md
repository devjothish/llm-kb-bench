# CLAUDE.md - llm-kb-bench

This file provides guidance to Claude Code when working on the llm-kb-bench project.

## Project Identity

`llm-kb-bench` is an open source **benchmark repository**, not a tool implementation. We measure and compare existing LLM knowledge base tools. We do not build a new one.

**This was a deliberate choice.** The space already has 5+ implementations. Building a 6th has no defensible differentiator. The gap is reproducible benchmarking. That's what we fill.

If a future session suggests "let's just build a simple LLM KB tool," that's a regression. Push back.

## Goal

Get GitHub stars. Become the canonical citation for "which LLM KB tool should I use?" Drive subscribers to Jo's Cloud AI Hub newsletter as a side effect.

## Working Principles

1. **Reproducibility is the product.** Every metric must be reproducible by a stranger with one command. If we can't reproduce it, we don't publish it.

2. **No cherry-picking.** Charts use honest axes. Methodology is documented. Tool authors should be able to read our results and verify them independently.

3. **LLM-as-judge with audit trail.** Accuracy is graded by Claude Sonnet using a strict rubric in `benchmarks/judge_prompt.md`. 20% of answers get human spot-checks.

4. **Each phase is shippable.** Don't start Phase 2 until Phase 1 is done. Don't half-finish phases. If we stop after Phase 1, the repo still stands.

5. **Tag the tool authors when we publish results.** They'll either link back (good) or push back (also good, drives engagement).

## Working with Tool Wrappers

Each tool gets a wrapper directory under `tools/<tool-name>/`. The wrapper exposes a uniform interface to the harness:

```python
class ToolWrapper:
    def setup(self) -> SetupResult        # Install, configure, return setup time
    def compile(self, raw_dir, wiki_dir) -> CompileResult
    def query(self, question: str) -> QueryResult
    def lint(self) -> LintResult           # Optional, returns None if not supported
```

When adding a new tool, only this interface and a small wrapper script should be required. If you're modifying the harness to accommodate one tool, that's a smell. The harness should be tool-agnostic.

## Scoping Rules

**In scope:**
- Benchmarking existing tools
- Measuring metrics defined in the design doc
- Adding new tool wrappers
- Improving the Q&A set
- Improving the LLM-as-judge prompt
- Adding baselines (LangChain RAG, GraphRAG) in Phase 3

**Out of scope:**
- Building a new LLM KB compiler
- Recommending one tool over another in the README
- Adding tool features
- Long-term tool maintenance
- Forking any of the tools

## Where Things Live

- `corpus/` - the Karpathy material, downloaded from public sources, SHA256-verified
- `tools/<name>/` - per-tool wrapper directories
- `benchmarks/harness.py` - the benchmark runner
- `benchmarks/qa_set.yaml` - hand-curated questions for accuracy
- `benchmarks/judge_prompt.md` - LLM-as-judge rubric (auditable)
- `results/<date>/` - snapshotted run results
- `reports/charts/` - auto-generated comparison charts
- `scripts/run_all.sh` - one command to reproduce everything

## Reference

Full design doc: `../../docs/plans/2026-04-08-llm-kb-bench-design.md`
Project memory: claude-mem observation #5210
