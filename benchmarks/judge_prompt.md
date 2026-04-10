# LLM-as-Judge Rubric

You are grading an answer from an LLM knowledge base tool. Grade strictly.

## Input

- **Question:** {question}
- **Expected concepts:** {expected_concepts}
- **Source files that should be referenced:** {source_files}
- **Tool's answer:** {tool_answer}

## Rubric

Grade 0-3:

- **3**: Covers ALL expected concepts. Cites or references correct source files. No hallucinations. Accurate and complete.
- **2**: Covers MOST expected concepts (>60%). May miss minor details. Sources mostly correct. Minor inaccuracies acceptable.
- **1**: Partial answer. Misses key expected concepts (<60% coverage) OR cites wrong sources. Significant gaps.
- **0**: Wrong, missing, hallucinated, or does not address the question.

## Output

Respond with ONLY this JSON (no markdown, no explanation outside the JSON):

{"grade": <0-3>, "rationale": "<one sentence explaining the grade>"}
