// components/UploadPage.js
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { AppBar, Toolbar, Typography, Button, Container } from '@mui/material';

function UploadPage({ setPdfData }) {
  const navigate = useNavigate();

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (file) {
      // Here you would typically send the file to your backend for processing
      // For this example, we'll simulate a response
      const mockResponse = [
        { id: 1, image: 'url1', annotations: { amount: '100', date: '2023-01-01' } },
        { id: 2, image: 'url2', annotations: { amount: '200', date: '2023-01-02' } },
      ];
      setPdfData(mockResponse);
      navigate('/parser');
    }
  };

  return (
    <>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6">Cheque Parser</Typography>
        </Toolbar>
      </AppBar>
      <Container maxWidth="sm" style={{ marginTop: '2rem' }}>
        <input
          accept="application/pdf"
          style={{ display: 'none' }}
          id="raised-button-file"
          type="file"
          onChange={handleFileUpload}
        />
        <label htmlFor="raised-button-file">
          <Button variant="contained" component="span">
            Upload PDF
          </Button>
        </label>
      </Container>
    </>
  );
}

export default UploadPage;