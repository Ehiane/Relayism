/**
 * Main App component
 */

import React from 'react';
import HomePage from './pages/HomePage';
import './App.css';

const App: React.FC = () => {
  return (
    <div className="app">
      <HomePage />
    </div>
  );
};

export default App;
