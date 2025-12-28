import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import os
from config import load_config
from agent.semantic_agent import SemanticAgent
from agent.task_analyzer import TaskAnalyzer, TaskBreakdown, Prerequisite
from agent.resource_finder import ResourceFinder, LearningResource
from agent.project_planner import ProjectPlanner
from agent.code_companion import CodeCompanion
from agent.tutor_agent import TutorAgent
from agent.output_formatter import OutputFormatter  # Keep for markdown generation


class LearnMateOrchestrator:
    """Orchestrates the multi-agent workflow, returning data for any UI."""

    def __init__(self):
        """Initialize all agents and components."""
        self.config = load_config()
        self.semantic_agent = SemanticAgent(self.config)
        self.task_analyzer = TaskAnalyzer(self.semantic_agent)
        self.resource_finder = ResourceFinder(max_results_per_concept=5)
        self.project_planner = ProjectPlanner(self.semantic_agent)
        self.code_companion = CodeCompanion(self.semantic_agent)
        self.tutor_agent = TutorAgent(self.semantic_agent)
        
        # Store the state
        self.task_breakdown: TaskBreakdown = None
        self.resources_by_concept: Dict[str, List[LearningResource]] = {}

    async def analyze_task(self, task_description: str) -> TaskBreakdown:
        """
        Performs the initial task analysis and returns the breakdown.
        
        Args:
            task_description: The user's task.
            
        Returns:
            A TaskBreakdown object.
        """
        self.task_breakdown = await self.task_analyzer.analyze_task(task_description)
        return self.task_breakdown

    async def find_resources(self, known_prerequisites_indices: List[int] = None) -> Dict[str, List[LearningResource]]:
        """
        Finds learning resources for the analyzed task, skipping known prerequisites.
        
        Args:
            known_prerequisites_indices: A list of indices for prerequisites the user already knows.
            
        Returns:
            A dictionary mapping concepts to a list of LearningResource objects.
        """
        if not self.task_breakdown:
            raise ValueError("Task has not been analyzed yet. Call analyze_task first.")

        selected_prerequisites = list(self.task_breakdown.prerequisites)
        if known_prerequisites_indices:
            selected_prerequisites = [
                p for i, p in enumerate(self.task_breakdown.prerequisites) 
                if i not in known_prerequisites_indices
            ]
        
        self.resources_by_concept = self.resource_finder.find_resources_for_prerequisites(
            selected_prerequisites
        )
        return self.resources_by_concept

    async def generate_project_plan(self) -> str:
        """Generates and returns a project plan."""
        if not self.task_breakdown:
            return "Please perform initial task analysis first."
        plan = await self.project_planner.generate_plan(self.task_breakdown)
        return plan

    async def get_code_example(self, concept: str) -> str:
        """Generates and returns a code example for a given concept."""
        if not self.task_breakdown:
            return "Please perform initial task analysis first."
        example = await self.code_companion.get_code_example(concept, self.task_breakdown.task_description)
        return example

    async def get_tutor_response(self, query: str) -> str:
        """Gets a response from the tutor agent for a question or error."""
        if not self.task_breakdown:
            return "Please perform initial task analysis first."
        if "error" in query.lower() or "traceback" in query.lower():
            response = await self.tutor_agent.explain_error(query, self.task_breakdown.task_description)
        else:
            response = await self.tutor_agent.answer_question(query, self.task_breakdown.task_description)
        return response

    def save_results_to_markdown(self, output_path: str = None) -> str:
        """
        Saves the current analysis and resources to a markdown file.
        
        Returns:
            The path where the file was saved.
        """
        if not self.task_breakdown:
            raise ValueError("No analysis results to save.")

        # Use the console formatter specifically for markdown generation
        markdown_formatter = OutputFormatter()
        markdown_content = markdown_formatter.generate_markdown(self.task_breakdown, self.resources_by_concept)
        
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_task = "".join(c for c in self.task_breakdown.task_description[:30] if c.isalnum() or c in " _-").strip().replace(" ", "_")
            resources_dir = Path("resources")
            resources_dir.mkdir(exist_ok=True)
            save_path = resources_dir / f"learning_resources_{safe_task}_{timestamp}.md"
        else:
            save_path = Path(output_path)

        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return str(save_path)

# Helper function for reading task from file
import docx

def read_task_from_file(file_path: str) -> str:
    """Read task description from a file."""
    if not file_path:
        return ""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if file_path.endswith(".docx"):
        doc = docx.Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    elif file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        raise ValueError("Unsupported file type. Please use .txt or .docx")
