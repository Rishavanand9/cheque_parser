import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [file, setFile] = useState(null);
  const [parsedData, setParsedData] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      alert('Please select a file first!');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    setLoading(true);
    try {
      const response = await axios.post('http://localhost:5050/api/parse-cheque', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setParsedData(response.data);
    } catch (error) {
      console.error('Error uploading file:', error);
      alert('Error uploading file. Please try again.');
    }
    setLoading(false);
  };

  const handleDataChange = (index, field, value) => {
    const newData = [...parsedData];
    newData[index] = { ...newData[index], [field]: value };
    setParsedData(newData);
  };

  const handleSubmit = async () => {
    try {
      await axios.post('http://localhost:5050/api/save-data', parsedData);
      alert('Data saved successfully!');
    } catch (error) {
      console.error('Error saving data:', error);
      alert('Error saving data. Please try again.');
    }
  };

  const handleExport = async () => {
    try {
      const response = await axios.post('http://localhost:5050/api/export-excel', parsedData, {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'cheque_data.xlsx');
      document.body.appendChild(link);
      link.click();
    } catch (error) {
      console.error('Error exporting to Excel:', error);
      alert('Error exporting to Excel. Please try again.');
    }
  };

  return (
    <div className="App">
      <h1>Cheque Parser Dashboard</h1>
      <input type="file" onChange={handleFileChange} accept=".pdf" />
      <button onClick={handleUpload} disabled={loading}>
        {loading ? 'Uploading...' : 'Upload and Parse'}
      </button>
      {parsedData.length > 0 && (
        <>
          <h2>Parsed Cheque Data</h2>
          {parsedData.map((pageData, pageIndex) => (
            <div key={pageIndex}>
              <h3>Page {pageIndex + 1}</h3>
              {Object.entries(pageData).map(([field, value]) => (
                <div key={field}>
                  <label>{field}: </label>
                  <input
                    type="text"
                    value={value}
                    onChange={(e) => handleDataChange(pageIndex, field, e.target.value)}
                  />
                </div>
              ))}
            </div>
          ))}
          <button onClick={handleSubmit}>Submit Data</button>
          <button onClick={handleExport}>Export to Excel</button>
        </>
      )}
    </div>
  );
}

export default App;