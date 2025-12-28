"""Project Planner Agent: Creates a step-by-step plan for a given task."""

from semantic_kernel.functions import KernelArguments
from agent.semantic_agent import SemanticAgent
from agent.task_analyzer import TaskBreakdown


class ProjectPlanner:
    """Agent that generates a project plan based on a task breakdown."""

    def __init__(self, semantic_agent: SemanticAgent):
        """Initialize the Project Planner.
        
        Args:
            semantic_agent: The SemanticAgent to use for AI operations.
        """
        self.kernel = semantic_agent.get_kernel()
        self._setup_semantic_function()

    def _setup_semantic_function(self):
        """Create the semantic function for generating a project plan."""
        prompt = """
You are an expert project manager. Based on the following task description and its prerequisites, create a high-level, step-by-step project plan.

The plan should be clear, concise, and actionable for a developer.

**Task Description:**
{{$task_description}}

**Prerequisites:**
{{$prerequisites}}

**Project Plan:**
Provide a numbered list of steps from project setup to completion. Focus on major milestones.
1. ...
2. ...
3. ...
"""
        self.planner_function = self.kernel.add_function(
            function_name="generate_project_plan",
            plugin_name="ProjectPlanner",
            prompt=prompt,
        )

    async def generate_plan(self, task_breakdown: TaskBreakdown) -> str:
        """Generate a project plan.
        
        Args:
            task_breakdown: The TaskBreakdown object from the TaskAnalyzer.
            
        Returns:
            A string containing the generated project plan.
        """
        prerequisites_str = "\n".join(
            f"- {p.name}: {p.description}" for p in task_breakdown.prerequisites
        )
        
        args = KernelArguments(
            task_description=task_breakdown.task_description,
            prerequisites=prerequisites_str,
        )
        
        result = await self.kernel.invoke(self.planner_function, args)
        return str(result)
