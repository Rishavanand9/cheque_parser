// App.js
import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import UploadPage from './components/UploadPage';
import ParserPage from './components/ParserPage';

const theme = createTheme();

function App() {
  const [pdfData, setPdfData] = useState(null);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/" element={<UploadPage setPdfData={setPdfData} />} />
          <Route path="/parser" element={<ParserPage pdfData={pdfData} />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;