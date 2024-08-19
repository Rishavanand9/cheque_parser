
// components/ParserPage.js
import React, { useState } from 'react';
import { 
  Grid, 
  Paper, 
  List, 
  ListItem, 
  ListItemText, 
  TextField, 
  Button, 
  Pagination 
} from '@mui/material';

function ParserPage({ pdfData }) {
  const [currentPage, setCurrentPage] = useState(0);
  const [annotationValues, setAnnotationValues] = useState({});

  const handlePageChange = (event, value) => {
    setCurrentPage(value - 1);
  };

  const handleAnnotationChange = (key, value) => {
    setAnnotationValues(prev => ({ ...prev, [key]: value }));
  };

  const handleSubmit = () => {
    // Here you would typically send the data to your backend
    console.log('Submitting data:', annotationValues);
  };

  const handleExport = () => {
    // Here you would typically generate and download an Excel file
    console.log('Exporting to Excel');
  };

  if (!pdfData) return <div>No data available</div>;

  const currentData = pdfData[currentPage];

  return (
    <Grid container spacing={2}>
      <Grid item xs={3}>
        <Paper>
          <List>
            {Object.keys(currentData.annotations).map((key) => (
              <ListItem key={key}>
                <ListItemText primary={key} />
              </ListItem>
            ))}
          </List>
        </Paper>
      </Grid>
      <Grid item xs={9}>
        <Paper style={{ padding: '1rem' }}>
          <img src={currentData.image} alt={`Page ${currentPage + 1}`} style={{ width: '100%' }} />
          {Object.entries(currentData.annotations).map(([key, value]) => (
            <TextField
              key={key}
              label={key}
              value={annotationValues[key] || value}
              onChange={(e) => handleAnnotationChange(key, e.target.value)}
              style={{ position: 'absolute', /* You'll need to position these appropriately */ }}
            />
          ))}
        </Paper>
        <Pagination 
          count={pdfData.length} 
          page={currentPage + 1} 
          onChange={handlePageChange} 
        />
        <Button onClick={handleSubmit}>Submit</Button>
        <Button onClick={handleExport}>Export to Excel</Button>
      </Grid>
    </Grid>
  );
}

export default ParserPage;