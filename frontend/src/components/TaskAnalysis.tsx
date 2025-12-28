// Task analysis display and prerequisite selector

import React, { useState } from 'react';
import { Search, Loader2, CheckCircle2 } from 'lucide-react';
import { useAppContext } from '../context/AppContext';
import learnMateApi from '../services/api';

export function TaskAnalysis() {
  const { state, dispatch } = useAppContext();
  const [selectedIndices, setSelectedIndices] = useState<number[]>([]);

  if (!state.taskBreakdown) return null;

  const { prerequisites, suggested_learning_order, estimated_complexity } = state.taskBreakdown;

  const handleCheckboxChange = (index: number) => {
    setSelectedIndices((prev) =>
      prev.includes(index) ? prev.filter((i) => i !== index) : [...prev, index]
    );
  };

  const handleFindResources = async () => {
    dispatch({ type: 'SET_LOADING', payload: true });
    dispatch({ type: 'SET_ERROR', payload: null });
    dispatch({ type: 'SET_KNOWN_PREREQUISITES', payload: selectedIndices });

    try {
      const resources = await learnMateApi.findResources(selectedIndices);
      dispatch({ type: 'SET_RESOURCES', payload: resources });
    } catch (error: any) {
      dispatch({
        type: 'SET_ERROR',
        payload: error.response?.data?.detail || 'Failed to find resources. Please try again.',
      });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const getComplexityColor = (complexity: string) => {
    switch (complexity) {
      case 'beginner':
        return '#10b981';
      case 'intermediate':
        return '#f59e0b';
      case 'advanced':
        return '#ef4444';
      default:
        return '#6b7280';
    }
  };

  const getCategoryBadge = (category: string) => {
    const colors: Record<string, string> = {
      concept: '#3b82f6',
      technology: '#8b5cf6',
      skill: '#10b981',
      tool: '#f59e0b',
    };
    return colors[category] || '#6b7280';
  };

  return (
    <div className="task-analysis-container">
      <div className="analysis-header">
        <h2>Task Analysis</h2>
        <span
          className="complexity-badge"
          style={{ backgroundColor: getComplexityColor(estimated_complexity) }}
        >
          {estimated_complexity}
        </span>
      </div>

      <div className="learning-order">
        <h3>Suggested Learning Order</h3>
        <ol>
          {suggested_learning_order.map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ol>
      </div>

      <div className="prerequisites-section">
        <h3>Prerequisites</h3>
        <p className="subtitle">
          Check the prerequisites you already know. We'll find resources for the ones you don't.
        </p>

        <div className="prerequisites-list">
          {prerequisites.map((prereq, index) => (
            <div key={index} className="prerequisite-item">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={selectedIndices.includes(index)}
                  onChange={() => handleCheckboxChange(index)}
                />
                <span className="checkbox-custom">
                  {selectedIndices.includes(index) && <CheckCircle2 size={16} />}
                </span>
                <div className="prereq-content">
                  <div className="prereq-header">
                    <span className="prereq-name">{prereq.name}</span>
                    <span
                      className="category-badge"
                      style={{ backgroundColor: getCategoryBadge(prereq.category) }}
                    >
                      {prereq.category}
                    </span>
                  </div>
                  <p className="prereq-description">{prereq.description}</p>
                </div>
              </label>
            </div>
          ))}
        </div>

        <button
          className="btn-primary btn-large"
          onClick={handleFindResources}
          disabled={state.isLoading}
        >
          {state.isLoading ? (
            <>
              <Loader2 size={20} className="spinner" />
              Finding Resources...
            </>
          ) : (
            <>
              <Search size={20} />
              Find Learning Resources
            </>
          )}
        </button>
      </div>

      {state.error && <div className="error-message">{state.error}</div>}
    </div>
  );
}

export default TaskAnalysis;