import React, { useState } from 'react';
import axios from 'axios';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);
const allowedMonths = [2, 5, 8, 11];

type TaskAllocation = {
  task_name: string;
  workers: number;
};

type ForecastData = {
  forecast_date: string;
  expected_orders: number;
  forecasted_total_workers: number;
  confidence_interval_workers: [number, number];
  forecasted_total_labor_hours: number;
  llm_summary: string;
  assumptions: string[];
  task_allocations: TaskAllocation[];
};

const ForecastWorkers: React.FC = () => {
  const [expectedOrders, setExpectedOrders] = useState('10000000');
  const [forecastDate, setForecastDate] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [forecast, setForecast] = useState<ForecastData | null>(null);
  const [dateError, setDateError] = useState('');

const handleForecast = async () => {
    setError('');
    setDateError('');
    setForecast(null);

    if (!expectedOrders || isNaN(Number(expectedOrders)) || Number(expectedOrders) <= 0) {
      setError('Please enter a valid positive number for expected orders.');
      return;
    }

    // Date validation
    if (!forecastDate) {
      setDateError('Please provide the date on which supersale event happens.');
      return;
    } else {
      const month = new Date(forecastDate).getMonth();
      if (!allowedMonths.includes(month)) {
        setDateError('Supersale events only happen in March, June, September, or December. Please select a valid date.');
        return;
      }
    }

    setLoading(true);
    try {
      const response = await axios.post<ForecastData>('http://127.0.0.1:5001/forecast', {
        expectedOrders: Number(expectedOrders),
        forecastDate: forecastDate,
      });
      setForecast(response.data);
    } catch (err: any) {
      if (err.response?.data?.error) {
        setError(err.response.data.error);
      } else {
        setError('Could not connect to the backend server. Is it running?');
      }
    } finally {
      setLoading(false);
    }
  };


  // Chart data preparation
  const chartData = forecast
    ? {
        labels: forecast.task_allocations.map((t) => t.task_name),
        datasets: [
          {
            label: 'Number of Workers',
            data: forecast.task_allocations.map((t) => t.workers),
            backgroundColor: 'rgba(75, 192, 192, 0.6)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1,
          },
        ],
      }
    : undefined;

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: { display: false },
      title: { display: true, text: 'Worker Allocation by Task' },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: { display: true, text: 'Number of Workers' },
      },
      x: {
        title: { display: true, text: 'Task' },
      },
    },
  };

  return (
    <div className="container">
      <style>{`
        body {
          font-family: Arial, sans-serif;
          background-color: #f4f7f6;
        }
        .container {
          background-color: #fff;
          padding: 30px;
          border-radius: 8px;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
          width: 100%;
          max-width: 900px;
          box-sizing: border-box;
        }
        h1, h2, h3 {
          color: #0056b3;
          text-align: center;
          margin-bottom: 20px;
        }
        .input-section {
          display: flex;
          flex-wrap: wrap;
          gap: 15px;
          margin-bottom: 25px;
          align-items: center;
          justify-content: center;
        }
        .input-section label {
          font-weight: bold;
          color: #555;
        }
        .input-section input[type="number"],
        .input-section input[type="date"] {
          padding: 10px;
          border: 1px solid #ddd;
          border-radius: 4px;
          width: 200px;
          box-sizing: border-box;
        }
        .input-section button {
          padding: 10px 20px;
          background-color: #007bff;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 16px;
          transition: background-color 0.3s ease;
        }
        .input-section button:hover {
          background-color: #0056b3;
        }
        .hidden {
          display: none !important;
        }
        .loading {
          text-align: center;
          padding: 20px;
          font-size: 1.1em;
          color: #007bff;
        }
        .error-message {
          color: #dc3545;
          background-color: #f8d7da;
          border: 1px solid #f5c6cb;
          padding: 10px;
          border-radius: 4px;
          text-align: center;
          margin-bottom: 20px;
        }
        #results p {
          font-size: 1.1em;
          margin-bottom: 10px;
        }
        #results p strong {
          color: #0056b3;
        }
        .chart-container {
          position: relative;
          height: 400px;
          width: 100%;
          margin-top: 20px;
          margin-bottom: 30px;
          background-color: #f9f9f9;
          border-radius: 5px;
          padding: 10px;
          box-sizing: border-box;
        }
        .llm-summary-box {
          background-color: #e9f7ef;
          border: 1px solid #d4edda;
          border-left: 5px solid #28a745;
          padding: 15px;
          border-radius: 5px;
          margin-top: 20px;
          line-height: 1.6;
          color: #155724;
        }
        .assumptionsList {
          list-style-type: disc;
          padding-left: 20px;
          margin-top: 15px;
        }
        .assumptionsList li {
          margin-bottom: 5px;
          color: #555;
        }
        @media (max-width: 768px) {
          .input-section {
            flex-direction: column;
            align-items: stretch;
          }
          .input-section input,
          .input-section button {
            width: 100%;
          }
        }
      `}</style>
      <h2>Rakuten Supersale Workforce Forecaster</h2>
      <div className="input-section">
        <label htmlFor="expectedOrders">Expected Orders for Next Event:</label>
        <input
          type="number"
          id="expectedOrders"
          placeholder="e.g., 10000000"
          value={expectedOrders}
          onChange={e => setExpectedOrders(e.target.value)}
        />

        <label htmlFor="forecastDate">
          Target Date (Only March, June, September, December allowed):
        </label>
        <input
          type="date"
          id="forecastDate"
          value={forecastDate}
          onChange={e => {
            setForecastDate(e.target.value);
            setDateError(''); // Clear error on change
          }}
        />

        <button
          onClick={handleForecast}
          disabled={loading}
        >
          Get Forecast
        </button>
      </div>
      {dateError && <div className="error-message">{dateError}</div>}
      {loading && <div className="loading">Loading forecast...</div>}
      {error && <div className="error-message">{error}</div>}
      {forecast && (
        <div id="results">
          <h2>Forecast Summary</h2>
          <p>
            <strong>Forecast Date:</strong> <span>{forecast.forecast_date}</span>
          </p>
          <p>
            <strong>Expected Orders:</strong> <span>{forecast.expected_orders.toLocaleString()}</span>
          </p>
          <p>
            <strong>Total Workers Required:</strong> <span>{forecast.forecasted_total_workers.toLocaleString()}</span>
          </p>
          <p>
            <strong>Confidence Interval:</strong>{' '}
            <span>
              {forecast.confidence_interval_workers[0].toLocaleString()} -{' '}
              {forecast.confidence_interval_workers[1].toLocaleString()} workers
            </span>
          </p>
          <p>
            <strong>Total Labor Hours:</strong>{' '}
            <span>{forecast.forecasted_total_labor_hours.toLocaleString()} hours</span>
          </p>
          <h3>Worker Allocation by Task</h3>
          <div className="chart-container">
            {chartData && <Bar data={chartData} options={chartOptions} />}
          </div>
          {/* <h3>LLM Generated Summary</h3>
          <div className="llm-summary-box">
            {forecast.llm_summary.split('\n').map((line, idx) => (
              <span key={idx}>
                {line}
                <br />
              </span>
            ))}
          </div> */}
          <h3>Key Assumptions</h3>
          <ul className="assumptionsList">
            {forecast.assumptions.map((assumption, idx) => (
              <li key={idx}>{assumption}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default ForecastWorkers;
