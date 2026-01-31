import { useState } from 'react';
import axios from 'axios';
import './App.css';
import ProductCard from './components/ProductCard';
import Dashboard from './components/Dashboard';
import Comparison from './components/Comparison';
import FilterPanel from './components/FilterPanel';
import { BarChart3, GitCompare } from 'lucide-react';

// Configure axios base URL
axios.defaults.baseURL = 'http://localhost:8000';

function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Dashboard state
  const [showDashboard, setShowDashboard] = useState(false);

  // Comparison state
  const [selectedForComparison, setSelectedForComparison] = useState([]);
  const [showComparison, setShowComparison] = useState(false);

  // Filter state
  const [filterOpen, setFilterOpen] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [minSentiment, setMinSentiment] = useState(null);
  const [sortBy, setSortBy] = useState('relevance');

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResults(null);
    setSelectedForComparison([]);

    try {
      const params = { q: query };
      if (selectedCategory) params.category = selectedCategory;
      if (minSentiment !== null) params.min_sentiment = minSentiment;
      if (sortBy) params.sort_by = sortBy;

      const response = await axios.get(`/search`, { params });
      setResults(response.data);
    } catch (err) {
      console.error(err);
      setError('Failed to fetch recommendations. Ensure backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const toggleComparisonSelection = (productId) => {
    setSelectedForComparison(prev => {
      if (prev.includes(productId)) {
        return prev.filter(id => id !== productId);
      } else {
        if (prev.length >= 4) {
          alert('Maximum 4 products can be compared at once');
          return prev;
        }
        return [...prev, productId];
      }
    });
  };

  const handleCompare = () => {
    if (selectedForComparison.length < 2) {
      alert('Please select at least 2 products to compare');
      return;
    }
    setShowComparison(true);
  };

  const clearFilters = () => {
    setSelectedCategory(null);
    setMinSentiment(null);
    setSortBy('relevance');
  };

  return (
    <div className="app-container">
      <header className="hero-section">
        <h1 className="title">
          Aspect<span className="gradient-text">Mind</span>
        </h1>
        <p className="subtitle">Discover products by what truly matters to you.</p>

        <form onSubmit={handleSearch} className="search-box glass-panel">
          <input
            type="text"
            className="input-field-transparent"
            placeholder="e.g., 'tasty milk but cool design'"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button type="submit" className="btn-search" disabled={loading}>
            {loading ? 'Analyzing...' : 'Search'}
          </button>
        </form>

        {/* Action Buttons */}
        <div className="action-buttons">
          <button className="btn-action btn-dashboard" onClick={() => setShowDashboard(true)}>
            <BarChart3 size={20} />
            <span>Analytics Dashboard</span>
          </button>

          {selectedForComparison.length > 0 && (
            <button
              className="btn-action btn-compare"
              onClick={handleCompare}
            >
              <GitCompare size={20} />
              <span>Compare ({selectedForComparison.length})</span>
            </button>
          )}
        </div>
      </header>

      {/* Filter Panel */}
      {results && (
        <FilterPanel
          categories={results.available_categories || []}
          selectedCategory={selectedCategory}
          onCategoryChange={setSelectedCategory}
          minSentiment={minSentiment}
          onMinSentimentChange={setMinSentiment}
          sortBy={sortBy}
          onSortByChange={setSortBy}
          onClearFilters={clearFilters}
          isOpen={filterOpen}
          onToggle={() => setFilterOpen(!filterOpen)}
        />
      )}

      <main className="results-section">
        {error && <div className="error-message glass-panel">{error}</div>}

        {results && (
          <div className="analysis-summary animate-fade-in">
            <div className="summary-card glass-panel">
              <h3>Your Query Analysis</h3>
              <div className="aspect-chips">
                {Object.entries(results.query_analysis).map(([aspect, data]) => (
                  <span key={aspect} className={`chip ${data.polarity}`}>
                    {aspect}: {data.sentiment} ({data.confidence})
                  </span>
                ))}
                {Object.keys(results.query_analysis).length === 0 && (
                  <span className="chip neutral">No specific aspects detected</span>
                )}
              </div>
              <div className="overall-sentiment">
                Overall Sentiment: <span className={results.overall_sentiment.label.toLowerCase()}>{results.overall_sentiment.label}</span>
              </div>
            </div>
          </div>
        )}

        <div className="products-grid">
          {results?.results.map((item, index) => (
            <ProductCard
              key={index}
              product={item}
              rawRecs={results.raw_recs[index]}
              isSelected={selectedForComparison.includes(results.raw_recs[index].id)}
              onToggleCompare={() => toggleComparisonSelection(results.raw_recs[index].id)}
            />
          ))}
        </div>
      </main>

      {/* Dashboard Modal */}
      {showDashboard && (
        <Dashboard onClose={() => setShowDashboard(false)} />
      )}

      {/* Comparison Modal */}
      {showComparison && (
        <Comparison
          productIds={selectedForComparison}
          onClose={() => setShowComparison(false)}
        />
      )}
    </div>
  );
}

export default App;

