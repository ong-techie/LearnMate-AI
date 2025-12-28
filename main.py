#!/usr/bin/env python3
"""LearnMate - A multi-agent AI-powered learning assistant (CLI Entry Point)."""

import argparse
import asyncio
import os
from rich.prompt import Prompt

from orchestrator import LearnMateOrchestrator, read_task_from_file
from agent.output_formatter import OutputFormatter


async def main_cli():
    """Main entry point for the command-line interface."""
    parser = argparse.ArgumentParser(
        description="LearnMate - A multi-agent AI-powered learning assistant.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py "Build a REST API with JWT authentication"
  python main.py --file my_task.txt
  python main.py "Create a machine learning model" --save
  python main.py "Build a web scraper" --save --output my_resources.md
        """
    )
    
    parser.add_argument(
        "task",
        nargs="?",
        default=None,
        help="Task or assignment description (optional if --file is used)"
    )
    
    parser.add_argument(
        "-f", "--file",
        type=str,
        help="Path to a .txt or .docx file containing the task description"
    )
    
    parser.add_argument(
        "-s", "--save",
        action="store_true",
        help="Save initial analysis to a markdown file without prompting"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Custom output path for markdown file"
    )
    
    args = parser.parse_args()
    
    task_description = ""
    if args.file:
        try:
            task_description = read_task_from_file(args.file)
        except (FileNotFoundError, ValueError) as e:
            print(f"Error: {e}")
            return 1
    elif args.task:
        task_description = args.task
    else:
        parser.error("You must provide a task description or a file path.")

    formatter = OutputFormatter()
    orchestrator = LearnMateOrchestrator(formatter)

    try:
        # Initial analysis and resource finding
        breakdown, _ = await orchestrator.initial_analysis(task_description)

        # Ask user to select prerequisites they already know (CLI specific)
        known_indices = []
        if breakdown.prerequisites:
            formatter.console.print()
            try:
                user_input = Prompt.ask(
                    "[bold]Enter the numbers of prerequisites you already know (e.g., '1 3 4'), or press Enter to search for all[/bold]"
                ).strip()
                
                if user_input:
                    known_indices = [int(i) - 1 for i in user_input.split()]
                    # Re-run analysis with known prerequisites
                    breakdown, _ = await orchestrator.initial_analysis(task_description, known_indices)

            except (ValueError, IndexError):
                formatter.console.print("\n[yellow]Invalid input. Searching for all prerequisites.[/yellow]")

        # Save initial analysis if requested
        if args.save or Prompt.ask("💾 Save initial analysis to a markdown file? (y/n)").lower() == 'y':
            orchestrator.save_results_to_markdown(args.output)

        # Interactive Multi-Agent Loop
        while True:
            formatter.console.print("\n[bold magenta]What would you like to do next?[/bold magenta]")
            choice = Prompt.ask(
                "  [P]lan the project\n"
                "  [C]ode an example\n"
                "  [A]sk a question / explain an error\n"
                "  [Q]uit\n"
                "Choose an option"
            ).lower()

            if choice == 'p':
                await orchestrator.generate_project_plan()
            
            elif choice == 'c':
                concept = Prompt.ask("Enter the concept for the code example (e.g., React, Flask, JWT)")
                await orchestrator.get_code_example(concept)

            elif choice == 'a':
                query = Prompt.ask("What is your question or error message?")
                await orchestrator.get_tutor_response(query)

            elif choice == 'q':
                formatter.console.print("\n[bold yellow]Happy learning![/bold yellow]")
                break
            
            else:
                formatter.show_error("Invalid choice. Please try again.")

    except ValueError as e:
        formatter.show_error(str(e))
        formatter.console.print("\n[dim]Please check your .env file and ensure API keys are set correctly.[/dim]")
        return 1
    except (EOFError, KeyboardInterrupt):
        formatter.console.print("\n\n[bold yellow]Operation cancelled by user. Exiting.[/bold yellow]")
        return 1
    except Exception as e:
        formatter.show_error(f"An unexpected error occurred: {str(e)}")
        import traceback
        formatter.console.print(f"[dim]{traceback.format_exc()}[/dim]")
        return 1
    
    return 0


if __name__ == "__main__":
    asyncio.run(main_cli())