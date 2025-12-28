// API service for communicating with FastAPI backend

import axios from 'axios';
import type {
  TaskBreakdown,
  ResourcesByConept,
  AnalyzeTaskRequest,
  FindResourcesRequest,
  GetCodeExampleRequest,
  AskTutorRequest,
} from '../types';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const learnMateApi = {
  // Analyze a task and extract prerequisites
  analyzeTask: async (taskDescription: string, sessionId: string = 'default'): Promise<TaskBreakdown> => {
    const response = await api.post<TaskBreakdown>('/analyze-task', {
      task_description: taskDescription,
      session_id: sessionId,
    });
    return response.data;
  },

  // Upload a file and extract its content
  uploadFile: async (file: File): Promise<{ content: string; filename: string }> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post<{ content: string; filename: string }>('/upload-file', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Find learning resources for unknown prerequisites
  findResources: async (
    knownPrerequisiteIndices: number[],
    sessionId: string = 'default'
  ): Promise<ResourcesByConept> => {
    const response = await api.post<{ resources: ResourcesByConept }>('/find-resources', {
      known_prerequisite_indices: knownPrerequisiteIndices,
      session_id: sessionId,
    });
    return response.data.resources;
  },

  // Generate a project plan
  generatePlan: async (sessionId: string = 'default'): Promise<string> => {
    const response = await api.post<{ plan: string }>('/generate-plan', {
      session_id: sessionId,
    });
    return response.data.plan;
  },

  // Get a code example for a concept
  getCodeExample: async (concept: string, sessionId: string = 'default'): Promise<string> => {
    const response = await api.post<{ code: string }>('/get-code-example', {
      concept,
      session_id: sessionId,
    });
    return response.data.code;
  },

  // Ask the tutor a question
  askTutor: async (query: string, sessionId: string = 'default'): Promise<string> => {
    const response = await api.post<{ response: string }>('/ask-tutor', {
      query,
      session_id: sessionId,
    });
    return response.data.response;
  },

  // Export results to markdown
  exportMarkdown: async (sessionId: string = 'default'): Promise<{ markdown: string; filename: string }> => {
    const response = await api.post<{ markdown: string; filename: string }>('/export-markdown', {
      session_id: sessionId,
    });
    return response.data;
  },

  // Reset session
  resetSession: async (sessionId: string = 'default'): Promise<void> => {
    await api.delete(`/reset-session?session_id=${sessionId}`);
  },

  // Health check
  healthCheck: async (): Promise<{ status: string; service: string }> => {
    const response = await api.get<{ status: string; service: string }>('/health');
    return response.data;
  },
};

export default learnMateApi;