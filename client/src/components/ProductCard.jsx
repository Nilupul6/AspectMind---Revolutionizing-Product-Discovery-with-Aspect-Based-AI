import { useState, useEffect } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import { Tilt } from 'react-tilt';
import './ProductCard.css';

export default function ProductCard({ product, rawRecs, isSelected, onToggleCompare, onSelect, index = 0 }) {
    const [showFeedback, setShowFeedback] = useState(false);
    const [feedback, setFeedback] = useState('');
    const [submitting, setSubmitting] = useState(false);
    const [analyzing, setAnalyzing] = useState(false);
    const [message, setMessage] = useState(null);
    const [feedbackResult, setFeedbackResult] = useState(null);
    const [imageError, setImageError] = useState(false);
    const [imageLoading, setImageLoading] = useState(true);

    // Realtime Analysis Effect
    useEffect(() => {
        if (!feedback.trim()) {
            setFeedbackResult(null);
            return;
        }

        const timer = setTimeout(async () => {
            setAnalyzing(true);
            try {
                const res = await axios.post('/analyze', { text: feedback });
                setFeedbackResult(res.data);
            } catch (e) {
                console.error("Analysis failed", e);
            } finally {
                setAnalyzing(false);
            }
        }, 800); // 800ms debounce

        return () => clearTimeout(timer);
    }, [feedback]);

    // Improved fallback image logic - using base64 SVG (works offline)
    const PLACEHOLDER = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaWdodD0iMjAwIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxyZWN0IHdpZHRoPSIzMDAiIGhlaWdodD0iMjAwIiBmaWxsPSIjMWUyOTNiIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxNiIgZmlsbD0iIzY0NzQ4YiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPk5vIEltYWdlIEF2YWlsYWJsZTwvdGV4dD48L3N2Zz4=';

    const getImageUrl = () => {
        const img = rawRecs.image;

        // Check if image exists and is a valid URL
        if (!img ||
            img === 'nan' ||
            img === 'null' ||
            img === '' ||
            typeof img !== 'string' ||
            !img.startsWith('http')) {
            return PLACEHOLDER;
        }

        return img;
    };

    const imgUrl = getImageUrl();

    const handleFeedbackSubmit = async (e) => {
        e.preventDefault();
        if (!feedback.trim()) return;

        setSubmitting(true);
        setFeedbackResult(null);
        try {
            const res = await axios.post('/feedback', {
                product_id: rawRecs.id,
                feedback: feedback
            });

            setMessage({ type: 'success', text: res.data.message });
            setFeedback('');
            // Clear result after success
            setFeedbackResult(null);
            setTimeout(() => setShowFeedback(false), 2000);
        } catch (err) {
            setMessage({ type: 'error', text: 'Failed to submit feedback.' });
        } finally {
            setSubmitting(false);
            setTimeout(() => setMessage(null), 5000);
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
            onClick={() => onSelect && onSelect(rawRecs)} // Trigger selection on click
            style={{ cursor: 'pointer' }} // Add pointer cursor
        >
            <Tilt className={`product-card glass-panel ${isSelected ? 'selected-for-comparison' : ''}`} options={{ max: 15, scale: 1.02, speed: 400, glare: true, "max-glare": 0.5 }}>
                {/* Comparison Checkbox */}
                {onToggleCompare && (
                    <div className="comparison-checkbox-wrapper" onClick={(e) => e.stopPropagation()}>
                        <input
                            type="checkbox"
                            id={`compare-${rawRecs.id}`}
                            checked={isSelected}
                            onChange={(e) => { e.stopPropagation(); onToggleCompare(); }}
                            className="comparison-checkbox"
                        />
                        <label htmlFor={`compare-${rawRecs.id}`} className="comparison-label">
                            Compare
                        </label>
                    </div>
                )}

                <div className="product-image-container">
                    {imageLoading && !imageError && (
                        <div className="image-skeleton">
                            <div className="skeleton-shimmer"></div>
                        </div>
                    )}
                    <img
                        src={imgUrl}
                        alt={product.product}
                        className={`product-image ${imageLoading ? 'loading' : ''} ${imageError ? 'error' : ''}`}
                        onLoad={() => setImageLoading(false)}
                        onError={(e) => {
                            setImageError(true);
                            setImageLoading(false);
                            e.target.src = PLACEHOLDER;
                        }}
                    />
                    <div className="score-badge">
                        {(rawRecs.score * 100).toFixed(0)}% Match
                    </div>
                </div>

                <div className="product-content">
                    <h3 className="product-name">{product.product}</h3>
                    <p className="product-category">{rawRecs.category}</p>

                    {/* Match reason removed as per request to focus on finding Top Strengths */}

                    {/* Aspect Visualization */}
                    <div className="aspect-analysis-grid">
                        <div className="aspect-column">
                            <h4 className="column-title positive-text">Top Strengths</h4>
                            {product.top_pos_aspects?.length > 0 ? (
                                product.top_pos_aspects.map((a, i) => (
                                    <div key={i} className="aspect-row">
                                        <span className="aspect-name">{a.name}</span>
                                        <div className="aspect-score-track">
                                            <div className="aspect-score-fill positive-fill" style={{ width: `${a.score * 100}%` }}></div>
                                        </div>
                                    </div>
                                ))
                            ) : <div className="no-data">No major strengths detected</div>}
                        </div>

                        <div className="aspect-column">
                            <h4 className="column-title negative-text">Concerns</h4>
                            {product.top_neg_aspects?.length > 0 ? (
                                product.top_neg_aspects.map((a, i) => (
                                    <div key={i} className="aspect-row">
                                        <span className="aspect-name">{a.name}</span>
                                        <div className="aspect-score-track">
                                            <div className="aspect-score-fill negative-fill" style={{ width: `${a.score * 100}%` }}></div>
                                        </div>
                                    </div>
                                ))
                            ) : <div className="no-data">No major concerns</div>}
                        </div>
                    </div>

                    <button
                        className="btn-feedback"
                        onClick={(e) => { e.stopPropagation(); setShowFeedback(!showFeedback); }}
                    >
                        {showFeedback ? 'Close' : 'Give Feedback'}
                    </button>

                    {showFeedback && (
                        <form onSubmit={handleFeedbackSubmit} className="feedback-form" onClick={e => e.stopPropagation()}>
                            <textarea
                                className="feedback-input"
                                placeholder="e.g. The taste is great but packaging is weak."
                                value={feedback}
                                onChange={e => setFeedback(e.target.value)}
                            />
                            <div className="analysis-status">
                                {analyzing && <span className="status-text analyzing">Analyzing text...</span>}

                                {!analyzing && feedbackResult && Object.keys(feedbackResult).length > 0 && (
                                    <div className="live-analysis animate-fade-in">
                                        <span className="live-label">Detected:</span>
                                        <div className="detected-chips">
                                            {Object.entries(feedbackResult).map(([aspect, data]) => (
                                                <span key={aspect} className={`chip-sm ${data.sentiment.toLowerCase()}`}>
                                                    {aspect}: {data.sentiment}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>

                            <button type="submit" disabled={submitting || analyzing} className="btn-submit">
                                {submitting ? 'Submitting...' : 'Submit Opinion'}
                            </button>

                            {message && <div className={`msg ${message.type}`}>{message.text}</div>}
                        </form>
                    )}
                </div>
            </Tilt>
        </motion.div>
    );
}
