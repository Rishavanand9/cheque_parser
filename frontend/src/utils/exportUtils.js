import { saveAs } from 'file-saver';
import { utils, write } from 'xlsx';
import { Document, Page, View, Text, pdf } from '@react-pdf/renderer';
import React from 'react';
import { fieldConfig } from '../config/fieldConfig';
import { formatDDMMYYYY } from './dateUtils';

export const exportToCSV = (results) => {
  const exportData = results.map((r, index) => {
    const extractedData = r.extracted_data || {};

    // Create a flattened object with just the values
    return Object.keys(fieldConfig).reduce((acc, field) => {
      const fieldData = extractedData[field] || {};
      acc[field] = field === 'date' ? formatDDMMYYYY(fieldData.value) : fieldData.value || '';
      return acc;
    }, {});
  });

  const ws = utils.json_to_sheet(exportData);
  const wb = utils.book_new();
  utils.book_append_sheet(wb, ws, "Cheque Data");
  const wbout = write(wb, { bookType: 'xlsx', type: 'binary' });
  const dateString = new Date().toISOString().split('T')[0];
  saveAs(new Blob([s2ab(wbout)], { type: "application/octet-stream" }), `cheque_data_${dateString}.xlsx`);
};

export const exportToPDF = async (results) => {
  const MyDocument = () => (
    <Document>
      <Page size="A4">
        <View>
          <Text>Cheque Data</Text>
          {results.map((result, index) => (
            <View key={index}>
              <Text>Page {index + 1}</Text>
              {Object.entries(result.extracted_data || {}).map(([key, value]) => (
                <Text key={key}>{key}: {value.value}</Text>
              ))}
            </View>
          ))}
        </View>
      </Page>
    </Document>
  );

  const blob = await pdf(<MyDocument />).toBlob();
  const dateString = new Date().toISOString().split('T')[0];
  const fileName = `cheque_data_${dateString}.pdf`;
  saveAs(blob, fileName);
};

function s2ab(s) {
  const buf = new ArrayBuffer(s.length);
  const view = new Uint8Array(buf);
  for (let i = 0; i !== s.length; ++i) view[i] = s.charCodeAt(i) & 0xFF;
  return buf;
}