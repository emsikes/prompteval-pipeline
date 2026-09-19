import json
import re
import ast

from prompteval_pipeline.client import chat, add_user_message
from prompteval_pipeline.router import select_model, TaskContext


def strip_fences(text):
    """Strip markdown fences from model output."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]
    return text.strip()

def validate_json(text):
    """Return 10 if text is valid JSON, 0 otherwise"""
    try:
        json.loads(strip_fences(text))
        return 10
    except json.JSONDecodeError:
        return 0

def validate_python(text):
    """Return 10 if text is valid Python syntax, 0 otherwise"""
    try:
        ast.parse(strip_fences(text))
        return 10
    except SyntaxError:
        return 0

def validate_regex(text):
    """Return 10 if text is a valid regex, 0 otherwise"""
    try:
        re.compile(strip_fences(text))
        return 10
    except re.error:
        return 0

def grade_syntax(response, test_case):
    """Route to the correct syntax validator based on test case format"""
    format = test_case["format"]
    if format == "json":
        return validate_json(response)
    elif format == "python":
        return validate_python(response)
    else:
        return validate_regex(response)

def grade_by_model(test_case, output):
    """Grade output using a model selected by task type and complexity"""
    context = TaskContext(
        task_type="grade",
        format=test_case["format"],
        output_length=len(output),
        criteria_length=len(test_case.get("solution_criteria", ""))
    )
    model = select_model(context)

    eval_prompt = f"""
You are an expert code reviewer. Your task is to evaluate the following AI-generated solution.

Original Task:
<task>
{test_case["task"]}
</task>

Solution to Evaluate:
<solution>
{output}
</solution>

Criteria you should use to evaluate the solution:
<criteria>
{test_case.get("solution_criteria", "Evaluate correctness and quality.")}
</criteria>

Output Format
Provide your evaluation as a structured JSON object with the following fields, in this specific order:
- "strengths": An array of 1-3 key strengths
- "weaknesses": An array of 1-3 key areas for improvement
- "reasoning": A concise explanation of your overall assessment
- "score": A number between 1-10

Respond with JSON. Keep your responses concise and direct.
{{
    "strengths": string[],
    "weaknesses": string[],
    "reasoning": string,
    "score": number
}}
    """
    messages = []
    add_user_message(messages, eval_prompt)

    eval_text = chat(
        messages,
        model=model,
        system="Respond with raw JSON only.  No Markdown, no code fences, no explanation.",
        max_tokens=2000
    )

    return json.loads(eval_text)