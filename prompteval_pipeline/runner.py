from statistics import mean

from prompteval_pipeline.client import chat, add_user_message
from prompteval_pipeline.graders import grade_by_model, grade_syntax
from prompteval_pipeline.router import select_model, TaskContext


def run_prompt(test_case, prompt_template=None):
    """Execute a test case task and return the raw output"""
    context = TaskContext(task_type="run", format=test_case["format"])
    model = select_model(context)

    if prompt_template:
        prompt = prompt_template.format(
            task=test_case["task"],
            format=test_case["format"],
            solution_criteria=test_case.get("solution_criteria", "")
        )
    else:
        prompt = f"""
Please solve the following task:

{test_case["task"]}

* Respond only with Python, JSON, or plain Regex
* Do not add any commentary, comments, or explanations
"""
    messages = []
    add_user_message(messages, prompt)

    return chat(
        messages,
        model=model,
        system="Respond with raw code only. No markdown, no code fences, no backticks, no explanation, no comments. Output only the requested Python, JSON, or regex."
    )

   

def run_test_case(test_case):
    """Run a single test case and return scored results"""
    output = run_prompt(test_case)

    model_grade = grade_by_model(test_case, output)
    model_score = model_grade["score"]
    reasoning = model_grade["reasoning"]

    syntax_score = grade_syntax(output, test_case)

    score = (model_score + syntax_score) / 2

    return {
        "output": output,
        "test_case": test_case,
        "score": score,
        "reasoning": reasoning
    }

def run_eval(dataset):
    """Run the full eval pipeline against a dataset and return results."""
    results = []

    for test_case in dataset:
        result = run_test_case(test_case)
        results.append(result)

    average_score = mean([result["score"] for result in results])

    return {
        "results": results,
        "average_score": average_score
    }

def compare_prompts(dataset, prompt_variants: dict) -> dict:
    """Run eval pipeline for each prompt variant and return summary and raw results"""
    summary = []
    raw = {}

    for label, template in prompt_variants.items():
        results = []

        for test_case in dataset:
            output = run_prompt(test_case, prompt_template=template)

            model_grade = grade_by_model(test_case, output)
            syntax_score = grade_syntax(output, test_case)
            model_score = model_grade["score"]
            score = (model_score + syntax_score) / 2

            results.append({
                "output": output,
                "test_case": test_case,
                "score": score,
                "model_score": model_score,
                "syntax_score": syntax_score,
                "reasoning": model_grade["reasoning"]
            })

        raw[label] = results
        summary.append({
            "variant": label,
            "average_score": mean([r["score"] for r in results]),
            "average_model_score": mean([r["model_score"] for r in results]),
            "average_syntax_score": mean([r["syntax_score"] for r in results])
        })

    return {
        "summary": summary,
        "raw": raw
    }