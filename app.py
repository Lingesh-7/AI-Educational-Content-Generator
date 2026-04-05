import streamlit as st
from backend import run_pipeline

st.set_page_config(page_title="AI Educational Content Generator")

st.title("AI Educational Content Generator")

grade = st.number_input("Grade", 1, 12, 4)
topic = st.text_input("Topic", "Types of angles")

num_questions = st.slider("Number of Questions", 1, 10, 3)

if st.button("Generate"):

    status = st.empty()
    progress = st.progress(0)

    result = run_pipeline(grade, topic, num_questions)

    if "error" in result:
        st.error(result["error"])
        st.stop()

    for i, step in enumerate(result["steps"]):
        status.info(step)
        progress.progress((i + 1) * 25)

    status.success("Completed")

    st.divider()

    # -------- GENERATOR OUTPUT --------
    st.subheader("Generator Output")
    st.json(result["initial"])

    # -------- REVIEWER --------
    st.subheader("Reviewer Feedback")
    st.json(result["review"])

    # -------- REFINED --------
    if result["review"]["status"] == "fail":
        st.subheader("Refined Output")
        st.json(result["refined"])