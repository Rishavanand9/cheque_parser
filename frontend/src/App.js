// App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import EnhancedChequeParse from './components/EnhancedChequeParse';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<EnhancedChequeParse />} />
      </Routes>
    </Router>
  );
}

export default App;