from dataclasses import dataclass

# Model constants - update here when changing or adding providers
HAIKU  = "anthropic/claude-haiku-4-5-20251001"
SONNET = "anthropic/claude-sonnet-4-6"
OPUS   = "anthropic/claude-opus-4-6"

@dataclass
class TaskContext:
    """Holds task metadata used to determine model routing"""
    task_type: str          # e.g 'generate', 'run', 'grade'
    format: str = ""        # e.g. 'json', 'python', 'regex'
    output_length: int = 0
    criteria_length: int = 0

def route_by_task(task_type: str) -> str:
    """Select model based on task type along - no LLM call needed here"""
    routes = {
        "generate": HAIKU,
        "run": HAIKU,
        "grade": SONNET
    }
    return routes.get(task_type, SONNET)

def score_complexity(context: TaskContext) -> int:
    """Score task complexity 1-3 to inform model upgrade decisions based on context length"""
    score = 1

    if context.format == "python":
        score += 1

    if context.output_length > 500:
        score += 1

    if context.criteria_length > 200:
        score += 1

    return min(score, 3)

def select_model(context: TaskContext) -> str:
    """Select the appropriate model based on task type and complexity."""
    model = route_by_task(context.task_type)

    if context.task_type == "grade":
        complexity = score_complexity(context)
        if complexity == 3:
            model = OPUS

    return model