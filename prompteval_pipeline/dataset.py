import json

from prompteval_pipeline.client import chat, add_user_message
from prompteval_pipeline.router import select_model, TaskContext
from prompteval_pipeline.graders import strip_fences


def generate_dataset(count=3):
    """Generate an eval dataset of Python, JSON, and Regex tasks."""
    context = TaskContext(task_type="generate")
    model = select_model(context)

    prompt = f"""
Generate an evaluation dataset for a prompt evaluation. The dataset will be used to evaluate prompts
that generate Python, JSON, or Regex to complete technical tasks. Generate an array of JSON objects,
each representing a task that requires Python, JSON, or a Regex to complete.

Example output:
```json
[
    {{
        "task": "Description of task",
        "format": "json" or "python" or "regex",
        "solution_criteria": "Key criteria for evaluating the solution"
    }},
    ...additional
]
```

* Focus on tasks that can be solved by writing a single Python function, a single JSON object, or a regular expression.
* Focus on tasks that do not require writing much code

Please generate {count} objects.
"""
    messages = []
    add_user_message(messages, prompt)

    text = chat(
        messages,
        model=model,
        system="Respond with RAW JSON only.  No Markdown, no code fences, no explanation.",
        max_tokens=5000
    )

    print(repr(text))
    return json.loads(strip_fences(text))

def save_dataset(dataset, path="dataset.json"):
    """Save dataset to a JSON file"""
    with open(path, "w") as f:
        json.dump(dataset, f, indent=2)

def load_dataset(path="dataset.json"):
    """Load dataset from a JSON file"""
    with open(path, "r") as f:
        return json.load(f)
