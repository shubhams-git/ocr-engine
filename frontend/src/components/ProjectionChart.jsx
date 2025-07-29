import React from 'react';
import { Line } from 'react-chartjs-2';

const ProjectionChart = ({ data }) => {
  if (!data) return null;

  const projectionData = data['1_year_ahead'];
  if (!projectionData) return null;

  const chartData = {
    labels: projectionData.revenue.map(d => d.period),
    datasets: [
      {
        label: 'Projected Revenue',
        data: projectionData.revenue.map(d => d.value),
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1,
      },
      {
        label: 'Projected Expenses',
        data: projectionData.expenses.map(d => d.value),
        borderColor: 'rgb(255, 99, 132)',
        tension: 0.1,
      },
    ],
  };

  return <Line data={chartData} />;
};

export default ProjectionChart;