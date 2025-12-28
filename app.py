import streamlit as st
import asyncio
import os
from orchestrator import LearnMateOrchestrator, read_task_from_file
from agent.streamlit_formatter import StreamlitFormatter
from agent.task_analyzer import TaskBreakdown

# --- Page Configuration ---
st.set_page_config(
    layout="wide",
    page_title="LearnMate AI Assistant",
    page_icon="🎓"
)

# --- State Management ---
def get_orchestrator():
    """Initializes and retrieves the orchestrator from session state."""
    if 'orchestrator' not in st.session_state:
        st.session_state.orchestrator = LearnMateOrchestrator()
    return st.session_state.orchestrator

def reset_task_state():
    """Resets task-specific keys from the session state for a new analysis."""
    task_keys = ['task_description', 'task_breakdown', 'resources', 'known_prereqs']
    for key in task_keys:
        if key in st.session_state:
            del st.session_state[key]

# --- Main Application UI ---
st.title("🎓 LearnMate - Your AI Learning Assistant")
st.markdown("Enter a task, assignment, or topic. LearnMate will analyze it, find resources, and help you with your project.")

# Initialize orchestrator and formatter
orchestrator = get_orchestrator()
formatter = StreamlitFormatter()

# --- 1. Task Input Section ---
st.header("1. Describe Your Task")
col1, col2 = st.columns([2, 1])
with col1:
    task_description_input = st.text_area(
        "Enter your learning task:",
        height=150,
        key='task_input',
        help="Be as descriptive as possible for the best results."
    )
with col2:
    uploaded_file = st.file_uploader(
        "Or upload a file (.txt, .docx)",
        type=['txt', 'docx']
    )

if st.button("Analyze Task", type="primary"):
    reset_task_state()
    task_description = ""
    if uploaded_file:
        # To read the file, we save it temporarily
        temp_file_path = os.path.join(".", uploaded_file.name)
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        with st.spinner("Reading file..."):
            try:
                task_description = read_task_from_file(temp_file_path)
            except Exception as e:
                st.error(f"Error reading file: {e}")
            finally:
                os.remove(temp_file_path) # Clean up the temp file
    elif task_description_input:
        task_description = task_description_input

    if task_description:
        st.session_state.task_description = task_description
        with st.spinner("🔍 Analyzing task... This may take a moment."):
            breakdown = asyncio.run(orchestrator.analyze_task(task_description))
            st.session_state.task_breakdown = breakdown
    else:
        st.warning("Please enter a task description or upload a file.")

# --- 2. Prerequisite Selection and Resource Finding ---
if 'task_breakdown' in st.session_state:
    st.header("2. Refine and Find Resources")
    
    breakdown: TaskBreakdown = st.session_state.task_breakdown
    formatter.display_task_analysis(breakdown)

    prereq_options = [p.name for p in breakdown.prerequisites]
    st.session_state.known_prereqs = st.multiselect(
        "Select any prerequisites you already know (optional):",
        options=prereq_options,
        help="LearnMate will skip searching for resources on these topics."
    )

    if st.button("Find Learning Resources", type="primary"):
        known_indices = [i for i, p in enumerate(breakdown.prerequisites) if p.name in st.session_state.known_prereqs]
        
        with st.spinner("🌐 Searching for the best learning resources..."):
            resources = asyncio.run(orchestrator.find_resources(known_indices))
            st.session_state.resources = resources

# --- 3. Display Resources and Agent Actions ---
if 'resources' in st.session_state:
    formatter.display_resources(st.session_state.resources)
    
    st.header("3. Explore and Get Help")
    st.sidebar.title("Agent Actions")

    if st.sidebar.button("📝 Plan the Project"):
        with st.spinner("Generating project plan..."):
            plan = asyncio.run(orchestrator.generate_project_plan())
            formatter.display_plan(plan)

    st.sidebar.markdown("---")
    concept_for_code = st.sidebar.text_input("Enter a concept for a code example:")
    if st.sidebar.button("💻 Get Code Example"):
        if concept_for_code:
            with st.spinner(f"Generating code for '{concept_for_code}'..."):
                example = asyncio.run(orchestrator.get_code_example(concept_for_code))
                formatter.display_code_example(example)
        else:
            st.sidebar.warning("Please enter a concept.")

    st.sidebar.markdown("---")
    tutor_query = st.sidebar.text_area("Ask a question or paste an error message:")
    if st.sidebar.button("🧠 Ask Tutor"):
        if tutor_query:
            with st.spinner("Thinking..."):
                response = asyncio.run(orchestrator.get_tutor_response(tutor_query))
                formatter.display_tutor_response(response)
        else:
            st.sidebar.warning("Please enter a question or error message.")