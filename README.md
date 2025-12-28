# LearnMate - AI Learning Resource Finder

Learning complex topics and tackling new projects can be daunting. Learners often face challenges in breaking down tasks, finding relevant resources, and getting timely, contextual help. LearnMate, now a multi-agent AI assistant, addresses this by intelligently analyzing tasks, discovering essential learning resources, and providing specialized support through its **Project Planner** for structured execution, **Code Companion** for practical examples, and **Tutor Agent** for interactive guidance and debugging assistance.

LearnMate is an AI-powered terminal agent that helps you find learning resources for any assignment or task. It analyzes your task, breaks it down into prerequisite concepts and technologies, and searches the web for relevant tutorials, documentation, and courses.

## Features

- 🤖 **AI-Powered Analysis**: Uses Semantic Kernel with OpenAI to intelligently break down tasks into prerequisites
- 🔍 **Smart Resource Discovery**: Searches DuckDuckGo for tutorials, documentation, and courses
- 📋 **Structured Output**: Beautiful terminal output with Rich formatting
- 💾 **Markdown Export**: Save results to markdown files for future reference
- 💻 **Terminal-Based**: Fully functional in the terminal

## Installation

### Prerequisites

- Python 3.8 or higher
- OpenAI API key

### Setup

1. **Clone or download this repository**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   
   Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your OpenAI API key:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Usage

Provide the task directly as a command-line argument:

```bash
python main.py "Build a REST API with JWT authentication in Node.js"
```

### Save Results

Save results to a markdown file:

```bash
python main.py "Create a machine learning model" --save
```

Or specify a custom output path:

```bash
python main.py "Build a web scraper" --save --output my_resources.md
```

### Command-Line Options

```
usage: main.py [-h] [-s] [-o OUTPUT] task

LearnMate - Find learning resources for your assignments and tasks

positional arguments:
  task                  Task or assignment description

options:
  -h, --help            show this help message and exit
  -s, --save            Save results to markdown file
  -o OUTPUT, --output OUTPUT
                        Custom output path for markdown file
```

## Examples

### Example 1: Web Development Task

```bash
python main.py "Build a full-stack web application with React and Django"
```

**Output:**
- Analyzes the task
- Identifies prerequisites: React, Django, REST APIs, database design, etc.
- Searches for learning resources for each prerequisite
- Displays formatted results in the terminal

### Example 2: Data Science Task

```bash
python main.py "Create a machine learning model for image classification using TensorFlow" --save
```

This will:
- Break down the task into ML concepts, TensorFlow, image processing, etc.
- Find resources for each concept
- Save results to `resources/learning_resources_*.md`

## AI Provider

LearnMate uses OpenAI's GPT models via Semantic Kernel for task analysis and prerequisite identification.

## Project Structure

```
LearnMate/
├── .env.example          # Template for API keys
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── main.py              # CLI entry point
├── config.py            # Configuration management
├── agent/
│   ├── __init__.py
│   ├── semantic_agent.py    # Semantic Kernel setup
│   ├── task_analyzer.py     # Task breakdown logic
│   ├── resource_finder.py   # DuckDuckGo search
│   └── output_formatter.py  # Console & markdown output
└── resources/           # Output directory for saved files
```

## How It Works

1. **Task Analysis**: The agent uses Semantic Kernel to analyze your task and identify prerequisite concepts, technologies, skills, and tools.

2. **Prerequisite Extraction**: The AI breaks down the task into:
   - Core concepts needed
   - Technologies/frameworks required
   - Skills and knowledge prerequisites
   - Suggested learning order

3. **Resource Discovery**: For each prerequisite, the agent searches DuckDuckGo for:
   - Tutorials
   - Documentation
   - Courses
   - Learning guides

4. **Output**: Results are displayed in a beautifully formatted terminal output and can be saved as markdown files.

## Troubleshooting

### API Key Errors

If you see an error about missing API keys:
- Ensure your `.env` file exists and contains your OpenAI API key
- Verify your API key is valid and has sufficient credits

### Search Errors

If DuckDuckGo search fails:
- Check your internet connection
- The agent will continue with other searches if one fails
- Some results may be filtered out if they're not educational

### Import Errors

If you encounter import errors:
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check that you're using Python 3.8 or higher

## Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

## License

This project is open source and available for educational purposes.

## Acknowledgments

- Built with [Microsoft Semantic Kernel](https://github.com/microsoft/semantic-kernel)
- Uses [DuckDuckGo Search](https://github.com/deedy5/duckduckgo_search)
- Terminal formatting powered by [Rich](https://github.com/Textualize/rich)

