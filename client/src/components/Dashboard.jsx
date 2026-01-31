import { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, Package, Tag, BarChart3 } from 'lucide-react';
import './Dashboard.css';

const COLORS = ['#10b981', '#ef4444', '#6b7280'];

export default function Dashboard({ onClose }) {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/analytics');
      setAnalytics(response.data);
    } catch (err) {
      console.error(err);
      setError('Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="dashboard-overlay">
        <div className="dashboard-modal glass-panel">
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Loading Analytics...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-overlay">
        <div className="dashboard-modal glass-panel">
          <div className="error-state">{error}</div>
          <button onClick={onClose} className="btn-close">Close</button>
        </div>
      </div>
    );
  }

  const sentimentData = [
    { name: 'Positive', value: analytics.sentiment_distribution.Positive, color: '#10b981' },
    { name: 'Negative', value: analytics.sentiment_distribution.Negative, color: '#ef4444' },
    { name: 'Neutral', value: analytics.sentiment_distribution.Neutral, color: '#6b7280' }
  ];

  return (
    <div className="dashboard-overlay" onClick={onClose}>
      <div className="dashboard-modal glass-panel" onClick={(e) => e.stopPropagation()}>
        <div className="dashboard-header">
          <h2>📊 Analytics Dashboard</h2>
          <button onClick={onClose} className="btn-close-x">✕</button>
        </div>

        {/* Stats Cards */}
        <div className="stats-grid">
          <div className="stat-card glass-panel">
            <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
              <Package size={24} />
            </div>
            <div className="stat-content">
              <h3>{analytics.total_products.toLocaleString()}</h3>
              <p>Total Products</p>
            </div>
          </div>

          <div className="stat-card glass-panel">
            <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' }}>
              <Tag size={24} />
            </div>
            <div className="stat-content">
              <h3>{analytics.total_aspects.toLocaleString()}</h3>
              <p>Unique Aspects</p>
            </div>
          </div>

          <div className="stat-card glass-panel">
            <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' }}>
              <TrendingUp size={24} />
            </div>
            <div className="stat-content">
              <h3>{analytics.dataset_info.total_reviews.toLocaleString()}</h3>
              <p>Total Reviews</p>
            </div>
          </div>

          <div className="stat-card glass-panel">
            <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)' }}>
              <BarChart3 size={24} />
            </div>
            <div className="stat-content">
              <h3>{analytics.top_categories.length}</h3>
              <p>Categories</p>
            </div>
          </div>
        </div>

        {/* Charts Section */}
        <div className="charts-grid">
          {/* Sentiment Distribution */}
          <div className="chart-card glass-panel">
            <h3>Sentiment Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={sentimentData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {sentimentData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Top Aspects */}
          <div className="chart-card glass-panel">
            <h3>Top 10 Aspects</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={analytics.top_aspects.slice(0, 10)}>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} stroke="#888" />
                <YAxis stroke="#888" />
                <Tooltip 
                  contentStyle={{ background: '#1a1a2e', border: '1px solid #333', borderRadius: '8px' }}
                />
                <Legend />
                <Bar dataKey="positive" stackId="a" fill="#10b981" name="Positive" />
                <Bar dataKey="negative" stackId="a" fill="#ef4444" name="Negative" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Top Categories */}
          <div className="chart-card glass-panel full-width">
            <h3>Top Categories by Product Count</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={analytics.top_categories.slice(0, 10)} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                <XAxis type="number" stroke="#888" />
                <YAxis dataKey="name" type="category" width={150} stroke="#888" />
                <Tooltip 
                  contentStyle={{ background: '#1a1a2e', border: '1px solid #333', borderRadius: '8px' }}
                />
                <Bar dataKey="count" fill="#667eea" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Aspect Details Table */}
        <div className="aspect-table-container glass-panel">
          <h3>Detailed Aspect Breakdown</h3>
          <div className="aspect-table-scroll">
            <table className="aspect-table">
              <thead>
                <tr>
                  <th>Aspect</th>
                  <th>Total</th>
                  <th>Positive</th>
                  <th>Negative</th>
                  <th>Neutral</th>
                  <th>Sentiment Ratio</th>
                </tr>
              </thead>
              <tbody>
                {analytics.top_aspects.slice(0, 15).map((aspect, idx) => {
                  const ratio = aspect.total > 0 
                    ? ((aspect.positive - aspect.negative) / aspect.total * 100).toFixed(1)
                    : 0;
                  return (
                    <tr key={idx}>
                      <td className="aspect-name">{aspect.name}</td>
                      <td>{aspect.total}</td>
                      <td className="positive-text">{aspect.positive}</td>
                      <td className="negative-text">{aspect.negative}</td>
                      <td className="neutral-text">{aspect.neutral}</td>
                      <td>
                        <span className={ratio > 0 ? 'positive-text' : ratio < 0 ? 'negative-text' : 'neutral-text'}>
                          {ratio}%
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
