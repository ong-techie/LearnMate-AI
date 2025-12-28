"""Code Companion Agent: Provides code examples for specific concepts."""

from semantic_kernel.functions import KernelArguments
from agent.semantic_agent import SemanticAgent


class CodeCompanion:
    """Agent that generates code snippets and examples."""

    def __init__(self, semantic_agent: SemanticAgent):
        """Initialize the Code Companion.
        
        Args:
            semantic_agent: The SemanticAgent to use for AI operations.
        """
        self.kernel = semantic_agent.get_kernel()
        self._setup_semantic_function()

    def _setup_semantic_function(self):
        """Create the semantic function for generating code examples."""
        prompt = """
You are a helpful code assistant. Provide a clear, simple, and well-commented code example for the following concept.

**Concept:**
{{$concept}}

**Context:**
The user is working on the task: "{{$task_context}}"

**Code Example:**
Provide a language-appropriate, copy-pasteable code block.
```language
...
```
"""
        self.code_example_function = self.kernel.add_function(
            function_name="generate_code_example",
            plugin_name="CodeCompanion",
            prompt=prompt,
        )

    async def get_code_example(self, concept: str, task_context: str) -> str:
        """Get a code example for a given concept.
        
        Args:
            concept: The programming concept or technology.
            task_context: The original task description for context.
            
        Returns:
            A string containing the code example.
        """
        args = KernelArguments(concept=concept, task_context=task_context)
        
        result = await self.kernel.invoke(self.code_example_function, args)
        return str(result)
