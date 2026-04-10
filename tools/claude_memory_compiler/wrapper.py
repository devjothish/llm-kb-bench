"""Wrapper for claude-memory-compiler (coleam00)."""

import subprocess
import time
import json
from pathlib import Path
from tools.base import ToolWrapper
from benchmarks.models import SetupResult, CompileResult, QueryResult, LintResult


class ClaudeMemoryCompilerWrapper(ToolWrapper):
    def __init__(self):
        self._repo_dir = Path("tools/claude_memory_compiler/repo")

    @property
    def name(self) -> str:
        return "claude-memory-compiler"

    @property
    def version(self) -> str:
        pkg = self._repo_dir / "pyproject.toml"
        if pkg.exists():
            for line in pkg.read_text().splitlines():
                if line.strip().startswith("version"):
                    return line.split("=")[1].strip().strip('"')
        return "unknown"

    def setup(self) -> SetupResult:
        start = time.monotonic()
        try:
            if not self._repo_dir.exists():
                subprocess.run(
                    ["git", "clone", "--depth", "1",
                     "https://github.com/coleam00/claude-memory-compiler.git",
                     str(self._repo_dir)],
                    check=True, capture_output=True
                )
            subprocess.run(
                ["pip", "install", "-e", str(self._repo_dir)],
                check=True, capture_output=True
            )
            elapsed = time.monotonic() - start
            return SetupResult(elapsed_seconds=elapsed, success=True)
        except subprocess.CalledProcessError as e:
            elapsed = time.monotonic() - start
            return SetupResult(elapsed_seconds=elapsed, success=False, error=str(e))

    def compile(self, raw_dir: Path, wiki_dir: Path) -> CompileResult:
        start = time.monotonic()
        try:
            wiki_dir.mkdir(parents=True, exist_ok=True)
            result = subprocess.run(
                ["python", "-m", "claude_memory_compiler", "compile",
                 "--input", str(raw_dir), "--output", str(wiki_dir)],
                capture_output=True, text=True, check=True, timeout=600,
                cwd=str(self._repo_dir)
            )
            elapsed = time.monotonic() - start

            output_size = sum(
                f.stat().st_size for f in wiki_dir.rglob("*") if f.is_file()
            ) if wiki_dir.exists() else 0

            output = {}
            try:
                output = json.loads(result.stdout)
            except json.JSONDecodeError:
                pass

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
                ["python", "-m", "claude_memory_compiler", "query", question],
                capture_output=True, text=True, check=True, timeout=120,
                cwd=str(self._repo_dir)
            )
            elapsed = time.monotonic() - start

            return QueryResult(
                elapsed_seconds=elapsed,
                input_tokens=0,
                output_tokens=0,
                answer=result.stdout.strip(),
                cited_sources=[],
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
