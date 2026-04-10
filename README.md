# llm-kb-bench

> Karpathy on Karpathy: benchmarking LLM knowledge base tools on their inspiration's own work.

A reproducible benchmark of LLM-compiled knowledge base tools. Same corpus, same synthesis model, same judge, different retrieval methods.

## What This Compares

Two fundamentally different approaches to building a queryable knowledge base:

| | **Graphify** | **Naive RAG** |
|---|---|---|
| **Retrieval method** | AST extraction + graph traversal | Chunk + embed + vector similarity |
| **Compile step** | Deterministic (zero LLM tokens) | Deterministic (local embeddings) |
| **Query step** | Graph BFS/DFS -> Haiku synthesis | Top-5 chunks -> Haiku synthesis |
| **What you get** | Interactive knowledge graph + JSON | In-memory vector store |

Both tools use **the same LLM (Claude Haiku)** for answer synthesis. The only variable is the retrieval method. This is what makes the comparison fair.

## Results (v0.1)

| Metric | graphify | naive-rag |
|--------|----------|-----------|
| Setup time | 0.2s | 5.2s |
| Compile tokens | 0 (local AST) | 0 (local embeddings) |
| Compile time | **0.3s** | 16.5s |
| Storage size | 578 KB (JSON + HTML) | ~0 KB (in-memory) |
| Avg query tokens | 3,439 | 1,436 |
| Avg query latency | 4.47s | 3.56s |
| Accuracy | **40.0%** | 36.7% |
| Drift detection | No | No |
| Output portable | Yes (JSON + HTML) | No (in-memory DB) |
| Complexity (1-5) | 2 | 2 |

**Key finding:** With the same synthesis model (Haiku), graph traversal retrieval (Graphify) matches vector similarity retrieval (naive RAG) on accuracy (40% vs 37%) while compiling 55x faster with zero tokens. Graphify uses more tokens per query (larger graph context) but produces a portable, inspectable knowledge graph as a side effect.

> Run `./scripts/run_all.sh` to reproduce these numbers.

### Charts

![Compilation Cost](reports/charts/compile_comparison.png)
![Query Accuracy](reports/charts/accuracy_comparison.png)
![Query Latency](reports/charts/query_latency.png)

## Why This Benchmark Exists

After Karpathy posted his [LLM Knowledge Bases gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f), five implementations shipped in four days. Every blog post describes one tool. Nobody benchmarks them against each other with reproducible methodology.

This repo does. One command reproduces everything. The methodology is documented. The judge prompt is auditable.

## Fair Comparison Design

A naive benchmark would compare Graphify's graph node output against RAG's prose output. That's unfair because Graphify returns structural data while RAG returns natural language. The judge (which grades prose quality) would always favor RAG.

We fix this by adding the same LLM synthesis step to both tools:

```
Graphify:  corpus -> AST extraction -> graph -> BFS traversal -> [Haiku synthesis] -> answer
Naive RAG: corpus -> chunking -> embeddings -> similarity search -> [Haiku synthesis] -> answer
```

The retrieval method is the only variable. The synthesis model is controlled.

## Reproduce

```bash
git clone https://github.com/devjothish/llm-kb-bench
cd llm-kb-bench
pip install -e ".[dev]"
export ANTHROPIC_API_KEY="your-key"
./scripts/run_all.sh
```

Requires: Python 3.10+, Anthropic API key (for query synthesis and judge grading).

## Corpus

Karpathy's public material (~71 files):
- **Repos:** nanoGPT, micrograd, llm.c
- **Blog posts:** Software 2.0, A Recipe for Training Neural Networks, Yes You Should Understand Backprop, Deep Neural Nets 33 Years Ago

See [corpus/README.md](corpus/README.md) for details.

## Methodology

10 metrics measured per tool. Accuracy graded by Claude Haiku using a strict 0-3 rubric with 20% human spot-checks. Both tools use the same synthesis model (Haiku) so the judge grades apples-to-apples. Full methodology: [METHODOLOGY.md](METHODOLOGY.md).

## Adding a Tool

1. Create `tools/<tool_name>/wrapper.py` implementing `ToolWrapper`
2. Ensure `query()` returns a natural language answer (add LLM synthesis if the tool returns structural data)
3. Register in `benchmarks/harness.py` `TOOL_REGISTRY`
4. Run `./scripts/run_all.sh`
5. Submit a PR

## License

MIT

## Author

Built by [Jothiswaran Arumugam](https://www.linkedin.com/in/jothiswaranarumugam) as part of [Jo's Cloud AI Hub](https://www.linkedin.com/newsletters/jos-cloud-ai-hub-7242091893717741568) newsletter research.
