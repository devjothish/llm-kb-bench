"""Generate comparison charts and summary from benchmark results."""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

RESULTS_DIR = Path("results")
CHARTS_DIR = Path("reports/charts")


def load_latest_results() -> dict:
    latest = RESULTS_DIR / "latest"
    if not latest.exists():
        raise FileNotFoundError("No results found. Run benchmarks first.")
    summary = latest / "summary.json"
    with open(summary) as f:
        return json.load(f)


def chart_compile_comparison(results: dict) -> None:
    tools = [t["tool_name"] for t in results["tools"]]
    tokens = [t["compile"]["total_tokens"] for t in results["tools"]]
    times = [t["compile"]["elapsed_seconds"] for t in results["tools"]]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("Compilation Cost: Graphify vs claude-memory-compiler", fontsize=14)

    colors = ["#7c3aed", "#059669"]

    ax1.bar(tools, tokens, color=colors[:len(tools)])
    ax1.set_ylabel("Total Tokens")
    ax1.set_title("Token Cost")
    for i, v in enumerate(tokens):
        ax1.text(i, v + max(tokens)*0.02, f"{v:,}", ha="center", fontsize=10)

    ax2.bar(tools, times, color=colors[:len(tools)])
    ax2.set_ylabel("Seconds")
    ax2.set_title("Wall Time")
    for i, v in enumerate(times):
        ax2.text(i, v + max(times)*0.02, f"{v:.1f}s", ha="center", fontsize=10)

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "compile_comparison.png", dpi=150, bbox_inches="tight")
    plt.close()


def chart_accuracy_comparison(results: dict) -> None:
    tools = [t["tool_name"] for t in results["tools"]]
    accuracy = [t["accuracy"]["percentage"] for t in results["tools"]]

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ["#7c3aed", "#059669"]

    ax.bar(tools, accuracy, color=colors[:len(tools)])
    ax.set_ylabel("Accuracy (%)")
    ax.set_title("Query Accuracy (LLM-as-Judge, 10 Questions)")
    ax.set_ylim(0, 100)

    for i, v in enumerate(accuracy):
        ax.text(i, v + 2, f"{v:.1f}%", ha="center", fontsize=12, fontweight="bold")

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "accuracy_comparison.png", dpi=150, bbox_inches="tight")
    plt.close()


def chart_query_latency(results: dict) -> None:
    tools = [t["tool_name"] for t in results["tools"]]
    latencies = [
        [q["elapsed_seconds"] for q in t["queries"]]
        for t in results["tools"]
    ]

    fig, ax = plt.subplots(figsize=(8, 5))
    bp = ax.boxplot(latencies, labels=tools, patch_artist=True)
    colors = ["#7c3aed", "#059669"]
    for patch, color in zip(bp["boxes"], colors[:len(tools)]):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax.set_ylabel("Seconds")
    ax.set_title("Query Latency Distribution")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "query_latency.png", dpi=150, bbox_inches="tight")
    plt.close()


def generate_summary_table(results: dict) -> str:
    tools = results["tools"]
    rows = []
    rows.append("| Metric | " + " | ".join(t["tool_name"] for t in tools) + " |")
    rows.append("|--------|" + "|".join("--------|" for _ in tools))

    rows.append("| Setup time | " + " | ".join(
        f"{t['setup']['elapsed_seconds']:.1f}s" for t in tools) + " |")
    rows.append("| Compile tokens | " + " | ".join(
        f"{t['compile']['total_tokens']:,}" for t in tools) + " |")
    rows.append("| Compile time | " + " | ".join(
        f"{t['compile']['elapsed_seconds']:.1f}s" for t in tools) + " |")
    rows.append("| Storage size | " + " | ".join(
        f"{t['compile']['output_size_bytes']/1024:.0f} KB" for t in tools) + " |")

    avg_query_tokens = []
    for t in tools:
        qtokens = [q["total_tokens"] for q in t["queries"]]
        avg = sum(qtokens) / len(qtokens) if qtokens else 0
        avg_query_tokens.append(avg)
    rows.append("| Avg query tokens | " + " | ".join(
        f"{v:,.0f}" for v in avg_query_tokens) + " |")

    avg_latency = []
    for t in tools:
        lats = [q["elapsed_seconds"] for q in t["queries"]]
        avg = sum(lats) / len(lats) if lats else 0
        avg_latency.append(avg)
    rows.append("| Avg query latency | " + " | ".join(
        f"{v:.2f}s" for v in avg_latency) + " |")

    rows.append("| Accuracy | " + " | ".join(
        f"{t['accuracy']['percentage']:.1f}%" for t in tools) + " |")
    rows.append("| Drift detection | " + " | ".join(
        "Yes" if t["drift_detection_supported"] else "No" for t in tools) + " |")
    rows.append("| Output portable | " + " | ".join(
        "Yes" if t["output_portable"] else "No" for t in tools) + " |")
    rows.append("| Complexity (1-5) | " + " | ".join(
        str(t["operational_complexity"]) for t in tools) + " |")

    return "\n".join(rows)


def generate_all() -> None:
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    results = load_latest_results()

    print("Generating charts...")
    chart_compile_comparison(results)
    chart_accuracy_comparison(results)
    chart_query_latency(results)

    print("Generating summary table...")
    table = generate_summary_table(results)
    summary_md = RESULTS_DIR / "latest" / "summary.md"
    summary_md.write_text(f"# Benchmark Results: {results['date']}\n\n{table}\n")

    print(f"Charts saved to {CHARTS_DIR}")
    print(f"Summary saved to {summary_md}")


if __name__ == "__main__":
    generate_all()
