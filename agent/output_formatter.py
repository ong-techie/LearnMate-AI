"""Output formatter for console and markdown generation."""

from typing import Dict, List
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from agent.task_analyzer import TaskBreakdown, Prerequisite
from agent.resource_finder import LearningResource


class OutputFormatter:
    """Handles formatting and output of learning resources."""
    
    def __init__(self):
        """Initialize output formatter with Rich console."""
        self.console = Console()
    
    def display_task_analysis(self, breakdown: TaskBreakdown):
        """Display task breakdown in console.
        
        Args:
            breakdown: TaskBreakdown object to display
        """
        self.console.print("\n")
        self.console.print(Panel.fit(
            f"[bold cyan]Task:[/bold cyan] {breakdown.task_description}",
            title="📋 Task Analysis",
            border_style="cyan"
        ))
        
        # Display complexity
        complexity_colors = {
            "beginner": "green",
            "intermediate": "yellow",
            "advanced": "red"
        }
        color = complexity_colors.get(breakdown.estimated_complexity.lower(), "yellow")
        self.console.print(f"\n[bold]Estimated Complexity:[/bold] [{color}]{breakdown.estimated_complexity.title()}[/{color}]")
        
        # Display prerequisites in a single numbered list
        prereq_list = breakdown.prerequisites
        if prereq_list:
            table = Table(title="[bold cyan]Prerequisites Identified[/bold cyan]", show_header=True, header_style="bold magenta", border_style="cyan")
            table.add_column("#", style="dim", width=4)
            table.add_column("Prerequisite", style="cyan")
            table.add_column("Category", style="yellow")
            table.add_column("Priority", style="green")

            for i, prereq in enumerate(prereq_list, 1):
                priority_map = {0: "High", 1: "Medium", 2: "Low"}
                priority_text = priority_map.get(prereq.priority, "N/A")
                table.add_row(str(i), prereq.name, prereq.category.title(), priority_text)
            
            self.console.print(table)
        
        # Display suggested learning order
        if breakdown.suggested_learning_order:
            self.console.print("\n[bold cyan]Suggested Learning Order:[/bold cyan]")
            for i, item in enumerate(breakdown.suggested_learning_order[:10], 1):
                self.console.print(f"  {i}. {item}")
            self.console.print()
    
    def display_resources(self, resources_by_concept: Dict[str, List[LearningResource]]):
        """Display learning resources in console.
        
        Args:
            resources_by_concept: Dictionary mapping concept names to resources
        """
        self.console.print("\n")
        self.console.print(Panel.fit(
            "[bold green]Learning Resources Found[/bold green]",
            title="🌐 Search Results",
            border_style="green"
        ))
        self.console.print()
        
        # Check if any resources were found
        total_resources = sum(len(resources) for resources in resources_by_concept.values())
        if total_resources == 0:
            self.console.print("[yellow]⚠️  No learning resources found. This might be due to:")
            self.console.print("   • Network connectivity issues")
            self.console.print("   • Search rate limiting")
            self.console.print("   • Very specific or niche topics")
            self.console.print("\n[dim]Try running the search again or with a different task description.[/dim]\n")
            return
        
        for concept_name, resources in resources_by_concept.items():
            if not resources:
                continue
            
            # Create a table for each concept
            table = Table(
                title=f"[bold cyan]{concept_name}[/bold cyan]",
                show_header=True,
                header_style="bold magenta",
                border_style="cyan"
            )
            table.add_column("Title", style="cyan", no_wrap=False)
            table.add_column("URL", style="blue", no_wrap=False)
            
            for resource in resources:
                # Truncate title if too long
                title = resource.title[:60] + "..." if len(resource.title) > 60 else resource.title
                table.add_row(title, resource.url)
            
            self.console.print(table)
            self.console.print()
    
    def display_plan(self, plan_content: str):
        """Display a project plan in the console.
        
        Args:
            plan_content: The project plan as a string.
        """
        self.console.print("\n")
        self.console.print(Panel.fit(
            Markdown(plan_content, style="magenta"),
            title="📝 Project Plan",
            border_style="magenta"
        ))

    def display_code_example(self, code_example: str):
        """Display a code example in the console.
        
        Args:
            code_example: The code example as a string.
        """
        self.console.print("\n")
        self.console.print(Panel.fit(
            Markdown(code_example, style="green"),
            title="💻 Code Example",
            border_style="green"
        ))

    def display_tutor_response(self, response: str):
        """Display a tutor's response in the console.
        
        Args:
            response: The tutor's response as a string.
        """
        self.console.print("\n")
        self.console.print(Panel.fit(
            Markdown(response, style="yellow"),
            title="🧠 Tutor Response",
            border_style="yellow"
        ))

    def generate_markdown(self, breakdown: TaskBreakdown, 
                         resources_by_concept: Dict[str, List[LearningResource]]) -> str:
        """Generate markdown output.
        
        Args:
            breakdown: TaskBreakdown object
            resources_by_concept: Dictionary mapping concept names to resources
            
        Returns:
            Markdown formatted string
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        md = f"""# Learning Resources for: {breakdown.task_description}

**Generated:** {timestamp}  
**Estimated Complexity:** {breakdown.estimated_complexity.title()}

## Task Description

{breakdown.task_description}

## Prerequisites

"""
        
        # Group prerequisites by category
        by_category = {}
        for prereq in breakdown.prerequisites:
            category = prereq.category.title()
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(prereq)
        
        for category, prereqs in by_category.items():
            md += f"### {category}\n\n"
            for prereq in prereqs:
                priority_badge = "🔴 High" if prereq.priority == 0 else "🟡 Medium" if prereq.priority == 1 else "🟢 Low"
                md += f"- **{prereq.name}** ({priority_badge})\n"
                if prereq.description:
                    md += f"  - {prereq.description}\n"
            md += "\n"
        
        # Suggested learning order
        if breakdown.suggested_learning_order:
            md += "## Suggested Learning Order\n\n"
            for i, item in enumerate(breakdown.suggested_learning_order, 1):
                md += f"{i}. {item}\n"
            md += "\n"
        
        # Learning resources
        md += "## Learning Resources\n\n"
        
        for concept_name, resources in resources_by_concept.items():
            if not resources:
                continue
            
            md += f"### {concept_name}\n\n"
            for i, resource in enumerate(resources, 1):
                md += f"{i}. [{resource.title}]({resource.url})\n"
                if resource.description:
                    md += f"   - {resource.description}\n"
            md += "\n"
        
        md += "---\n\n*Generated by LearnMate AI Agent*\n"
        
        return md
    
    def save_markdown(self, markdown_content: str, output_path: str):
        """Save markdown content to file.
        
        Args:
            markdown_content: Markdown string to save
            output_path: Path to save the file
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            self.console.print(f"\n[bold green]✓[/bold green] Results saved to: [cyan]{output_path}[/cyan]")
        except Exception as e:
            self.console.print(f"\n[bold red]✗[/bold red] Error saving file: {e}")
    
    def show_progress(self, message: str):
        """Display a progress message.
        
        Args:
            message: Progress message to display
        """
        self.console.print(f"[cyan]{message}[/cyan]")
    
    def show_error(self, message: str):
        """Display an error message.
        
        Args:
            message: Error message to display
        """
        self.console.print(f"[bold red]Error:[/bold red] {message}")

