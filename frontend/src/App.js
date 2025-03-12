// App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ChequeParse } from './components/ChequeParse';
import './EnhancedChequeParse.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<ChequeParse />} />
      </Routes>
    </Router>
  );
}

export default App;
