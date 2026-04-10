"""Wrapper for Graphify (safishamsi/graphify) using Python API."""

import subprocess
import time
from pathlib import Path

from tools.base import ToolWrapper
from benchmarks.models import SetupResult, CompileResult, QueryResult, LintResult


class GraphifyWrapper(ToolWrapper):
    def __init__(self):
        self._graph_path: Path | None = None

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
            elapsed = time.monotonic() - start
            return SetupResult(elapsed_seconds=elapsed, success=True)
        except ImportError as e:
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

            # Step 1: Collect files and extract (deterministic AST pass for code)
            files = collect_files(Path(raw_dir))
            extractions = extract(files)

            # extract() returns a single dict; build() expects a list
            if isinstance(extractions, dict):
                extractions = [extractions]

            # Step 2: Build graph from extractions
            G = build(extractions)

            # Step 3: Cluster using Leiden algorithm
            communities = cluster(G)

            # Step 4: Export to JSON and HTML
            graph_json = wiki_dir / "graph.json"
            to_json(G, communities, str(graph_json))
            to_html(G, communities, str(wiki_dir / "graph.html"))

            self._graph_path = graph_json

            elapsed = time.monotonic() - start

            output_size = sum(
                f.stat().st_size for f in wiki_dir.rglob("*") if f.is_file()
            )

            # AST extraction is local (zero LLM tokens)
            # Semantic extraction of docs/images would use tokens but
            # we're running the deterministic-only pipeline here
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
        start = time.monotonic()
        try:
            graph_path = self._graph_path
            if graph_path is None or not graph_path.exists():
                # Search for graph.json in results directories
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

            result = subprocess.run(
                ["graphify", "query", question, "--graph", str(graph_path)],
                capture_output=True, text=True, timeout=120
            )
            elapsed = time.monotonic() - start

            return QueryResult(
                elapsed_seconds=elapsed,
                input_tokens=0,
                output_tokens=0,
                answer=result.stdout.strip(),
                cited_sources=[],
                success=result.returncode == 0,
                error=result.stderr.strip() if result.returncode != 0 else None,
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
