// Header component for LearnMate

import React from 'react';
import { BookOpen, RotateCcw } from 'lucide-react';
import { useAppContext } from '../context/AppContext';

export function Header() {
  const { state, dispatch } = useAppContext();

  const handleReset = () => {
    dispatch({ type: 'RESET_STATE' });
  };

  return (
    <header className="app-header">
      <div className="logo">
        <BookOpen size={32} />
        <h1>LearnMate</h1>
      </div>
      <p className="tagline">AI-Powered Learning Resource Discovery</p>
      {state.phase !== 'input' && (
        <button className="btn-ghost" onClick={handleReset}>
          <RotateCcw size={18} />
          New Task
        </button>
      )}
    </header>
  );
}

export default Header;