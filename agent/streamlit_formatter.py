import streamlit as st
from typing import Dict, List
from agent.task_analyzer import TaskBreakdown
from agent.resource_finder import LearningResource

class StreamlitFormatter:
    """Handles formatting and output for the Streamlit web app."""

    def display_task_analysis(self, breakdown: TaskBreakdown):
        """Display task breakdown in Streamlit."""
        st.subheader("📋 Task Analysis")
        st.markdown(f"**Task:** {breakdown.task_description}")
        
        complexity_color = {
            "beginner": "green",
            "intermediate": "orange",
            "advanced": "red"
        }.get(breakdown.estimated_complexity.lower(), "gray")
        
        st.markdown(f"**Estimated Complexity:** :{complexity_color}[{breakdown.estimated_complexity.title()}]")

        st.subheader("Prerequisites Identified")
        if breakdown.prerequisites:
            prereq_data = []
            for i, prereq in enumerate(breakdown.prerequisites, 1):
                prereq_data.append({
                    "#": i,
                    "Prerequisite": prereq.name,
                    "Category": prereq.category.title(),
                    "Description": prereq.description
                })
            st.table(prereq_data)
        else:
            st.write("No prerequisites were identified.")

        if breakdown.suggested_learning_order:
            st.subheader("Suggested Learning Order")
            for i, item in enumerate(breakdown.suggested_learning_order, 1):
                st.markdown(f"{i}. {item}")

    def display_resources(self, resources_by_concept: Dict[str, List[LearningResource]]):
        """Display learning resources in Streamlit."""
        st.subheader("🌐 Learning Resources Found")
        
        total_resources = sum(len(resources) for resources in resources_by_concept.values())
        if total_resources == 0:
            st.warning("No learning resources found. This might be due to network issues or a very specific topic.")
            return

        for concept_name, resources in resources_by_concept.items():
            if resources:
                with st.expander(f"**{concept_name}** ({len(resources)} resources)"):
                    for resource in resources:
                        st.markdown(f"[{resource.title}]({resource.url})")
                        if resource.description:
                            st.caption(resource.description)

    def display_plan(self, plan_content: str):
        """Display a project plan in Streamlit."""
        st.subheader("📝 Project Plan")
        st.markdown(plan_content)

    def display_code_example(self, code_example: str):
        """Display a code example in Streamlit."""
        st.subheader("💻 Code Example")
        st.markdown(code_example)

    def display_tutor_response(self, response: str):
        """Display a tutor's response in Streamlit."""
        st.subheader("🧠 Tutor Response")
        st.markdown(response)

    def show_progress(self, message: str):
        """Display a progress message in Streamlit."""
        st.info(message)

    def show_error(self, message: str):
        """Display an error message in Streamlit."""
        st.error(message)
