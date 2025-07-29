import React from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const TimeSeriesChart = ({ data }) => {
  if (!data) return null;

  const fields = Object.keys(data);
  const chartData = {
    labels: data[fields[0]]?.time_series.map(d => d.period),
    datasets: fields.map(field => ({
      label: field,
      data: data[field].time_series.map(d => d.value),
      fill: false,
      borderColor: `rgb(${Math.random() * 255}, ${Math.random() * 255}, ${Math.random() * 255})`,
      tension: 0.1
    }))
  };

  return <Line data={chartData} />;
};

export default TimeSeriesChart;