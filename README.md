# llm-kb-bench

> Karpathy on Karpathy: benchmarking LLM knowledge base tools on their inspiration's own work.

A reproducible benchmark of LLM-compiled knowledge base tools. Same corpus, same metrics, same methodology, different tools.

## Results (v0.1)

| Metric | graphify | naive-rag |
|--------|----------|-----------|
| Setup time | 0.1s | 2.2s |
| Compile tokens | 0 (local AST) | 0 (local embeddings) |
| Compile time | 0.1s | 14.4s |
| Storage size | 578 KB | ~0 KB (in-memory) |
| Avg query tokens | 0 | 1,428 |
| Avg query latency | 0.15s | 3.06s |
| Accuracy | 10.0% | 40.0% |
| Drift detection | No | No |
| Output portable | Yes (JSON + HTML) | No (in-memory DB) |
| Complexity (1-5) | 2 | 2 |

> Graphify compiles 140x faster with zero LLM tokens (pure AST extraction) but returns graph nodes, not prose. Naive RAG is slower and costs tokens per query but produces natural language answers the judge can grade. Run `./scripts/run_all.sh` to reproduce.

### Charts

![Compilation Cost](reports/charts/compile_comparison.png)
![Query Accuracy](reports/charts/accuracy_comparison.png)
![Query Latency](reports/charts/query_latency.png)

## Reproduce

```bash
git clone https://github.com/<owner>/llm-kb-bench
cd llm-kb-bench
pip install -e ".[dev]"
./scripts/run_all.sh
```

Requires: Python 3.10+, Anthropic API key (for LLM-as-judge grading).

## Corpus

Karpathy's public material, pinned by SHA256:
- **Repos:** nanoGPT, micrograd, llm.c
- **Blog posts:** Software 2.0, A Recipe for Training Neural Networks, Yes You Should Understand Backprop, Deep Neural Nets 33 Years Ago

~50 files. Mix of code, markdown, and prose. See [corpus/README.md](corpus/README.md) for details.

## Methodology

10 metrics measured per tool. Accuracy graded by Claude Sonnet using a strict 0-3 rubric with 20% human spot-checks. Full methodology: [METHODOLOGY.md](METHODOLOGY.md).

## Adding a Tool

1. Create `tools/<tool_name>/wrapper.py` implementing `ToolWrapper`
2. Register in `benchmarks/harness.py` `TOOL_REGISTRY`
3. Run `./scripts/run_all.sh`
4. Submit a PR

## License

MIT

## Author

Built by [Jothiswaran Arumugam](https://www.linkedin.com/in/jothiswaranarumugam) as part of [Jo's Cloud AI Hub](https://www.linkedin.com/newsletters/jos-cloud-ai-hub-7242091893717741568) newsletter research.
