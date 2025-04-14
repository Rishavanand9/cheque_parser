
// components/ChequeParse.js
import React, { useState, useEffect } from 'react';
import { Sidebar } from './Sidebar';
import { ParsedChequeViewer } from './ParsedChequeViewer';
import { AllChequesTable } from './AllChequesTable';
import { fieldConfig } from '../config/fieldConfig';
import { API_URL } from '../config/constants';

export const ChequeParse = () => {
  // State declarations
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [allCheques, setAllCheques] = useState([]);
  const [editedFields, setEditedFields] = useState([]);
  const [dateRange, setDateRange] = useState({
    startDate: new Date(),
    endDate: new Date()
  });
  
  const [fields, setFields] = useState(
    Object.keys(fieldConfig).reduce((acc, key) => ({ ...acc, [key]: '' }), {})
  );

  const handleFieldChange = (field, value) => {
    setEditedFields(prevEditedFields => {
      const newEditedFields = [...prevEditedFields];
      if (!newEditedFields[currentPage]) {
        newEditedFields[currentPage] = {};
      }
      newEditedFields[currentPage][field] = { value, confidence: 1 };
      return newEditedFields;
    });
  };

  /**
   * Handles file selection for upload
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
      const response = await fetch(`${API_URL}/api/parse-cheque`, {
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
   * Saves the parsed and potentially edited data to the database
   */
  const handleSaveToDb = async () => {
    try {
      let updatedResults = results.map((result, index) => ({
        ...result,
        extracted_data: {
          ...result.extracted_data,
          ...(editedFields[index] || {})
        }
      }));
  
      // Appending image path to Request obj
      updatedResults = updatedResults.map(i => { 
        return {...i, extracted_data: {...i.extracted_data, image_path: {confidence: 100, value: i.image_data} } }
      });

      const response = await fetch(`${API_URL}/api/save-to-db`, {
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

  useEffect(() => {
    if (results.length > 0) {
      const currentData = results[currentPage].extracted_data;
      const editedData = editedFields[currentPage] || {};
      setFields({
        ...currentData,
        ...editedData
      });
    }
  }, [currentPage, results, editedFields]);

  useEffect(() => {
    fetchAllCheques();
    // eslint-disable-next-line
  }, [dateRange]);

  const fetchAllCheques = async () => {
    try {
      const params = new URLSearchParams();
      if (dateRange.startDate) {
        params.append('start_date', dateRange.startDate.toISOString());
      }
      if (dateRange.endDate) {
        params.append('end_date', dateRange.endDate.toISOString());
      }

      const url = `${API_URL}/api/get-all-cheques${params.toString() ? '?' + params.toString() : ''}`;
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      if (data.status === 'success') {
        setAllCheques(data.data);
      } else {
        throw new Error(data.message || 'Failed to fetch cheques.');
      }
    } catch (error) {
      console.error('Fetch error:', error);
      setError(`Error fetching cheques: ${error.message}`);
    }
  };

  return (
    <div className="dashboard">
      <header className="header">
        <h1>Cheque Parser Dashboard</h1>
      </header>
      <main className="main-content">
        <Sidebar 
          file={file}
          uploading={uploading}
          error={error}
          results={results}
          handleFileChange={handleFileChange}
          handleUpload={handleUpload}
          handleSaveToDb={handleSaveToDb}
        />
        <ParsedChequeViewer 
          results={results}
          currentPage={currentPage}
          setCurrentPage={setCurrentPage}
          fields={fields}
          handleFieldChange={handleFieldChange}
          fieldConfig={fieldConfig}
        />
        <AllChequesTable 
          allCheques={allCheques}
          searchTerm={searchTerm}
          setSearchTerm={setSearchTerm}
          dateRange={dateRange}
          setDateRange={setDateRange}
          fieldConfig={fieldConfig}
          fetchAllCheques={fetchAllCheques}
        />
      </main>
    </div>
  );
};