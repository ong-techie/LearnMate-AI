// Agent panel with Project Planner, Code Companion, and Tutor

import  { useState } from 'react';
import { ClipboardList, Code, GraduationCap, Loader2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { useAppContext } from '../context/AppContext';
import learnMateApi from '../services/api';

type Tab = 'plan' | 'code' | 'tutor';

export function AgentPanel() {
  const { state } = useAppContext();
  const [activeTab, setActiveTab] = useState<Tab>('plan');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Plan state
  const [plan, setPlan] = useState<string>('');

  // Code state
  const [concept, setConcept] = useState('');
  const [codeExample, setCodeExample] = useState('');

  // Tutor state
  const [query, setQuery] = useState('');
  const [tutorResponse, setTutorResponse] = useState('');

  if (state.phase !== 'resources') return null;

  const handleGeneratePlan = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await learnMateApi.generatePlan();
      setPlan(result);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate plan');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGetCodeExample = async () => {
    if (!concept.trim()) return;
    setIsLoading(true);
    setError(null);
    try {
      const result = await learnMateApi.getCodeExample(concept);
      setCodeExample(result);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to get code example');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAskTutor = async () => {
    if (!query.trim()) return;
    setIsLoading(true);
    setError(null);
    try {
      const result = await learnMateApi.askTutor(query);
      setTutorResponse(result);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to get tutor response');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="agent-panel">
      <div className="panel-header">
        <h2>AI Agents</h2>
      </div>

      <div className="tabs">
        <button
          className={`tab ${activeTab === 'plan' ? 'active' : ''}`}
          onClick={() => setActiveTab('plan')}
        >
          <ClipboardList size={18} />
          Plan
        </button>
        <button
          className={`tab ${activeTab === 'code' ? 'active' : ''}`}
          onClick={() => setActiveTab('code')}
        >
          <Code size={18} />
          Code
        </button>
        <button
          className={`tab ${activeTab === 'tutor' ? 'active' : ''}`}
          onClick={() => setActiveTab('tutor')}
        >
          <GraduationCap size={18} />
          Tutor
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'plan' && (
          <div className="plan-tab">
            <p className="tab-description">
              Generate a step-by-step project plan based on your task.
            </p>
            {!plan && (
              <button
                className="btn-primary"
                onClick={handleGeneratePlan}
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <Loader2 size={18} className="spinner" />
                    Generating...
                  </>
                ) : (
                  'Generate Plan'
                )}
              </button>
            )}
            {plan && (
              <div className="result-box">
                <ReactMarkdown>{plan}</ReactMarkdown>
              </div>
            )}
          </div>
        )}

        {activeTab === 'code' && (
          <div className="code-tab">
            <p className="tab-description">
              Get code examples for specific concepts from your task.
            </p>
            <div className="input-row">
              <input
                type="text"
                value={concept}
                onChange={(e) => setConcept(e.target.value)}
                placeholder="Enter concept (e.g., Python BeautifulSoup)"
                onKeyDown={(e) => e.key === 'Enter' && handleGetCodeExample()}
              />
              <button
                className="btn-primary"
                onClick={handleGetCodeExample}
                disabled={isLoading || !concept.trim()}
              >
                {isLoading ? (
                  <Loader2 size={18} className="spinner" />
                ) : (
                  'Get Example'
                )}
              </button>
            </div>
            {codeExample && (
              <div className="result-box code-result">
                <ReactMarkdown>{codeExample}</ReactMarkdown>
              </div>
            )}
          </div>
        )}

        {activeTab === 'tutor' && (
          <div className="tutor-tab">
            <p className="tab-description">
              Ask questions about your task or paste error messages for help.
            </p>
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask a question or paste an error message..."
              rows={4}
            />
            <button
              className="btn-primary"
              onClick={handleAskTutor}
              disabled={isLoading || !query.trim()}
            >
              {isLoading ? (
                <>
                  <Loader2 size={18} className="spinner" />
                  Thinking...
                </>
              ) : (
                'Ask Tutor'
              )}
            </button>
            {tutorResponse && (
              <div className="result-box">
                <ReactMarkdown>{tutorResponse}</ReactMarkdown>
              </div>
            )}
          </div>
        )}

        {error && <div className="error-message">{error}</div>}
      </div>
    </div>
  );
}

export default AgentPanel;