import React from 'react';
import { TextField, Button, Grid, Typography } from '@mui/material';
import styled from 'styled-components';
import { theme } from '../App';

const StyledTextField = styled(TextField)`
  margin-bottom: ${theme.spacing(2)};
`;

const DataDisplay = ({ data, currentPage, totalPages, onPageChange }) => {
  return (
    <>
      <Grid container spacing={2}>
        {Object.entries(data).map(([key, value]) => (
          <Grid item xs={12} sm={6} key={key}>
            <StyledTextField
              label={key}
              value={value.value}
              fullWidth
              InputProps={{
                readOnly: true,
              }}
              helperText={`Confidence: ${value.confidence}%`}
            />
          </Grid>
        ))}
      </Grid>
      <Grid container justifyContent="space-between" style={{ marginTop: '1rem' }}>
        <Button
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage === 0}
        >
          Previous
        </Button>
        <Typography>
          Page {currentPage + 1} of {totalPages}
        </Typography>
        <Button
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage === totalPages - 1}
        >
          Next
        </Button>
      </Grid>
    </>
  );
};

export default DataDisplay;