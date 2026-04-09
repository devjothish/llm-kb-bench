#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$ROOT_DIR"

echo "=== llm-kb-bench: Full Benchmark Run ==="
echo "Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo ""

# 1. Download and verify corpus
echo "--- Step 1: Downloading corpus ---"
python -m corpus.download

# 2. Run benchmark harness
echo "--- Step 2: Running benchmarks ---"
python -m benchmarks.harness

# 3. Generate charts and report
echo "--- Step 3: Generating report ---"
python -m scripts.generate_report

echo ""
echo "=== Done. Results in results/latest/ ==="
