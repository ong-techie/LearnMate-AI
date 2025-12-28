// TypeScript interfaces for LearnMate

export interface Prerequisite {
  name: string;
  category: 'concept' | 'technology' | 'skill' | 'tool';
  description: string;
  priority: number;
}

export interface TaskBreakdown {
  task_description: string;
  prerequisites: Prerequisite[];
  suggested_learning_order: string[];
  estimated_complexity: 'beginner' | 'intermediate' | 'advanced';
}

export interface LearningResource {
  title: string;
  url: string;
  description: string;
  source: string;
}

export interface ResourcesByConept {
  [concept: string]: LearningResource[];
}

// API Request/Response types
export interface AnalyzeTaskRequest {
  task_description: string;
  session_id?: string;
}

export interface FindResourcesRequest {
  known_prerequisite_indices: number[];
  session_id?: string;
}

export interface GetCodeExampleRequest {
  concept: string;
  session_id?: string;
}

export interface AskTutorRequest {
  query: string;
  session_id?: string;
}

// App state types
export type AppPhase = 'input' | 'analysis' | 'resources';

export interface AppState {
  phase: AppPhase;
  taskDescription: string;
  taskBreakdown: TaskBreakdown | null;
  knownPrerequisiteIndices: number[];
  resources: ResourcesByConept;
  isLoading: boolean;
  error: string | null;
}