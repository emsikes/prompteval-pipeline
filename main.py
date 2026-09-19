import json
from prompteval_pipeline import(
    load_dataset,
    generate_dataset,
    save_dataset,
    run_eval,
    compare_prompts
)

if __name__ == "__main__":

    # Load or generate dataset
    dataset = load_dataset("dataset.json")

    # Run the full eval pipeline
    print("Running eval pipeline...")
    results = run_eval(dataset)
    print(f"Average score: {results['average_score']:.2f}")

    # Run prompt variant comparison
    print("\nRunning prompt comparison...")
    variants = {
        "concise": "Solve this task:\n{task}\nRespond only with {format}.  No explanation.",
        "detailed": "You are an expert at {task}.  Solve this task:\n{task}\nCriteria: {solution_criteria}\nRespond only with {format}.  No explanation."
    }
    comparison = compare_prompts(dataset, variants)

    print("\nComparison Summary:")
    for row in comparison["summary"]:
        print(f"  {row['variant']}:")
        print(f"    avg score:    {row['average_score']:.2f}")
        print(f"    model score:  {row['average_model_score']:.2f}")
        print(f"    syntax score: {row['average_syntax_score']:.2f}")