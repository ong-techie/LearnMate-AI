// Main App component for LearnMate

import { useState, useRef, useEffect } from 'react';
import { AppProvider, useAppContext } from './context/AppContext';
import { Header, TaskInput, TaskAnalysis, ResourceDisplay, AgentPanel } from './components';
import './App.css';

function AppContent() {
  const { state } = useAppContext();
  const [sidebarWidth, setSidebarWidth] = useState(() => {
    const saved = localStorage.getItem('sidebarWidth');
    return saved ? parseInt(saved, 10) : 380;
  });
  const [isResizing, setIsResizing] = useState(false);
  const sidebarRef = useRef<HTMLElement>(null);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing) return;

      const newWidth = window.innerWidth - e.clientX - 24;
      const minWidth = 200;
      const maxWidth = window.innerWidth - 400;

      if (newWidth >= minWidth && newWidth <= maxWidth) {
        setSidebarWidth(newWidth);
        localStorage.setItem('sidebarWidth', newWidth.toString());
      }
    };

    const handleMouseUp = () => {
      setIsResizing(false);
    };

    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'ew-resize';
      document.body.style.userSelect = 'none';
    } else {
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing]);

  return (
    <div className="app">
      <Header />

      <main
        className="app-main"
        style={state.phase === 'resources' ? {
          gridTemplateColumns: `1fr 8px ${sidebarWidth}px`
        } : undefined}
      >
        <div className="main-content">
          {state.phase === 'input' && <TaskInput />}
          {state.phase === 'analysis' && <TaskAnalysis />}
          {state.phase === 'resources' && (
            <>
              <ResourceDisplay />
            </>
          )}
        </div>

        {state.phase === 'resources' && (
          <>
            <div
              className="resize-handle"
              onMouseDown={() => setIsResizing(true)}
              title="Drag to resize"
            />
            <aside className="sidebar" ref={sidebarRef}>
              <AgentPanel />
            </aside>
          </>
        )}
      </main>
    </div>
  );
}

function App() {
  return (
    <AppProvider>
      <AppContent />
    </AppProvider>
  );
}

export default App;