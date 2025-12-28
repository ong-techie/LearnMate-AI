// Application state context for LearnMate

import React, { createContext, useContext, useReducer, ReactNode } from 'react';
import type { AppState, AppPhase, TaskBreakdown, ResourcesByConept } from '../types';

// Initial state
const initialState: AppState = {
  phase: 'input',
  taskDescription: '',
  taskBreakdown: null,
  knownPrerequisiteIndices: [],
  resources: {},
  isLoading: false,
  error: null,
};

// Action types
type AppAction =
  | { type: 'SET_TASK_DESCRIPTION'; payload: string }
  | { type: 'SET_TASK_BREAKDOWN'; payload: TaskBreakdown }
  | { type: 'SET_KNOWN_PREREQUISITES'; payload: number[] }
  | { type: 'SET_RESOURCES'; payload: ResourcesByConept }
  | { type: 'SET_PHASE'; payload: AppPhase }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'RESET_STATE' };

// Reducer function
function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case 'SET_TASK_DESCRIPTION':
      return { ...state, taskDescription: action.payload };
    case 'SET_TASK_BREAKDOWN':
      return { ...state, taskBreakdown: action.payload, phase: 'analysis' };
    case 'SET_KNOWN_PREREQUISITES':
      return { ...state, knownPrerequisiteIndices: action.payload };
    case 'SET_RESOURCES':
      return { ...state, resources: action.payload, phase: 'resources' };
    case 'SET_PHASE':
      return { ...state, phase: action.payload };
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    case 'RESET_STATE':
      return initialState;
    default:
      return state;
  }
}

// Context
interface AppContextType {
  state: AppState;
  dispatch: React.Dispatch<AppAction>;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

// Provider component
export function AppProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  return (
    <AppContext.Provider value={{ state, dispatch }}>
      {children}
    </AppContext.Provider>
  );
}

// Custom hook to use the context
export function useAppContext() {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
}

export default AppContext;