import React, { useRef } from 'react';
import { ChequeVisualization } from './ChequeVisualization';
import { ChequeDataForm } from './ChequeDataForm';

export const ParsedChequeViewer = ({ 
  results, 
  currentPage, 
  setCurrentPage, 
  fields, 
  handleFieldChange,
  fieldConfig 
}) => {
  const svgRef = useRef(null);
  const inputRefs = useRef({});

  if (results.length === 0) {
    return (
      <section className="main-section">
        <h2>Parsed Cheque Data</h2>
        <p className="no-data">No data to display. Please parse a cheque first.</p>
      </section>
    );
  }

  console.log("logs---------------",results.length, currentPage)
  return (
    <section className="main-section">
      <h2>Parsed Cheque Data</h2>
      <div className="content-wrapper">
        <ChequeDataForm 
          fields={fields} 
          handleFieldChange={handleFieldChange} 
          fieldConfig={fieldConfig}
        />
        <ChequeVisualization 
          svgRef={svgRef}
          result={results[currentPage]}
          fieldConfig={fieldConfig}
          fields={fields}
          handleFieldChange={handleFieldChange}
          inputRefs={inputRefs}
        />
      </div>
      <div className="pagination">
        <button
          onClick={() => setCurrentPage(prev => Math.max(0, prev - 1))}
          disabled={currentPage === 0}
          className="button"
        >
          Previous
        </button>
        <span>Page {currentPage + 1} of {results.length}</span>
        <button
          onClick={() => setCurrentPage(prev => Math.min(results.length - 1, prev + 1))}
          disabled={currentPage === results.length - 1}
          className="button"
        >
          Next
        </button>
      </div>
    </section>
  );
};
