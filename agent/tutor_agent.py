"""Tutor Agent: Answers questions and helps with debugging."""

from semantic_kernel.functions import KernelArguments
from agent.semantic_agent import SemanticAgent


class TutorAgent:
    """Agent that acts as a tutor, answering questions and explaining errors."""

    def __init__(self, semantic_agent: SemanticAgent):
        """Initialize the Tutor Agent.
        
        Args:
            semantic_agent: The SemanticAgent to use for AI operations.
        """
        self.kernel = semantic_agent.get_kernel()
        self._setup_semantic_functions()

    def _setup_semantic_functions(self):
        """Create semantic functions for tutoring."""
        # Function for general questions
        question_prompt = """
You are a friendly and knowledgeable tutor. A student has a question related to their task.

**Student's Task:**
{{$task_context}}

**Student's Question:**
{{$question}}

**Answer:**
Provide a clear, concise, and helpful answer to the student's question.
"""
        self.answer_question_function = self.kernel.add_function(
            function_name="answer_question",
            plugin_name="TutorAgent",
            prompt=question_prompt,
        )

        # Function for explaining errors
        error_prompt = """
You are a helpful debugging assistant. A student has encountered an error message and needs help understanding it.

**Student's Task:**
{{$task_context}}

**Error Message / Code:**
{{$error_message}}

**Explanation:**
1.  **What the error means:** Briefly explain the error in simple terms.
2.  **Common causes:** List the most likely reasons for this error in the context of the student's task.
3.  **How to fix it:** Suggest specific steps or code corrections to resolve the error.
"""
        self.explain_error_function = self.kernel.add_function(
            function_name="explain_error",
            plugin_name="TutorAgent",
            prompt=error_prompt,
        )

    async def answer_question(self, question: str, task_context: str) -> str:
        """Answer a general question.
        
        Args:
            question: The user's question.
            task_context: The original task description for context.
            
        Returns:
            The answer to the question.
        """
        args = KernelArguments(question=question, task_context=task_context)
        result = await self.kernel.invoke(self.answer_question_function, args)
        return str(result)

    async def explain_error(self, error_message: str, task_context: str) -> str:
        """Explain an error message.
        
        Args:
            error_message: The error message or code snippet from the user.
            task_context: The original task description for context.
            
        Returns:
            An explanation of the error.
        """
        args = KernelArguments(error_message=error_message, task_context=task_context)
        result = await self.kernel.invoke(self.explain_error_function, args)
        return str(result)
