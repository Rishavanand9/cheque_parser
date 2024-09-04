import React, { useState } from 'react';
import { Grid, Paper, Typography } from '@mui/material';
import styled from 'styled-components';
import FileUpload from './FileUpload';
import DataDisplay from './DataDisplay';
import ImageDisplay from './ImageDisplay';
import { parseChequePDF } from '../services/chequeParseService';
import { theme } from '../App';

const MainContent = styled.main`
  flex-grow: 1;
  padding: ${theme.spacing(3)};
`;

const StyledPaper = styled(Paper)`
  padding: ${theme.spacing(3)};
  height: 100%;
`;

const ChequeParse = () => {
  const [results, setResults] = useState([]);
  const [currentPage, setCurrentPage] = useState(0);
  const [error, setError] = useState(null);

  const handleFileUpload = async (file) => {
    try {
      const data = await parseChequePDF(file);
      setResults(data);
      setCurrentPage(0);
      setError(null);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <MainContent>
      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <StyledPaper>
            <FileUpload onFileUpload={handleFileUpload} error={error} />
          </StyledPaper>
        </Grid>
        <Grid item xs={12} md={8}>
          <StyledPaper>
            {results.length > 0 ? (
              <>
                <DataDisplay
                  data={JSON.parse(results[currentPage].extracted_data)}
                  currentPage={currentPage}
                  totalPages={results.length}
                  onPageChange={setCurrentPage}
                />
                <ImageDisplay imageData={results[currentPage].image_data} />
              </>
            ) : (
              <Typography>No data to display. Please parse a cheque first.</Typography>
            )}
          </StyledPaper>
        </Grid>
      </Grid>
    </MainContent>
  );
};

export default ChequeParse;