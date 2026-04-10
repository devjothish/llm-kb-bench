"""Wrapper for Graphify (safishamsi/graphify)."""

import subprocess
import time
import json
from pathlib import Path
from tools.base import ToolWrapper
from benchmarks.models import SetupResult, CompileResult, QueryResult, LintResult


class GraphifyWrapper(ToolWrapper):
    @property
    def name(self) -> str:
        return "graphify"

    @property
    def version(self) -> str:
        try:
            result = subprocess.run(
                ["graphify", "--version"], capture_output=True, text=True
            )
            return result.stdout.strip() or "unknown"
        except FileNotFoundError:
            return "not-installed"

    def setup(self) -> SetupResult:
        start = time.monotonic()
        try:
            subprocess.run(
                ["pip", "install", "graphifyy"], check=True, capture_output=True
            )
            subprocess.run(
                ["graphify", "install"], check=True, capture_output=True
            )
            elapsed = time.monotonic() - start
            return SetupResult(elapsed_seconds=elapsed, success=True)
        except subprocess.CalledProcessError as e:
            elapsed = time.monotonic() - start
            return SetupResult(elapsed_seconds=elapsed, success=False, error=str(e))

    def compile(self, raw_dir: Path, wiki_dir: Path) -> CompileResult:
        start = time.monotonic()
        try:
            result = subprocess.run(
                ["graphify", str(raw_dir), "--output", str(wiki_dir), "--json"],
                capture_output=True, text=True, check=True, timeout=600
            )
            elapsed = time.monotonic() - start

            output = {}
            try:
                output = json.loads(result.stdout)
            except json.JSONDecodeError:
                pass

            output_size = sum(
                f.stat().st_size for f in wiki_dir.rglob("*") if f.is_file()
            ) if wiki_dir.exists() else 0

            return CompileResult(
                elapsed_seconds=elapsed,
                input_tokens=output.get("input_tokens", 0),
                output_tokens=output.get("output_tokens", 0),
                output_size_bytes=output_size,
                success=True,
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            elapsed = time.monotonic() - start
            return CompileResult(
                elapsed_seconds=elapsed, input_tokens=0, output_tokens=0,
                output_size_bytes=0, success=False, error=str(e)
            )

    def query(self, question: str) -> QueryResult:
        start = time.monotonic()
        try:
            result = subprocess.run(
                ["graphify", "query", question, "--json"],
                capture_output=True, text=True, check=True, timeout=120
            )
            elapsed = time.monotonic() - start

            output = {}
            try:
                output = json.loads(result.stdout)
            except json.JSONDecodeError:
                output = {"answer": result.stdout}

            return QueryResult(
                elapsed_seconds=elapsed,
                input_tokens=output.get("input_tokens", 0),
                output_tokens=output.get("output_tokens", 0),
                answer=output.get("answer", result.stdout),
                cited_sources=output.get("cited_sources", []),
                success=True,
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
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
