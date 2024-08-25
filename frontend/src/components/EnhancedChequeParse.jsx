import React, { useState, useEffect, useRef } from 'react';
import * as d3 from 'd3';
import './EnhancedChequeParse.css';
import { saveAs } from 'file-saver';
import { utils, write } from 'xlsx';
import { Document, Page, View, Text, pdf } from '@react-pdf/renderer';

/**
 * EnhancedChequeParse Component
 * 
 * This component provides a comprehensive interface for parsing cheques,
 * visualizing the results, and allowing users to edit the extracted data.
 */
const EnhancedChequeParse = () => {
  // State declarations
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(0);
  const svgRef = useRef(null);

  // Configuration for cheque fields
  const fieldConfig = {
    date: { label: 'Date', x: 900, y: 30, color: '#3357FF' },
    // id: { label: 'ID', x: 50, y: 30, color: '#FF5733' },
    bank_name: { label: 'Bank Name', x: 100, y: 10, color: '#20B2AA' },
    ifsc_code: { label: 'IFSC Code', x:500, y: 20, color: '#20B2AA' },
    amount_in_words: { label: 'Amount in Words', x: 300, y: 130, color: '#FF33FF' },
    amount_in_digits: { label: 'Amount in Digits', x: 800, y: 180, color: '#33FFFF' },
    payer: { label: 'Payer', x: 400, y: 70, color: '#FFA500' },
    account_number: { label: 'Account Number', x: 300, y: 220, color: '#8A2BE2' },
    cheque_number: { label: 'Cheque Number', x: 600, y: 400, color: '#20B2AA' },
    party_code: { label: 'Party Code',  x: 850, y: 380, color: '#DC143C' },
    party_name: { label: 'Party Name',  x: 850, y: 430, color: '#4B0082' }
  };

  const [fields, setFields] = useState(
    Object.keys(fieldConfig).reduce((acc, key) => ({ ...acc, [key]: '' }), {})
  );

  /**
   * Handles file selection for upload
   * @param {Event} event - The file input change event
   */
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

  /**
   * Handles the cheque parsing process
   */
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
        setFields(data.data[0].extracted_data || fields);
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

  /**
   * Updates the state when a field value changes
   * @param {string} field - The field name
   * @param {string} value - The new value
   */
  const handleFieldChange = (field, value) => {
    setFields(prevFields => ({
      ...prevFields,
      [field]: value
    }));
  };

  /**
   * Saves the parsed and potentially edited data to the database
   */
  const handleSaveToDb = async () => {
    try {
      const updatedResults = [...results];
      updatedResults[currentPage].extracted_data = fields;

      const response = await fetch('http://172.105.50.148:5050/api/save-to-db', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedResults),
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

  /**
   * Renders the D3 visualization of the cheque
   */
  useEffect(() => {
    if (results.length > 0 && results[currentPage].image_data) {
      const svg = d3.select(svgRef.current);
      svg.selectAll("*").remove(); // Clear previous content

      const width = 1000;
      const height = 500;

      svg
        .attr("width", width)
        .attr("height", height)
        .style("border", "1px solid #ccc");

      // Create an image element
      svg.append("image")
        .attr("xlink:href", `data:image/jpeg;base64,${results[currentPage].image_data}`)
        .attr("width", width)
        .attr("height", 400);

      // Add dots and input fields for each field
      Object.entries(fieldConfig).forEach(([field, config]) => {
        // Add dot on the cheque
        svg.append("circle")
          .attr("cx", config.x)
          .attr("cy", config.y)
          .attr("r", 5)
          .attr("fill", config.color);

        // Add input field below the dot
        const foreignObject = svg.append("foreignObject")
          .attr("x", config.x - 75)  // Center the input field below the dot
          .attr("y", config.y + 10)  // Position it just below the dot
          .attr("width", 200)
          .attr("height", 45);

          const input = foreignObject.append("xhtml:input")
          .attr("type", "text")
          .attr("value", fields[field] || '')
          .attr("placeholder", config.label)
          .style("width", "100%")
          .style("height", "100%")
          .style("font-size", "12px")
          .style("padding", "5px")
          .style("border", "none")
          .style("border-radius", "3px")
          .style("color", "white")
          .style("background-color", "rgba(0, 0, 0, 0.8)")  // Semi-transparent black background
          .style("outline", "none")  // Remove the focus outline
          .style("transition", "background-color 0.3s");  // Smooth transition for hover effect

        input.on("input", function() {
          handleFieldChange(field, this.value);
        });

        // Add label above the input field
        svg.append("text")
          .attr("x", config.x)
          .attr("y", config.y + 8)  // Position it just above the input field
          .text(config.label)
          .style("font-size", "10px")
          .style("font-weight", "bold")
          .style("fill", config.color)
          .style("text-anchor", "middle");
      });
    }
  }, [results, currentPage, fields]);

  useEffect(() => {
    if (results.length > 0) {
      setFields(results[currentPage].extracted_data || {});
    }
  }, [currentPage, results]);

  const exportToCSV = () => {
    const ws = utils.json_to_sheet(results.map(r => r.extracted_data));
    const wb = utils.book_new();
    utils.book_append_sheet(wb, ws, "Cheque Data");
    const wbout = write(wb, { bookType: 'csv', type: 'binary' });
    saveAs(new Blob([s2ab(wbout)], { type: "application/octet-stream" }), "cheque_data.csv");
  };

  const exportToPDF = async () => {
    const MyDocument = () => (
      <Document>
        <Page size="A4">
          <View>
            <Text>Cheque Data</Text>
            {results.map((result, index) => (
              <View key={index}>
                <Text>Page {index + 1}</Text>
                {Object.entries(result.extracted_data).map(([key, value]) => (
                  <Text key={key}>{key}: {value}</Text>
                ))}
              </View>
            ))}
          </View>
        </Page>
      </Document>
    );

    const blob = await pdf(<MyDocument />).toBlob();
    saveAs(blob, "cheque_data.pdf");
  };

  function s2ab(s) {
    const buf = new ArrayBuffer(s.length);
    const view = new Uint8Array(buf);
    for (let i = 0; i != s.length; ++i) view[i] = s.charCodeAt(i) & 0xFF;
    return buf;
  }


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
            <>
            <button onClick={handleSaveToDb} className="button">Save to Database</button>
            <button onClick={exportToCSV} className="button">Export to CSV</button>
            <button onClick={exportToPDF} className="button">Export to PDF</button>
            </>
          )}
          {error && <div className="error-message">{error}</div>}
          {uploading && <div className="loading-spinner"></div>}
        </aside>
        <section className="main-section">
          <h2>Parsed Cheque Data</h2>
          {results.length > 0 ? (
            <>
              <div className="content-wrapper">
                <div className="card form-section">
                  <h3>Extracted Data</h3>
                  {Object.entries(fieldConfig).map(([field, config]) => (
                    <div key={field} className="input-group">
                      <label htmlFor={field}>{config.label}</label>
                      <input
                        id={field}
                        type="text"
                        value={fields[field] || ''}
                        onChange={(e) => handleFieldChange(field, e.target.value)}
                        className="input-field"
                        style={{ borderColor: config.color }}
                      />
                    </div>
                  ))}
                </div>
                <div className="card image-section">
                  <svg ref={svgRef}></svg>
                </div>
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
            </>
          ) : (
            <p className="no-data">No data to display. Please parse a cheque first.</p>
          )}
        </section>
      </main>
    </div>
  );
};

export default EnhancedChequeParse;