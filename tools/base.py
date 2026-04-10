"""Abstract base class for tool wrappers."""

from abc import ABC, abstractmethod
from pathlib import Path
from benchmarks.models import SetupResult, CompileResult, QueryResult, LintResult


class ToolWrapper(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def version(self) -> str: ...

    @abstractmethod
    def setup(self) -> SetupResult: ...

    @abstractmethod
    def compile(self, raw_dir: Path, wiki_dir: Path) -> CompileResult: ...

    @abstractmethod
    def query(self, question: str) -> QueryResult: ...

    @abstractmethod
    def lint(self) -> LintResult: ...
