"""
FastAPI backend for LearnMate React frontend.
Wraps the existing orchestrator with REST API endpoints.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import asyncio
import io

from orchestrator import LearnMateOrchestrator
from agent.task_analyzer import TaskBreakdown, Prerequisite
from agent.resource_finder import LearningResource

# Initialize FastAPI app
app = FastAPI(
    title="LearnMate API",
    description="AI-powered learning resource discovery API",
    version="1.0.0"
)

# Add CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store orchestrator instances per session (in production, use proper session management)
orchestrators: Dict[str, LearnMateOrchestrator] = {}

def get_orchestrator(session_id: str = "default") -> LearnMateOrchestrator:
    """Get or create an orchestrator instance for a session."""
    if session_id not in orchestrators:
        orchestrators[session_id] = LearnMateOrchestrator()
    return orchestrators[session_id]


# Request/Response models
class AnalyzeTaskRequest(BaseModel):
    task_description: str
    session_id: str = "default"


class PrerequisiteResponse(BaseModel):
    name: str
    category: str
    description: str
    priority: int


class TaskBreakdownResponse(BaseModel):
    task_description: str
    prerequisites: List[PrerequisiteResponse]
    suggested_learning_order: List[str]
    estimated_complexity: str


class FindResourcesRequest(BaseModel):
    known_prerequisite_indices: List[int]
    session_id: str = "default"


class LearningResourceResponse(BaseModel):
    title: str
    url: str
    description: str
    source: str


class GeneratePlanRequest(BaseModel):
    session_id: str = "default"


class GetCodeExampleRequest(BaseModel):
    concept: str
    session_id: str = "default"


class AskTutorRequest(BaseModel):
    query: str
    session_id: str = "default"


class ExportMarkdownRequest(BaseModel):
    session_id: str = "default"


# API Endpoints
@app.post("/api/analyze-task", response_model=TaskBreakdownResponse)
async def analyze_task(request: AnalyzeTaskRequest):
    """Analyze a task and extract prerequisites."""
    try:
        orchestrator = get_orchestrator(request.session_id)
        breakdown = await orchestrator.analyze_task(request.task_description)

        return TaskBreakdownResponse(
            task_description=breakdown.task_description,
            prerequisites=[
                PrerequisiteResponse(
                    name=p.name,
                    category=p.category,
                    description=p.description,
                    priority=p.priority
                )
                for p in breakdown.prerequisites
            ],
            suggested_learning_order=breakdown.suggested_learning_order,
            estimated_complexity=breakdown.estimated_complexity
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload-file")
async def upload_file(file: UploadFile = File(...)):
    """Upload a .txt or .docx file and extract its content."""
    try:
        content = ""

        if file.filename.endswith('.txt'):
            content = (await file.read()).decode('utf-8')
        elif file.filename.endswith('.docx'):
            from docx import Document
            doc_bytes = await file.read()
            doc = Document(io.BytesIO(doc_bytes))
            content = '\n'.join([para.text for para in doc.paragraphs])
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Please upload .txt or .docx files."
            )

        return {"content": content, "filename": file.filename}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/find-resources")
async def find_resources(request: FindResourcesRequest):
    """Find learning resources for unknown prerequisites."""
    try:
        orchestrator = get_orchestrator(request.session_id)

        if orchestrator.task_breakdown is None:
            raise HTTPException(
                status_code=400,
                detail="No task has been analyzed yet. Please analyze a task first."
            )

        resources = await orchestrator.find_resources(request.known_prerequisite_indices)

        # Convert to response format
        response = {}
        for concept, resource_list in resources.items():
            response[concept] = [
                LearningResourceResponse(
                    title=r.title,
                    url=r.url,
                    description=r.description,
                    source=r.source
                ).model_dump()
                for r in resource_list
            ]

        return {"resources": response}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-plan")
async def generate_plan(request: GeneratePlanRequest):
    """Generate a project plan based on the analyzed task."""
    try:
        orchestrator = get_orchestrator(request.session_id)

        if orchestrator.task_breakdown is None:
            raise HTTPException(
                status_code=400,
                detail="No task has been analyzed yet. Please analyze a task first."
            )

        plan = await orchestrator.generate_project_plan()
        return {"plan": plan}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/get-code-example")
async def get_code_example(request: GetCodeExampleRequest):
    """Get a code example for a specific concept."""
    try:
        orchestrator = get_orchestrator(request.session_id)

        if orchestrator.task_breakdown is None:
            raise HTTPException(
                status_code=400,
                detail="No task has been analyzed yet. Please analyze a task first."
            )

        code = await orchestrator.get_code_example(request.concept)
        return {"code": code}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ask-tutor")
async def ask_tutor(request: AskTutorRequest):
    """Ask the tutor agent a question or explain an error."""
    try:
        orchestrator = get_orchestrator(request.session_id)

        if orchestrator.task_breakdown is None:
            raise HTTPException(
                status_code=400,
                detail="No task has been analyzed yet. Please analyze a task first."
            )

        response = await orchestrator.get_tutor_response(request.query)
        return {"response": response}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/export-markdown")
async def export_markdown(request: ExportMarkdownRequest):
    """Export the analysis results to markdown format."""
    try:
        orchestrator = get_orchestrator(request.session_id)

        if orchestrator.task_breakdown is None:
            raise HTTPException(
                status_code=400,
                detail="No task has been analyzed yet. Please analyze a task first."
            )

        markdown = orchestrator.save_results_to_markdown()
        return {"markdown": markdown, "filename": f"learning_resources.md"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/reset-session")
async def reset_session(session_id: str = "default"):
    """Reset a session by removing its orchestrator."""
    if session_id in orchestrators:
        del orchestrators[session_id]
    return {"message": "Session reset successfully"}


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "LearnMate API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)