import React from 'react';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import { formatDDMMYYYY } from '../utils/dateUtils';

export const AllChequesTable = ({ 
  allCheques, 
  searchTerm, 
  setSearchTerm, 
  dateRange, 
  setDateRange, 
  fieldConfig,
  fetchAllCheques
}) => {
  const filteredCheques = allCheques.filter(cheque =>
    Object.values(cheque).some(value => 
      value?.toString()?.toLowerCase()?.includes(searchTerm.toLowerCase())
    )
  );

  return (
    <section className="all-cheques-section">
      <h2>Parsed Cheques</h2>
      <div className="filters">
        <div className="date-filters">
          <div className="date-picker-container">
            <label>Start Date:</label>
            <DatePicker
              selected={dateRange.startDate}
              onChange={(date) => setDateRange(prev => ({ ...prev, startDate: date }))}
              selectsStart
              startDate={dateRange.startDate}
              endDate={dateRange.endDate}
              className="date-input"
              placeholderText="Select start date"
              isClearable
            />
          </div>
          <div className="date-picker-container">
            <label>End Date:</label>
            <DatePicker
              selected={dateRange.endDate}
              onChange={(date) => setDateRange(prev => ({ ...prev, endDate: date }))}
              selectsEnd
              startDate={dateRange.startDate}
              endDate={dateRange.endDate}
              minDate={dateRange.startDate}
              className="date-input"
              placeholderText="Select end date"
              isClearable
            />
          </div>
        </div>
          <input
            type="text"
            placeholder="Search cheques..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          <button
            onClick={fetchAllCheques}
            className="fetch-button"
          >
            Fetch Cheques
          </button>
      </div>
      <table className="cheques-table">
        <thead>
          <tr>
            {Object.keys(fieldConfig).map(field => (
              <th key={field}>{fieldConfig[field].label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
        {filteredCheques.map((cheque, index) => (
            <tr key={index}>
              {Object.keys(fieldConfig).map(field => (
                <td key={field}>
                  {field === 'date' && cheque[field]
                    ? formatDDMMYYYY(cheque[field])
                    : cheque[field]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
};
