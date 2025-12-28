"""Task analyzer that breaks down assignments into prerequisite concepts."""

from typing import List, Dict, Any
from dataclasses import dataclass, field
import re
import json
from semantic_kernel import Kernel
from agent.semantic_agent import SemanticAgent


@dataclass
class Prerequisite:
    """Represents a prerequisite concept or technology."""
    name: str
    category: str  # e.g., "concept", "technology", "skill", "tool"
    description: str
    priority: int = 0  # 0 = highest priority, higher numbers = lower priority


@dataclass
class TaskBreakdown:
    """Structured breakdown of a task with prerequisites."""
    task_description: str
    prerequisites: List[Prerequisite] = field(default_factory=list)
    suggested_learning_order: List[str] = field(default_factory=list)
    estimated_complexity: str = "medium"


class TaskAnalyzer:
    """Analyzes tasks and breaks them down into prerequisite learning resources."""
    
    def __init__(self, semantic_agent: SemanticAgent):
        """Initialize task analyzer with Semantic Kernel agent.
        
        Args:
            semantic_agent: Configured SemanticAgent instance
        """
        self.kernel = semantic_agent.get_kernel()
        self._setup_semantic_functions()
    
    def _setup_semantic_functions(self):
        """Create semantic functions for task analysis."""
        # Store the prompt template for later use
        self.task_decomposition_prompt = """
You are an expert learning advisor. Analyze the following task/assignment and identify the ESSENTIAL prerequisite concepts and technologies needed to complete it. Keep it concise - focus on the most important prerequisites only.

Task: {{$task}}

Provide a brief breakdown in the following JSON format (limit to 8-12 most essential prerequisites):
{
  "prerequisites": [
    {
      "name": "concept/technology name",
      "category": "concept|technology|skill|tool",
      "description": "brief description of why this is needed",
      "priority": 0
    }
  ],
  "suggested_learning_order": ["prerequisite1", "prerequisite2", ...],
  "estimated_complexity": "beginner|intermediate|advanced"
}

Priorities: 0 = must learn first, 1 = should learn early, 2 = can learn later
Categories: 
- "concept": fundamental concepts/theories
- "technology": specific technologies/frameworks/libraries
- "skill": practical skills/techniques
- "tool": development tools/platforms

IMPORTANT: 
- Focus on HIGH-LEVEL prerequisites only (e.g., "React" not "React hooks, React components, React state management" separately)
- Group related concepts together
- Limit to 8-12 most essential prerequisites maximum
- Prioritize technologies and core concepts over detailed sub-skills
"""
    
    async def analyze_task(self, task_description: str) -> TaskBreakdown:
        """Analyze a task and return structured breakdown.
        
        Args:
            task_description: The task or assignment to analyze
            
        Returns:
            TaskBreakdown object with prerequisites and learning order
        """
        # Format the prompt with the task
        prompt = self.task_decomposition_prompt.replace("{{$task}}", task_description)
        
        # Invoke semantic function using the kernel's invoke method
        try:
            # Use ChatHistory for direct service invocation
            from semantic_kernel.contents import ChatHistory
            from semantic_kernel.contents.chat_message_content import ChatMessageContent
            
            chat_history = ChatHistory()
            chat_history.add_user_message(prompt)
            
            # Get the chat completion service
            service = self.kernel.get_service(type=None)
            if not service:
                # Try to get service by ID
                try:
                    service = self.kernel.get_service("openai_chat")
                except:
                    raise ValueError("No AI service available")
            
            # Get execution settings for the service
            # Try different approaches to get proper settings
            execution_settings = None
            try:
                # Try to get default settings from the service type
                from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings
                execution_settings = OpenAIChatPromptExecutionSettings()
            except:
                try:
                    # Alternative: get settings class from service
                    settings_class = service.get_prompt_execution_settings_class()
                    if settings_class:
                        execution_settings = settings_class()
                except:
                    # If all else fails, pass None and let service use defaults
                    pass
            
            # Get chat message contents
            response = await service.get_chat_message_contents(
                chat_history=chat_history,
                settings=execution_settings
            )
            
            if response and len(response) > 0:
                result_text = response[0].content if hasattr(response[0], 'content') else str(response[0])
            else:
                raise ValueError("Empty response from AI service")
            
            # Parse the result
            breakdown = self._parse_analysis_result(task_description, result_text)
            return breakdown
            
        except Exception as e:
            # Fallback: create a basic breakdown if parsing fails
            import traceback
            print(f"Warning: Task analysis failed, using fallback: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return self._create_fallback_breakdown(task_description, str(e))
    
    def _parse_analysis_result(self, task_description: str, result_text: str) -> TaskBreakdown:
        """Parse the AI response into structured TaskBreakdown.
        
        Args:
            task_description: Original task description
            result_text: Raw AI response text
            
        Returns:
            Parsed TaskBreakdown object
        """
        import json
        import re
        
        # Try to extract JSON from the response
        json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group())
                
                prerequisites = []
                for prereq_data in data.get("prerequisites", []):
                    prereq = Prerequisite(
                        name=prereq_data.get("name", ""),
                        category=prereq_data.get("category", "concept"),
                        description=prereq_data.get("description", ""),
                        priority=prereq_data.get("priority", 0)
                    )
                    prerequisites.append(prereq)
                
                # Sort by priority
                prerequisites.sort(key=lambda x: x.priority)
                
                return TaskBreakdown(
                    task_description=task_description,
                    prerequisites=prerequisites,
                    suggested_learning_order=data.get("suggested_learning_order", []),
                    estimated_complexity=data.get("estimated_complexity", "medium")
                )
            except json.JSONDecodeError:
                pass
        
        # If JSON parsing fails, try to extract prerequisites from text
        return self._extract_prerequisites_from_text(task_description, result_text)
    
    def _extract_prerequisites_from_text(self, task_description: str, text: str) -> TaskBreakdown:
        """Extract prerequisites from unstructured text response.
        
        Args:
            task_description: Original task description
            text: AI response text
            
        Returns:
            TaskBreakdown with extracted prerequisites
        """
        prerequisites = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 3:
                continue
            
            # Look for numbered or bulleted items
            if line[0].isdigit() or line.startswith('-') or line.startswith('*'):
                # Extract the prerequisite name (first part before colon or comma)
                name = line.split(':')[0].split(',')[0].strip()
                name = re.sub(r'^[\d\-\*\.\s]+', '', name)  # Remove numbering
                
                if name and len(name) > 2:
                    prereq = Prerequisite(
                        name=name,
                        category="concept",
                        description=line,
                        priority=len(prerequisites)
                    )
                    prerequisites.append(prereq)
        
        return TaskBreakdown(
            task_description=task_description,
            prerequisites=prerequisites[:12],  # Limit to 12 prerequisites
            suggested_learning_order=[p.name for p in prerequisites[:10]],
            estimated_complexity="medium"
        )
    
    def _create_fallback_breakdown(self, task_description: str, error: str) -> TaskBreakdown:
        """Create a basic breakdown when analysis fails.
        
        Args:
            task_description: Original task description
            error: Error message for debugging
            
        Returns:
            Basic TaskBreakdown with extracted prerequisites
        """
        # Extract technologies and concepts from task description
        prerequisites = []
        
        # Common technology keywords
        tech_keywords = {
            "react": "React",
            "django": "Django",
            "flask": "Flask",
            "node": "Node.js",
            "express": "Express.js",
            "angular": "Angular",
            "vue": "Vue.js",
            "python": "Python",
            "javascript": "JavaScript",
            "typescript": "TypeScript",
            "java": "Java",
            "spring": "Spring Framework",
            "sql": "SQL",
            "mongodb": "MongoDB",
            "postgresql": "PostgreSQL",
            "mysql": "MySQL",
            "redis": "Redis",
            "docker": "Docker",
            "kubernetes": "Kubernetes",
            "aws": "AWS",
            "azure": "Azure",
            "gcp": "Google Cloud Platform",
            "rest": "REST API",
            "graphql": "GraphQL",
            "jwt": "JWT Authentication",
            "oauth": "OAuth",
            "html": "HTML",
            "css": "CSS",
            "bootstrap": "Bootstrap",
            "tailwind": "Tailwind CSS",
            "tensorflow": "TensorFlow",
            "pytorch": "PyTorch",
            "machine learning": "Machine Learning",
            "deep learning": "Deep Learning",
            "neural network": "Neural Networks",
            "full-stack": "Full-Stack Development",
            "frontend": "Frontend Development",
            "backend": "Backend Development",
            "web application": "Web Development",
            "mobile app": "Mobile Development",
            "ios": "iOS Development",
            "android": "Android Development"
        }
        
        task_lower = task_description.lower()
        found_techs = set()
        
        # Extract technologies mentioned (limit to most important ones)
        priority_order = [
            # Frontend frameworks
            "react", "angular", "vue",
            # Backend frameworks
            "django", "flask", "express", "spring",
            # Languages
            "python", "javascript", "typescript", "java",
            # Databases
            "postgresql", "mysql", "mongodb", "sql",
            # Other important tech
            "node", "docker", "aws", "rest", "graphql"
        ]
        
        # First pass: extract high-priority technologies
        for keyword in priority_order:
            if keyword in task_lower:
                tech_name = tech_keywords.get(keyword)
                if tech_name and tech_name not in found_techs and len(prerequisites) < 10:
                    prerequisites.append(Prerequisite(
                        name=tech_name,
                        category="technology",
                        description=f"Learn {tech_name} to complete this task",
                        priority=len(prerequisites)
                    ))
                    found_techs.add(tech_name)
        
        # Second pass: extract other technologies if we have less than 8
        if len(prerequisites) < 8:
            for keyword, tech_name in tech_keywords.items():
                if keyword not in priority_order and keyword in task_lower and tech_name not in found_techs:
                    if len(prerequisites) >= 10:
                        break
                    prerequisites.append(Prerequisite(
                        name=tech_name,
                        category="technology",
                        description=f"Learn {tech_name} to complete this task",
                        priority=len(prerequisites)
                    ))
                    found_techs.add(tech_name)
        
        # Add general concepts if no specific tech found (limit to 2-3)
        if not prerequisites:
            added = 0
            if "web" in task_lower or "application" in task_lower:
                prerequisites.append(Prerequisite(
                    name="Web Development Fundamentals",
                    category="concept",
                    description="Learn web development basics",
                    priority=0
                ))
                added += 1
            if "api" in task_lower and added < 3:
                prerequisites.append(Prerequisite(
                    name="API Development",
                    category="concept",
                    description="Learn how to build and consume APIs",
                    priority=added
                ))
                added += 1
            if ("database" in task_lower or "data" in task_lower) and added < 3:
                prerequisites.append(Prerequisite(
                    name="Database Fundamentals",
                    category="concept",
                    description="Learn database concepts and SQL",
                    priority=added
                ))
        
        # If still no prerequisites, add a generic one
        if not prerequisites:
            prerequisites.append(Prerequisite(
                name="Fundamentals related to the task",
                category="concept",
                description=f"Learn the fundamentals needed for: {task_description}",
                priority=0
            ))
        
        # Limit to 10 prerequisites maximum
        prerequisites = prerequisites[:10]
        
        return TaskBreakdown(
            task_description=task_description,
            prerequisites=prerequisites,
            suggested_learning_order=[p.name for p in prerequisites[:8]],
            estimated_complexity="medium"
        )

