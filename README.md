---
title: prompteval-pipeline
emoji: 🔬
colorFrom: blue
colorTo: purple
sdk: docker
app_file: app.py
pinned: false
---

# prompteval-pipeline

![Python](https://img.shields.io/badge/python-3.12+-blue?style=flat-square)
![LiteLLM](https://img.shields.io/badge/litellm-provider--agnostic-orange?style=flat-square)
![Streamlit](https://img.shields.io/badge/streamlit-UI-red?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)
![Status](https://img.shields.io/badge/status-active-brightgreen?style=flat-square)

A provider-agnostic prompt evaluation pipeline for structured output tasks. Automatically routes models by task type and complexity, grades output via syntax validation and LLM-based evaluation, and supports prompt variant comparison across a shared dataset.

---

## Features

- **Automatic model routing** — Haiku for generation and execution, Sonnet/Opus for grading, selected dynamically by task type and output complexity
- **Dual grading** — syntax validation (pure Python, zero cost) combined with LLM-based evaluation for comprehensive scoring
- **Prompt variant comparison** — run multiple prompt templates against the same dataset and compare average scores side by side
- **Dataset generation** — AI-generated eval datasets with configurable case count, or bring your own JSON
- **Provider-agnostic** — built on LiteLLM; works with Anthropic, OpenAI, Gemini, and Bedrock with no code changes
- **Streamlit UI** — interactive interface for dataset management, eval runs, and prompt comparison

---

## Live Demo

[huggingface.co/spaces/emsikes/prompteval-pipeline](https://huggingface.co/spaces/emsikes/prompteval-pipeline)

Bring your own Anthropic API key to run the pipeline. Enter it in the sidebar when prompted.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| LLM Client | LiteLLM |
| Primary Provider | Anthropic (Claude) |
| UI | Streamlit |
| Package Management | uv |
| Syntax Validation | ast, json, re (stdlib) |

---

## Project Structure

```
prompteval/
├── prompteval_pipeline/
│   ├── __init__.py       # public API
│   ├── client.py         # LiteLLM client, chat(), message helpers
│   ├── dataset.py        # generate_dataset(), save_dataset(), load_dataset()
│   ├── graders.py        # syntax validators, grade_by_model()
│   ├── router.py         # TaskContext, model constants, select_model()
│   └── runner.py         # run_prompt(), run_test_case(), run_eval(), compare_prompts()
├── app.py                # Streamlit UI
├── main.py               # CLI entry point
├── dataset.json          # sample dataset
└── pyproject.toml
```

---

## Installation

```bash
git clone https://github.com/emsikes/prompteval-pipeline
cd prompteval-pipeline
uv sync
```

Add your API key to a `.env` file:

```bash
cp .env.example .env
# add ANTHROPIC_API_KEY to .env
```

---

## Usage

### Streamlit UI

```bash
uv run streamlit run app.py
```

Three tabs:

- **Dataset** — generate an AI-powered dataset, upload your own JSON, or edit cases manually
- **Run Eval** — run the full eval pipeline and view per-case scores and reasoning
- **Compare Prompts** — test two prompt variants against the same dataset and compare results

### CLI

```bash
uv run main.py
```

### Python API

Clone the repo and import directly from the local package:

```python
from prompteval_pipeline import load_dataset, run_eval, compare_prompts

dataset = load_dataset("dataset.json")

# Run eval
results = run_eval(dataset)
print(results["average_score"])

# Compare prompt variants
variants = {
    "concise": "Solve this task:\n{task}\nRespond only with {format}.",
    "detailed": "You are an expert. Solve:\n{task}\nCriteria: {solution_criteria}\nRespond only with {format}.",
}
comparison = compare_prompts(dataset, variants)
print(comparison["summary"])
```

> PyPI publishing planned for v2.

---

## Dataset Format

```json
[
  {
    "task": "Description of the task",
    "format": "json | python | regex",
    "solution_criteria": "Criteria used by the model grader to evaluate the solution"
  }
]
```

---

## Building Effective Datasets

The included `dataset.json` is a generated sample for demonstration. For real prompt
tuning work, hand-craft your dataset to reflect actual production inputs and edge cases.

A good dataset entry is:
- **Task** — a specific, realistic input your prompt will encounter in production
- **Format** — the expected output type your prompt should produce
- **Solution criteria** — the exact conditions a correct answer must satisfy

The AI dataset generator is useful for exploring a new domain quickly. For prompt
tuning decisions that affect shipped code, hand-crafted datasets against your real
inputs will produce more meaningful scores.

---

## Model Routing

| Task | Default Model | Upgrade Condition |
|---|---|---|
| Dataset generation | Haiku | — |
| Prompt execution | Haiku | — |
| Grading | Sonnet | Opus when complexity score == 3 |

Complexity is scored by format type (Python > JSON/Regex), output length, and criteria length.

---

## Scoring

Each test case receives two scores averaged together:

- **Syntax score** (0 or 10) — validates output is parseable Python, JSON, or Regex using stdlib only
- **Model score** (1-10) — LLM evaluation against task description and solution criteria

Final score range: 0-10.

---

## Roadmap

- PyPI package publishing
- Manual model override in UI
- Provider selector (OpenAI, Gemini, Bedrock)
- Domain-specific dataset generation (Kubernetes, healthcare, security)
- Run history and score tracking across sessions

---

## License

MIT
