import { Filter as FilterIcon, X } from 'lucide-react';
import './FilterPanel.css';

export default function FilterPanel({
    categories,
    selectedCategory,
    onCategoryChange,
    minSentiment,
    onMinSentimentChange,
    sortBy,
    onSortByChange,
    onClearFilters,
    isOpen,
    onToggle
}) {
    const hasActiveFilters = selectedCategory || minSentiment !== null || sortBy !== 'relevance';

    return (
        <>
            {/* Filter Toggle Button */}
            <button
                className={`filter-toggle-btn ${isOpen ? 'active' : ''} ${hasActiveFilters ? 'has-filters' : ''}`}
                onClick={onToggle}
            >
                <FilterIcon size={20} />
                <span>Filters</span>
                {hasActiveFilters && <span className="filter-badge">●</span>}
            </button>

            {/* Filter Panel */}
            <div className={`filter-panel glass-panel ${isOpen ? 'open' : ''}`}>
                <div className="filter-header">
                    <h3>🎯 Filters & Sorting</h3>
                    <button className="btn-close-filter" onClick={onToggle}>
                        <X size={20} />
                    </button>
                </div>

                <div className="filter-content">
                    {/* Category Filter */}
                    <div className="filter-group">
                        <label className="filter-label">
                            <span className="label-icon">📦</span>
                            Category
                        </label>
                        <select
                            value={selectedCategory || ''}
                            onChange={(e) => onCategoryChange(e.target.value || null)}
                            className="filter-select"
                        >
                            <option value="">All Categories</option>
                            {categories.map((cat, idx) => (
                                <option key={idx} value={cat}>{cat}</option>
                            ))}
                        </select>
                    </div>

                    {/* Sentiment Filter */}
                    <div className="filter-group">
                        <label className="filter-label">
                            <span className="label-icon">😊</span>
                            Minimum Sentiment Score
                        </label>
                        <div className="sentiment-slider-container">
                            <input
                                type="range"
                                min="-1"
                                max="1"
                                step="0.1"
                                value={minSentiment === null ? -1 : minSentiment}
                                onChange={(e) => {
                                    const val = parseFloat(e.target.value);
                                    onMinSentimentChange(val === -1 ? null : val);
                                }}
                                className="sentiment-slider"
                            />
                            <div className="slider-labels">
                                <span className="negative-text">Negative</span>
                                <span className="neutral-text">Neutral</span>
                                <span className="positive-text">Positive</span>
                            </div>
                            <div className="slider-value">
                                {minSentiment === null ? 'No Filter' : minSentiment.toFixed(1)}
                            </div>
                        </div>
                    </div>

                    {/* Sort By */}
                    <div className="filter-group">
                        <label className="filter-label">
                            <span className="label-icon">🔄</span>
                            Sort By
                        </label>
                        <div className="sort-options">
                            <button
                                className={`sort-btn ${sortBy === 'relevance' ? 'active' : ''}`}
                                onClick={() => onSortByChange('relevance')}
                            >
                                Relevance
                            </button>
                            <button
                                className={`sort-btn ${sortBy === 'sentiment' ? 'active' : ''}`}
                                onClick={() => onSortByChange('sentiment')}
                            >
                                Sentiment
                            </button>
                            <button
                                className={`sort-btn ${sortBy === 'name' ? 'active' : ''}`}
                                onClick={() => onSortByChange('name')}
                            >
                                Name
                            </button>
                        </div>
                    </div>

                    {/* Clear Filters */}
                    {hasActiveFilters && (
                        <button className="btn-clear-filters" onClick={onClearFilters}>
                            <X size={16} />
                            Clear All Filters
                        </button>
                    )}
                </div>
            </div>

            {/* Overlay */}
            {isOpen && <div className="filter-overlay" onClick={onToggle}></div>}
        </>
    );
}
