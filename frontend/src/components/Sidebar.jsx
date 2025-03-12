import React from 'react';
import { exportToCSV, exportToPDF } from '../utils/exportUtils';

export const Sidebar = ({ 
  file, 
  uploading, 
  error, 
  results, 
  handleFileChange, 
  handleUpload, 
  handleSaveToDb 
}) => {
  return (
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
        <>
        <button onClick={handleSaveToDb} className="button">Save to Database</button>
        <button onClick={() => exportToCSV(results)} className="button">Export to CSV</button>
        <button onClick={() => exportToPDF(results)} className="button">Export to PDF</button>
        </>
      )}
      {error && <div className="error-message">{error}</div>}
      {uploading && <div className="loading-spinner"></div>}
    </aside>
  );
};