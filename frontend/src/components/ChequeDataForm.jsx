import React from 'react';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import { formatDate, parseDate } from '../utils/dateUtils';

export const ChequeDataForm = ({ fields, handleFieldChange, fieldConfig }) => {
  return (
    <div className="card form-section">
      <h3>Extracted Data</h3>
      {Object.entries(fieldConfig).map(([field, config]) => (
        <div key={field} className="input-group">
          <label htmlFor={field}>{config.label}</label>
          {field === 'date' ? (
            <DatePicker
              selected={parseDate(fields[field]?.value)}
              onChange={(date) => handleFieldChange(field, formatDate(date))}
              dateFormat="ddMMyyyy"
              className="input-field"
              style={{ borderColor: config.color }}
            />
          ) : (
            <input
              id={field}
              type="text"
              value={fields[field]?.value || ''}
              onChange={(e) => handleFieldChange(field, e.target.value)}
              className="input-field"
              style={{ borderColor: config.color }}
            />
          )}
        </div>
      ))}
    </div>
  );
};