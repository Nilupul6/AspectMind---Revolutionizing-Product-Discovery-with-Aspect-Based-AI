import { useState, useEffect } from 'react';
import axios from 'axios';
import { X, CheckCircle, XCircle, MinusCircle } from 'lucide-react';
import './Comparison.css';

export default function Comparison({ productIds, onClose }) {
    // Offline SVG placeholder (works without network)
    const PLACEHOLDER = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iIzFlMjkzYiIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwsIHNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iMTYiIGZpbGw9IiM2NDc0OGIiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5ObyBJbWFnZSBBdmFpbGFibGU8L3RleHQ+PC9zdmc+';

    const [comparison, setComparison] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchComparison();
    }, [productIds]);

    const fetchComparison = async () => {
        setLoading(true);
        try {
            const response = await axios.post('/compare', { product_ids: productIds });
            setComparison(response.data);
        } catch (err) {
            console.error(err);
            setError('Failed to load comparison data');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="comparison-overlay">
                <div className="comparison-modal glass-panel">
                    <div className="loading-state">
                        <div className="spinner"></div>
                        <p>Comparing Products...</p>
                    </div>
                </div>
            </div>
        );
    }

    if (error || comparison?.error) {
        return (
            <div className="comparison-overlay">
                <div className="comparison-modal glass-panel">
                    <div className="error-state">{error || comparison.error}</div>
                    <button onClick={onClose} className="btn-close">Close</button>
                </div>
            </div>
        );
    }

    const getSentimentIcon = (sentiment) => {
        if (sentiment === 'Positive') return <CheckCircle size={18} className="icon-positive" />;
        if (sentiment === 'Negative') return <XCircle size={18} className="icon-negative" />;
        if (sentiment === 'Neutral') return <MinusCircle size={18} className="icon-neutral" />;
        return <span className="icon-na">—</span>;
    };

    const getSentimentClass = (sentiment) => {
        if (sentiment === 'Positive') return 'sentiment-positive';
        if (sentiment === 'Negative') return 'sentiment-negative';
        if (sentiment === 'Neutral') return 'sentiment-neutral';
        return 'sentiment-na';
    };

    return (
        <div className="comparison-overlay" onClick={onClose}>
            <div className="comparison-modal glass-panel" onClick={(e) => e.stopPropagation()}>
                <div className="comparison-header">
                    <h2>⚖️ Product Comparison</h2>
                    <button onClick={onClose} className="btn-close-x">✕</button>
                </div>

                {/* Product Overview Cards */}
                <div className="products-overview">
                    {comparison.products.map((product, idx) => (
                        <div key={idx} className="product-overview-card glass-panel">
                            <div className="product-image-wrapper">
                                <img
                                    src={product.image || PLACEHOLDER}
                                    alt={product.name}
                                    onError={(e) => e.target.src = PLACEHOLDER}
                                />
                            </div>
                            <h3>{product.name}</h3>
                            <p className="product-category">{product.category}</p>
                            <div className="product-stats">
                                <div className="stat">
                                    <span className="stat-value positive-text">{product.positive_count}</span>
                                    <span className="stat-label">Strengths</span>
                                </div>
                                <div className="stat">
                                    <span className="stat-value negative-text">{product.negative_count}</span>
                                    <span className="stat-label">Concerns</span>
                                </div>
                                <div className="stat">
                                    <span className="stat-value">{product.total_aspects}</span>
                                    <span className="stat-label">Total Aspects</span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Aspect Comparison Matrix */}
                <div className="comparison-matrix-container">
                    <h3>Detailed Aspect Comparison</h3>
                    <div className="matrix-scroll">
                        <table className="comparison-matrix">
                            <thead>
                                <tr>
                                    <th className="aspect-header">Aspect</th>
                                    {comparison.products.map((product, idx) => (
                                        <th key={idx} className="product-header">
                                            <div className="product-header-content">
                                                <span className="product-number">#{idx + 1}</span>
                                                <span className="product-name-short">{product.name.substring(0, 30)}{product.name.length > 30 ? '...' : ''}</span>
                                            </div>
                                        </th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {comparison.aspect_matrix.map((row, idx) => (
                                    <tr key={idx}>
                                        <td className="aspect-cell">{row.aspect}</td>
                                        {comparison.products.map((_, productIdx) => {
                                            const data = row[`product_${productIdx}`];
                                            return (
                                                <td key={productIdx} className={`sentiment-cell ${getSentimentClass(data.sentiment)}`}>
                                                    <div className="sentiment-content">
                                                        {getSentimentIcon(data.sentiment)}
                                                        <span className="sentiment-label">{data.sentiment}</span>
                                                        {data.confidence > 0 && (
                                                            <span className="confidence-badge">{(data.confidence * 100).toFixed(0)}%</span>
                                                        )}
                                                    </div>
                                                </td>
                                            );
                                        })}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Top Strengths Comparison */}
                <div className="strengths-comparison">
                    <h3>Top Strengths Comparison</h3>
                    <div className="strengths-grid">
                        {comparison.products.map((product, idx) => (
                            <div key={idx} className="strength-column glass-panel">
                                <h4>#{idx + 1} {product.name.substring(0, 25)}{product.name.length > 25 ? '...' : ''}</h4>
                                <div className="strength-list">
                                    {product.positive_aspects.slice(0, 5).map((aspect, i) => (
                                        <div key={i} className="strength-item">
                                            <span className="strength-name">{aspect.name}</span>
                                            <div className="strength-bar">
                                                <div
                                                    className="strength-fill"
                                                    style={{ width: `${aspect.score * 100}%` }}
                                                ></div>
                                            </div>
                                            <span className="strength-score">{(aspect.score * 100).toFixed(0)}%</span>
                                        </div>
                                    ))}
                                    {product.positive_aspects.length === 0 && (
                                        <p className="no-data">No positive aspects detected</p>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Winner Summary */}
                <div className="winner-summary glass-panel">
                    <h3>🏆 Quick Summary</h3>
                    <div className="winner-grid">
                        {comparison.products.map((product, idx) => {
                            const score = product.positive_count - product.negative_count;
                            const isWinner = score === Math.max(...comparison.products.map(p => p.positive_count - p.negative_count));
                            return (
                                <div key={idx} className={`winner-card ${isWinner ? 'winner' : ''}`}>
                                    {isWinner && <span className="winner-badge">🏆 Best Overall</span>}
                                    <h4>{product.name}</h4>
                                    <div className="winner-stats">
                                        <div className="winner-stat">
                                            <span className="label">Net Score:</span>
                                            <span className={`value ${score > 0 ? 'positive-text' : score < 0 ? 'negative-text' : ''}`}>
                                                {score > 0 ? '+' : ''}{score}
                                            </span>
                                        </div>
                                        <div className="winner-stat">
                                            <span className="label">Positive Ratio:</span>
                                            <span className="value">
                                                {product.total_aspects > 0
                                                    ? ((product.positive_count / product.total_aspects) * 100).toFixed(0)
                                                    : 0}%
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>
        </div>
    );
}
