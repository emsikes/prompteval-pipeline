import json
import streamlit as st

from prompteval_pipeline import (
    generate_dataset,
    save_dataset,
    load_dataset,
    run_eval,
    compare_prompts
)

st.set_page_config(page_title="prompteval-pipeline", layout="wide")
st.title("prompteval-pipeline")

tab1, tab2, tab3 = st.tabs(["Dataset", "Run Eval", "Compare Prompts"])

with tab1:
    st.subheader("Dataset")

    col1, col2 = st.columns([1, 3])

    with col1:
        count = st.number_input("Cases to generate", min_value=1, max_value=10, value=3)
        if st.button("Generate Dataset"):
            with st.spinner("Generating..."):
                st.session_state.dataset = generate_dataset(count=count)

        uploaded = st.file_uploader("Upload JSON", type="json")
        if uploaded:
            st.session_state.dataset = json.load(uploaded)

    with col2:
        if "dataset" in st.session_state:
            st.dataframe(st.session_state.dataset, use_container_width=True)
            if st.button("Save Dataset"):
                save_dataset(st.session_state.dataset)
                st.success("Saved to dataset.json")

with tab2:
    st.subheader("Run Eval")

    if st.button("Load Dataset from File"):
        st.session_state.dataset = load_dataset()

    if "dataset" not in st.session_state:
        st.info("Generate or load a dataset in the Dataset tab first.")
    else:
        st.dataframe(st.session_state.dataset, use_container_width=True)

        if st.button("Run Eval"):
            with st.spinner("Running eval pipeline..."):
                st.session_state.eval_results = run_eval(st.session_state.dataset)

        if "eval_results" in st.session_state:
            results = st.session_state.eval_results
            st.metric("Average Score", f"{results['average_score']:.2f} / 10")
            st.dataframe(
                [{"task": r["test_case"]["task"],
                  "format": r["test_case"]["format"],
                  "score": r["score"],
                  "reasoning": r["reasoning"]} for r in results["results"]],
                use_container_width=True
            )

with tab3:
    st.subheader("Compare Prompts")

    if "dataset" not in st.session_state:
        st.info("Generate or load a dataset in the Dataset tab first.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            label_a = st.text_input("Variant A label", value="concise")
            template_a = st.text_area(
                "Variant A prompt",
                value="Solve this task:\n{task}\nRespond only with {format}. No explanation.",
                height=150
            )

        with col2:
            label_b = st.text_input("Variant B label", value="detailed")
            template_b = st.text_area(
                "Variant B prompt",
                value="You are an expert. Solve this task:\n{task}\nCriteria: {solution_criteria}\nRespond only with {format}. No explanation.",
                height=150
            )

        st.caption("Available placeholders: {task}, {format}, {solution_criteria}")

        if st.button("Run Comparison"):
            with st.spinner("Running prompt comparison..."):
                variants = {label_a: template_a, label_b: template_b}
                st.session_state.comparison = compare_prompts(st.session_state.dataset, variants)

        if "comparison" in st.session_state:
            comparison = st.session_state.comparison

            st.subheader("Summary")
            st.dataframe(comparison["summary"], use_container_width=True)

            st.subheader("Raw Results")
            for label, results in comparison["raw"].items():
                with st.expander(f"Variant: {label}"):
                    st.dataframe(
                        [{"task": r["test_case"]["task"],
                          "format": r["test_case"]["format"],
                          "score": r["score"],
                          "model_score": r["model_score"],
                          "syntax_score": r["syntax_score"],
                          "reasoning": r["reasoning"]} for r in results],
                        use_container_width=True
                    )