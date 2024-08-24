import React, { useState } from 'react';
import './EnhancedChequeParse.css';

const EnhancedChequeParse = () => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(0);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile);
      setError(null);
    } else {
      setFile(null);
      setError('Please select a PDF file');
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    setUploading(true);
    setError(null);

    try {
      const response = await fetch('http://172.105.50.148:5050/api/parse-cheque', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      if (data.status === 'success') {
        setResults(data.data);
        setCurrentPage(0);
      } else {
        throw new Error(data.message || 'Failed to parse cheque.');
      }
    } catch (error) {
      console.error('Fetch error:', error);
      setError(`Error: ${error.message}. Please try again or contact support if the issue persists.`);
    } finally {
      setUploading(false);
    }
  };

  const handleSaveToDb = async () => {
    try {
      const response = await fetch('http://172.105.50.148:5050/api/save-to-db', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(results),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      if (data.status === 'success') {
        alert('Data saved to database successfully!');
      } else {
        throw new Error(data.message || 'Failed to save data to database.');
      }
    } catch (error) {
      console.error('Save to DB error:', error);
      setError(`Error saving to database: ${error.message}`);
    }
  };

  const renderContent = () => {
    if (results.length === 0) {
      return <p className="no-data">No data to display. Please parse a cheque first.</p>;
    }

    const currentData = results[currentPage];

    return (
      <div className="content-wrapper">
        <div className="image-section">
          <img 
            src={`data:image/jpeg;base64,${currentData.image_data}`} 
            alt={`Cheque ${currentPage + 1}`} 
            className="cheque-image"
          />
        </div>
        <div className="data-section">
          <h3>Extracted Data</h3>
          <pre className="json-data">{JSON.stringify(currentData.extracted_data, null, 2)}</pre>
          <h3>Full Text</h3>
          <p className="full-text">{currentData.full_text}</p>
        </div>
      </div>
    );
  };

  return (
    <div className="dashboard">
      <header className="header">
        <h1>Cheque Parser Dashboard</h1>
      </header>
      <main className="main-content">
        <aside className="sidebar">
          <h2>Upload PDF</h2>
          <input
            type="file"
            onChange={handleFileChange}
            accept=".pdf"
            className="file-input"
          />
          <button
            onClick={handleUpload}
            disabled={!file || uploading}
            className={`button ${(!file || uploading) ? 'disabled' : ''}`}
          >
            {uploading ? 'Parsing...' : 'Parse Cheque'}
          </button>
          {results.length > 0 && (
            <button onClick={handleSaveToDb} className="button">Save to Database</button>
          )}
          {error && <div className="error-message">{error}</div>}
          {uploading && <div className="loading-spinner"></div>}
        </aside>
        <section className="main-section">
          <h2>Parsed Cheque Data</h2>
          {renderContent()}
          {results.length > 1 && (
            <div className="pagination">
              <button
                onClick={() => setCurrentPage(prev => Math.max(0, prev - 1))}
                disabled={currentPage === 0}
                className="button"
              >
                Previous
              </button>
              <span>{`Page ${currentPage + 1} of ${results.length}`}</span>
              <button
                onClick={() => setCurrentPage(prev => Math.min(results.length - 1, prev + 1))}
                disabled={currentPage === results.length - 1}
                className="button"
              >
                Next
              </button>
            </div>
          )}
        </section>
      </main>
    </div>
  );
};

export default EnhancedChequeParse;