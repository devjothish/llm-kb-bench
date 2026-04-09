# Methodology

How llm-kb-bench measures things, and how you can reproduce every number.

## Reproducibility Promise

Every benchmark run is reproducible by anyone with the same environment:

```bash
git clone https://github.com/<owner>/llm-kb-bench
cd llm-kb-bench
python -m venv .venv && source .venv/bin/activate
pip install -e .
./scripts/run_all.sh
```

The script:
1. Downloads the corpus from public sources
2. Verifies every file's SHA256 against `corpus/manifest.yaml`
3. Sets up each tool wrapper
4. Runs the benchmark across all tools
5. Generates charts and updates `results/<today>/`

If any SHA256 mismatches, the run fails. If any tool errors, the result is recorded as a failure (we don't hide it).

## The Corpus

Defined in `corpus/manifest.yaml` and downloaded by `corpus/download.py`. Sources are pinned by:
- Git commit SHA for repos
- SHA256 hash for files

Corpus content is **never committed to the repo**. It's fetched fresh at run time. This avoids licensing issues and forces reproducibility.

## Metrics

### 1. Setup time

Wall-clock seconds from invoking the wrapper's `setup()` method to a successful return. Includes pip installs, model downloads, and any first-run initialization. Captured by `time.monotonic()` deltas.

**Why it matters:** real installation pain. A tool that takes 30 minutes to set up has a different audience than one that runs in 30 seconds.

### 2. Compile token cost

Total LLM tokens consumed during the full corpus compilation. Captured from API response metadata (Anthropic, OpenAI, and Bedrock all expose token counts).

Reported as input tokens + output tokens, plus a USD cost calculated using current public pricing.

**Why it matters:** the hidden tax. A tool that uses 10x more tokens has a 10x higher operational cost.

### 3. Compile wall time

Seconds from `compile()` invocation to completion. Wall clock, not CPU time.

**Why it matters:** practical iteration speed. If compiling 50 docs takes 4 hours, the developer experience suffers.

### 4. Storage size

`du -sb` on the wiki output directory. Bytes, reported as human-readable.

**Why it matters:** how portable is the result. A tool that produces 50MB of artifacts is harder to share than one that produces 5MB.

### 5. Query token cost

Average input + output tokens per query, measured across the full Q&A set. Reported with USD cost.

**Why it matters:** the cost of asking a question. A tool with cheap compile but expensive queries has different economics than one with the opposite tradeoff.

### 6. Query latency

P50 and P95 in milliseconds, measured across the full Q&A set. Wall clock around the query call.

**Why it matters:** practical user experience. A tool that takes 30 seconds to answer is a different product than one that answers in 3.

### 7. Query accuracy

Score on the hand-curated Q&A set in `benchmarks/qa_set.yaml`. Each question has expected concepts and source files. Each tool's answer is graded 0-3 by Claude Sonnet using the rubric in `benchmarks/judge_prompt.md`.

Final accuracy is the mean score across all questions, reported as a percentage of the maximum (3.0).

20% of answers are spot-checked by a human to verify the judge isn't biased.

### 8. Drift detection support

Boolean: does the tool support a lint pass? If yes, document the invocation and what it detects.

**Why it matters:** RAG pipelines have zero drift detection. Karpathy's pattern includes lint as a first-class concept. Tools that implement it are different from tools that don't.

### 9. Output portability

Boolean + qualitative description: can you read the wiki without the tool installed?

- "Yes, plain markdown in folders" → highly portable
- "Yes, but requires the tool to render the graph view" → semi-portable
- "No, output is a SQLite database" → not portable

**Why it matters:** lock-in matters for production use.

### 10. Operational complexity

Subjective 1-5 rating with documented rationale:

- 1: Single binary, zero dependencies, runs anywhere
- 2: Python package + standard ML deps, runs locally
- 3: Requires API keys, model access, or specific runtime
- 4: Requires Docker, services, or persistent processes
- 5: Requires dedicated infrastructure (database, queue, orchestrator)

**Why it matters:** matches tool complexity to team capability.

## LLM-as-Judge

Accuracy grading uses Claude Sonnet (separate from any tool being benchmarked) with this rubric:

```
Question: {question}
Expected concepts: {expected_concepts}
Source files: {source_files}

Tool's answer: {tool_answer}

Grade this answer 0-3:
- 3: Covers ALL expected concepts. Cites correct source files. No hallucinations.
- 2: Covers MOST expected concepts. May miss minor details. Sources correct.
- 1: Partial answer. Misses key concepts OR cites wrong sources.
- 0: Wrong, missing, or hallucinated.

Output format: { "grade": <0-3>, "rationale": "<one sentence>" }
```

The full prompt lives in `benchmarks/judge_prompt.md`. Anyone can audit it.

## Spot-Check Protocol

For 20% of answers (selected by hash modulo to be deterministic), a human reviews:
1. The original question
2. The tool's answer
3. The judge's grade
4. The source files

The human records agreement or disagreement. If the disagreement rate exceeds 15%, we flag the judge prompt for revision before publishing results.

## Tool Wrapper Contract

Every tool wrapper implements the `ToolWrapper` interface defined in AGENTS.md. Wrappers do NOT modify the tool. They invoke the tool through its public interface and capture metrics.

If a tool requires environment-specific setup (API keys, file system layout), the wrapper documents that in `tools/<tool-name>/README.md`.

## Versioning

Every benchmark run records:
- Date and time
- Tool versions (from each tool's reported version, NOT inferred)
- Corpus manifest SHA256
- Harness version (git SHA)
- Judge model + version
- Pricing assumptions used for USD costs

Results are stored under `results/<YYYY-MM-DD>/` and never deleted. The `results/latest/` symlink points to the most recent run.

## Adding New Tools

See AGENTS.md for the workflow.
