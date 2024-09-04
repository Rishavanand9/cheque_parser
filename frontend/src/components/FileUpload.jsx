import React, { useState } from 'react';
import { Button, Typography } from '@mui/material';
import styled from 'styled-components';

const FileInput = styled.input`
  display: none;
`;

const FileUpload = ({ onFileUpload, error }) => {
  const [uploading, setUploading] = useState(false);

  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    if (file && file.type === 'application/pdf') {
      setUploading(true);
      await onFileUpload(file);
      setUploading(false);
    } else {
      onFileUpload(new Error('Please select a PDF file'));
    }
  };

  return (
    <>
      <FileInput
        accept=".pdf"
        id="contained-button-file"
        type="file"
        onChange={handleFileChange}
      />
      <label htmlFor="contained-button-file">
        <Button variant="contained" component="span" disabled={uploading}>
          {uploading ? 'Uploading...' : 'Upload PDF'}
        </Button>
      </label>
      {error && <Typography color="error">{error}</Typography>}
    </>
  );
};

export default FileUpload;
