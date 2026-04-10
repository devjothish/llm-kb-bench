"""Wrapper for Graphify (safishamsi/graphify) using Python API.

Benchmark pipeline:
  1. Compile: deterministic AST extraction -> graph build -> cluster -> export
  2. Query: graph traversal retrieves relevant nodes -> Haiku synthesizes prose answer
  3. Both tools use the same LLM (Haiku) for answer synthesis so the judge
     grades apples-to-apples: same model, different retrieval methods.
"""

import json
import subprocess
import time
from pathlib import Path

import anthropic

from tools.base import ToolWrapper
from benchmarks.models import SetupResult, CompileResult, QueryResult, LintResult

SYNTHESIS_MODEL = "claude-haiku-4-5-20251001"


class GraphifyWrapper(ToolWrapper):
    def __init__(self):
        self._graph_path: Path | None = None
        self._raw_dir: Path | None = None

    @property
    def name(self) -> str:
        return "graphify"

    @property
    def version(self) -> str:
        try:
            import importlib.metadata
            return importlib.metadata.version("graphifyy")
        except Exception:
            return "unknown"

    def setup(self) -> SetupResult:
        start = time.monotonic()
        try:
            from graphify.extract import extract, collect_files
            from graphify.build import build
            from graphify.cluster import cluster
            from graphify.export import to_json, to_html
            # Verify Anthropic client works (needed for query synthesis)
            anthropic.Anthropic()
            elapsed = time.monotonic() - start
            return SetupResult(elapsed_seconds=elapsed, success=True)
        except (ImportError, anthropic.AuthenticationError) as e:
            elapsed = time.monotonic() - start
            return SetupResult(elapsed_seconds=elapsed, success=False, error=str(e))

    def compile(self, raw_dir: Path, wiki_dir: Path) -> CompileResult:
        start = time.monotonic()
        try:
            from graphify.extract import extract, collect_files
            from graphify.build import build
            from graphify.cluster import cluster
            from graphify.export import to_json, to_html

            wiki_dir.mkdir(parents=True, exist_ok=True)
            self._raw_dir = raw_dir

            # Step 1: Collect files and run deterministic AST extraction
            files = collect_files(Path(raw_dir))
            extractions = extract(files)

            if isinstance(extractions, dict):
                extractions = [extractions]

            # Step 2: Build NetworkX graph from extractions
            G = build(extractions)

            # Step 3: Cluster using Leiden algorithm (topology-based, no embeddings)
            communities = cluster(G)

            # Step 4: Export to JSON (queryable) and HTML (visual)
            graph_json = wiki_dir / "graph.json"
            to_json(G, communities, str(graph_json))
            to_html(G, communities, str(wiki_dir / "graph.html"))

            self._graph_path = graph_json

            elapsed = time.monotonic() - start

            output_size = sum(
                f.stat().st_size for f in wiki_dir.rglob("*") if f.is_file()
            )

            # Token cost is zero: AST extraction is fully local
            # Semantic extraction (docs, PDFs, images) would add tokens
            # but we benchmark the deterministic-only pipeline
            return CompileResult(
                elapsed_seconds=elapsed,
                input_tokens=0,
                output_tokens=0,
                output_size_bytes=output_size,
                success=True,
            )
        except Exception as e:
            elapsed = time.monotonic() - start
            return CompileResult(
                elapsed_seconds=elapsed, input_tokens=0, output_tokens=0,
                output_size_bytes=0, success=False, error=str(e)
            )

    def query(self, question: str) -> QueryResult:
        """Two-step query: graph traversal for retrieval, then LLM synthesis.

        Step 1: Graphify CLI does BFS/DFS traversal to find relevant nodes.
        Step 2: Feed the retrieved nodes to Haiku to produce a prose answer.

        This makes the benchmark fair: both tools (graphify and naive-rag) use
        the same LLM for answer synthesis. The only difference is the retrieval
        method (graph traversal vs vector similarity search).
        """
        start = time.monotonic()
        try:
            graph_path = self._graph_path
            if graph_path is None or not graph_path.exists():
                for p in Path("results").rglob("graph.json"):
                    if "graphify" in str(p):
                        graph_path = p
                        break

            if graph_path is None or not graph_path.exists():
                return QueryResult(
                    elapsed_seconds=0, input_tokens=0, output_tokens=0,
                    answer="", cited_sources=[], success=False,
                    error="No graph.json found. Run compile first."
                )

            # Step 1: Graph traversal retrieval
            result = subprocess.run(
                ["graphify", "query", question,
                 "--graph", str(graph_path),
                 "--budget", "3000"],
                capture_output=True, text=True, timeout=120
            )

            graph_context = result.stdout.strip()

            if not graph_context:
                return QueryResult(
                    elapsed_seconds=time.monotonic() - start,
                    input_tokens=0, output_tokens=0,
                    answer="No relevant nodes found in graph.",
                    cited_sources=[], success=True,
                )

            # Extract source file references from graph nodes
            cited = []
            for line in graph_context.split("\n"):
                if "src=" in line:
                    src_start = line.find("src=") + 4
                    src_end = line.find(" ", src_start)
                    if src_end == -1:
                        src_end = line.find("]", src_start)
                    if src_end > src_start:
                        cited.append(line[src_start:src_end])

            # Step 2: LLM synthesis (same model as naive-rag for fair comparison)
            client = anthropic.Anthropic()
            response = client.messages.create(
                model=SYNTHESIS_MODEL,
                max_tokens=500,
                messages=[{
                    "role": "user",
                    "content": (
                        f"You are answering a question about a codebase using "
                        f"knowledge graph nodes retrieved by Graphify.\n\n"
                        f"Question: {question}\n\n"
                        f"Retrieved graph nodes:\n{graph_context}\n\n"
                        f"Based on these graph nodes, answer the question concisely "
                        f"with specific details. Reference source files where possible."
                    )
                }],
            )

            answer = response.content[0].text
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens

            elapsed = time.monotonic() - start

            return QueryResult(
                elapsed_seconds=elapsed,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                answer=answer,
                cited_sources=list(set(cited)),
                success=True,
            )
        except Exception as e:
            elapsed = time.monotonic() - start
            return QueryResult(
                elapsed_seconds=elapsed, input_tokens=0, output_tokens=0,
                answer="", cited_sources=[], success=False, error=str(e)
            )

    def lint(self) -> LintResult:
        return LintResult(
            elapsed_seconds=0, issues_found=0, issues=[],
            success=True, supported=False
        )
