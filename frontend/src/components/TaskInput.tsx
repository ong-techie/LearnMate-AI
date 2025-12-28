// Task input component with file upload support

import React, { useState, useRef } from 'react';
import { Upload, FileText, Loader2 } from 'lucide-react';
import { useAppContext } from '../context/AppContext';
import learnMateApi from '../services/api';

export function TaskInput() {
  const { state, dispatch } = useAppContext();
  const [inputValue, setInputValue] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleAnalyze = async () => {
    if (!inputValue.trim()) return;

    dispatch({ type: 'SET_LOADING', payload: true });
    dispatch({ type: 'SET_ERROR', payload: null });

    try {
      const breakdown = await learnMateApi.analyzeTask(inputValue);
      dispatch({ type: 'SET_TASK_DESCRIPTION', payload: inputValue });
      dispatch({ type: 'SET_TASK_BREAKDOWN', payload: breakdown });
    } catch (error: any) {
      dispatch({
        type: 'SET_ERROR',
        payload: error.response?.data?.detail || 'Failed to analyze task. Please try again.',
      });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    dispatch({ type: 'SET_LOADING', payload: true });
    dispatch({ type: 'SET_ERROR', payload: null });

    try {
      const { content } = await learnMateApi.uploadFile(file);
      setInputValue(content);
    } catch (error: any) {
      dispatch({
        type: 'SET_ERROR',
        payload: error.response?.data?.detail || 'Failed to upload file. Please try again.',
      });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      handleAnalyze();
    }
  };

  return (
    <div className="task-input-container">
      <h2>Enter Your Task</h2>
      <p className="subtitle">
        Describe the task or assignment you want to learn about. You can also upload a .txt or .docx file.
      </p>

      <div className="input-group">
        <textarea
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Example: Build a web scraper using Python that extracts product data from e-commerce websites and stores it in a database."
          rows={6}
          disabled={state.isLoading}
        />

        <div className="input-actions">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            accept=".txt,.docx"
            style={{ display: 'none' }}
          />
          <button
            className="btn-secondary"
            onClick={() => fileInputRef.current?.click()}
            disabled={state.isLoading}
          >
            <Upload size={18} />
            Upload File
          </button>

          <button
            className="btn-primary"
            onClick={handleAnalyze}
            disabled={state.isLoading || !inputValue.trim()}
          >
            {state.isLoading ? (
              <>
                <Loader2 size={18} className="spinner" />
                Analyzing...
              </>
            ) : (
              <>
                <FileText size={18} />
                Analyze Task
              </>
            )}
          </button>
        </div>

        <p className="hint">Press Ctrl+Enter to analyze</p>
      </div>

      {state.error && (
        <div className="error-message">
          {state.error}
        </div>
      )}
    </div>
  );
}

export default TaskInput;
