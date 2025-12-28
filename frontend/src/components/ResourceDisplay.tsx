// Resource display component with accordion

import { useState } from 'react';
import { ChevronDown, ExternalLink, BookOpen, Download, Loader2 } from 'lucide-react';
import { useAppContext } from '../context/AppContext';
import learnMateApi from '../services/api';

export function ResourceDisplay() {
  const { state } = useAppContext();
  const [openConcepts, setOpenConcepts] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const concepts = Object.keys(state.resources);

  if (concepts.length === 0) return null;

  const toggleConcept = (concept: string) => {
    setOpenConcepts((prev) =>
      prev.includes(concept) ? prev.filter((c) => c !== concept) : [...prev, concept]
    );
  };

  const expandAll = () => {
    setOpenConcepts(concepts);
  };

  const collapseAll = () => {
    setOpenConcepts([]);
  };

  const handleExportMarkdown = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const { markdown, filename } = await learnMateApi.exportMarkdown();
      // Create download
      const blob = new Blob([markdown], { type: 'text/markdown' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to export markdown');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="resource-display-container">
      <div className="resources-header">
        <h2>
          <BookOpen size={24} />
          Learning Resources
        </h2>
        <div className="expand-controls">
          <button onClick={expandAll} className="btn-text">
            Expand All
          </button>
          <button onClick={collapseAll} className="btn-text">
            Collapse All
          </button>
          <button className="btn-secondary btn-small" onClick={handleExportMarkdown} disabled={isLoading}>
            <Download size={16} />
            Export
          </button>
        </div>
      </div>

      <div className="resources-accordion">
        {concepts.map((concept) => {
          const isOpen = openConcepts.includes(concept);
          const resources = state.resources[concept];

          return (
            <div key={concept} className="accordion-item">
              <button
                className={`accordion-trigger ${isOpen ? 'open' : ''}`}
                onClick={() => toggleConcept(concept)}
              >
                <span className="concept-name">{concept}</span>
                <span className="resource-count">{resources.length} resources</span>
                <ChevronDown
                  size={20}
                  className={`chevron ${isOpen ? 'rotated' : ''}`}
                />
              </button>

              {isOpen && (
                <div className="accordion-content">
                  {resources.map((resource, index) => (
                    <a
                      key={index}
                      href={resource.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="resource-card"
                    >
                      <div className="resource-info">
                        <h4 className="resource-title">{resource.title}</h4>
                        <p className="resource-description">{resource.description}</p>
                        <span className="resource-source">{resource.source}</span>
                      </div>
                      <ExternalLink size={16} className="external-icon" />
                    </a>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
      {error && <div className="error-message">{error}</div>}
    </div>
  );
}

export default ResourceDisplay;
