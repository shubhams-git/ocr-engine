import React from 'react';

const StatementTable = ({ data }) => {
  if (!data) return null;

  const fields = Object.keys(data);

  return (
    <div className="statement-table">
      <table>
        <thead>
          <tr>
            <th>Field</th>
            <th>Mapped From</th>
            <th>Confidence</th>
          </tr>
        </thead>
        <tbody>
          {fields.map((field, index) => (
            <tr key={index}>
              <td>{field}</td>
              <td>{data[field].mapped_from.join(', ')}</td>
              <td>{data[field].confidence}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default StatementTable;