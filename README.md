# llm-kb-bench

> Karpathy on Karpathy: benchmarking LLM knowledge base tools on their inspiration's own work.

A reproducible benchmark of LLM-compiled knowledge base tools, measuring token cost, query accuracy, drift detection, and operational complexity on the same corpus.

## What This Is

After Andrej Karpathy posted his [LLM Knowledge Bases gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) on April 3, 2026, the community shipped at least five implementations within four days. Graphify hit 7,000 stars in two days. Cole Medin built a Claude Code memory variant. Three more implementations followed.

Every blog post describes one tool. Nobody benchmarks them against each other.

This repo does. Same corpus, same metrics, same methodology, different tools. The numbers settle the comparison.

## What This Is Not

- Yet another LLM knowledge base implementation
- A recommendation engine (we publish numbers, you pick)
- A long-term maintenance project (each phase is shippable; we can stop after any)

## Status

**Phase 1 (v0.1):** In planning. Head-to-head benchmark of Graphify vs claude-memory-compiler.

See `docs/plans/2026-04-08-llm-kb-bench-design.md` (one level up) for the full design.

## Phase Plan

| Phase | Scope | Status |
|-------|-------|--------|
| v0.1 | Graphify vs claude-memory-compiler head-to-head | Planning |
| v0.2 | Add llm-wiki-compiler, karpathy-wiki, karpathy-llm-wiki | Not started |
| v0.3 | Add baselines (LangChain RAG, GraphRAG) | Not started |
| v0.4 | CI + live dashboard | Optional |

## Metrics

Every tool is measured on:

1. Setup time (clone to first compile)
2. Compile token cost
3. Compile wall time
4. Storage size
5. Query token cost
6. Query latency (P50, P95)
7. Query accuracy (LLM-as-judge with rubric)
8. Drift detection support
9. Output portability
10. Operational complexity (1-5 rating)

## Corpus

Karpathy's public material, pinned by SHA256:

- **Repos:** nanoGPT, micrograd, llm.c
- **Essays:** Software 2.0, A Recipe for Training Neural Networks, Yes You Should Understand Backprop
- **Talks:** State of GPT, LLM OS

About 50 files. Mix of code, markdown, and prose. Reproducible months from now.

## Reproducibility

```bash
git clone <this-repo>
cd llm-kb-bench
./scripts/run_all.sh
```

That's it. SHA256-verified corpus. Documented LLM-as-judge prompts. Every run snapshotted under `results/<date>/`.

## License

MIT. Use the numbers. Cite the repo.

## Author

Built by [Jothiswaran Arumugam](https://www.linkedin.com/in/jothiswaranarumugam) as part of [Jo's Cloud AI Hub](https://www.linkedin.com/newsletters/jos-cloud-ai-hub-7242091893717741568) newsletter research.
