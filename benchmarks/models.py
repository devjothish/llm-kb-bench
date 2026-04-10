"""Data models for benchmark results."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SetupResult:
    elapsed_seconds: float
    success: bool
    error: Optional[str] = None


@dataclass
class CompileResult:
    elapsed_seconds: float
    input_tokens: int
    output_tokens: int
    output_size_bytes: int
    success: bool
    error: Optional[str] = None

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


@dataclass
class QueryResult:
    elapsed_seconds: float
    input_tokens: int
    output_tokens: int
    answer: str
    cited_sources: list[str]
    success: bool
    error: Optional[str] = None

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


@dataclass
class LintResult:
    elapsed_seconds: float
    issues_found: int
    issues: list[dict]
    success: bool
    supported: bool
    error: Optional[str] = None


@dataclass
class JudgeGrade:
    question: str
    tool_answer: str
    grade: int
    rationale: str
    difficulty: str


@dataclass
class BenchmarkRun:
    tool_name: str
    tool_version: str
    setup: SetupResult
    compile: CompileResult
    queries: list[QueryResult]
    lint: Optional[LintResult]
    drift_detection_supported: bool
    output_portable: bool
    operational_complexity: int
    operational_complexity_rationale: str
    grades: list[JudgeGrade] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = {
            "tool_name": self.tool_name,
            "tool_version": self.tool_version,
            "setup": {"elapsed_seconds": self.setup.elapsed_seconds, "success": self.setup.success},
            "compile": {
                "elapsed_seconds": self.compile.elapsed_seconds,
                "input_tokens": self.compile.input_tokens,
                "output_tokens": self.compile.output_tokens,
                "total_tokens": self.compile.total_tokens,
                "output_size_bytes": self.compile.output_size_bytes,
                "success": self.compile.success,
            },
            "queries": [
                {
                    "elapsed_seconds": q.elapsed_seconds,
                    "input_tokens": q.input_tokens,
                    "output_tokens": q.output_tokens,
                    "total_tokens": q.total_tokens,
                    "success": q.success,
                }
                for q in self.queries
            ],
            "drift_detection_supported": self.drift_detection_supported,
            "output_portable": self.output_portable,
            "operational_complexity": self.operational_complexity,
            "operational_complexity_rationale": self.operational_complexity_rationale,
            "accuracy": {
                "mean_grade": (
                    sum(g.grade for g in self.grades) / len(self.grades)
                    if self.grades else 0
                ),
                "max_possible": 3.0,
                "percentage": (
                    sum(g.grade for g in self.grades) / (len(self.grades) * 3) * 100
                    if self.grades else 0
                ),
                "num_questions": len(self.grades),
            },
        }
        return d
