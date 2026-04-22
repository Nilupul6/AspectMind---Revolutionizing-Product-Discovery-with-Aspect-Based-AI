import { useEffect } from 'react';
import { motion } from 'framer-motion';
import { X, Check, FileText, Zap, BarChart2 } from 'lucide-react';
import './ProductModal.css';

export default function ProductModal({ data, onClose }) {
    // Lock body scroll when modal is open
    useEffect(() => {
        document.body.style.overflow = 'hidden';
        return () => {
            document.body.style.overflow = 'auto';
        };
    }, []);

    if (!data) return null;

    // Safe parsing for features (assuming they might be pipe or comma separated strings, or just text)
    const getFeatures = (text) => {
        if (!text || text === 'nan') return [];
        if (text.includes('|')) return text.split('|').filter(f => f.trim().length > 0);
        // If it's a long text with no obvious delimiters, just return it as one item or split by sentence
        if (text.length > 50 && text.includes('.')) return text.split('.').filter(f => f.trim().length > 5);
        return [text];
    };

    const features = getFeatures(data.feature);

    // Prepare aspects for grid
    const aspectsList = Object.entries(data.aspects || {}).map(([key, val]) => ({
        name: key,
        sentiment: val.sentiment,
        confidence: val.confidence
    })).sort((a, b) => b.confidence - a.confidence); // Sort by confidence

    // Image Fallback
    const PLACEHOLDER = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaWdodD0iMjAwIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxyZWN0IHdpZHRoPSIzMDAiIGhlaWdodD0iMjAwIiBmaWxsPSIjMWUyOTNiIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxNiIgZmlsbD0iIzY0NzQ4YiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPk5vIEltYWdlIEF2YWlsYWJsZTwvdGV4dD48L3N2Zz4=';
    const imgUrl = (data.image && data.image !== 'nan' && data.image.startsWith('http')) ? data.image : PLACEHOLDER;

    return (
        <div className="modal-overlay" onClick={onClose}>
            <motion.div
                className="product-modal glass-panel"
                initial={{ opacity: 0, scale: 0.9, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.9, y: 20 }}
                transition={{ type: "spring", stiffness: 300, damping: 25 }}
                onClick={(e) => e.stopPropagation()} // Prevent close on modal click
            >
                <button className="modal-close-btn" onClick={onClose}>
                    <X size={20} />
                </button>

                <div className="modal-header">
                    <div className="modal-image-container">
                        <img src={imgUrl} alt={data.name} className="modal-image" />
                    </div>
                    <div className="modal-title-section">
                        <div className="modal-category">{data.category}</div>
                        <h2 className="modal-title">{data.name}</h2>
                        <div className="modal-score">
                            <Zap size={16} fill="currentColor" />
                            <span>{(data.score * 100).toFixed(0)}% Match Score</span>
                        </div>
                    </div>
                </div>

                <div className="modal-body">
                    {/* Description */}
                    {data.description && data.description !== 'nan' && (
                        <div className="modal-section">
                            <h3 className="modal-section-title"><FileText size={18} /> Description</h3>
                            <div
                                className="modal-description"
                                dangerouslySetInnerHTML={{ __html: data.description }}
                            />
                        </div>
                    )}

                    {/* Features */}
                    {features.length > 0 && (
                        <div className="modal-section">
                            <h3 className="modal-section-title"><Check size={18} /> Key Features</h3>
                            <ul className="modal-features-list">
                                {features.map((feat, i) => (
                                    <li key={i} className="modal-feature-item">
                                        <span className="feature-bullet">•</span>
                                        {feat}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {/* Sentiment Analysis Grid */}
                    <div className="modal-section">
                        <h3 className="modal-section-title"><BarChart2 size={18} /> Aspect Analysis</h3>
                        <div className="sentiment-grid">
                            {aspectsList.length > 0 ? aspectsList.map((aspect, i) => (
                                <div key={i} className={`sentiment-card ${aspect.sentiment.toLowerCase()}`}>
                                    <span className="sentiment-aspect">{aspect.name}</span>
                                    <span className={`sentiment-label ${aspect.sentiment === 'Positive' ? 'pos' : aspect.sentiment === 'Negative' ? 'neg' : 'neu'}`}>
                                        {aspect.sentiment}
                                    </span>
                                    <span className="sentiment-conf">{(aspect.confidence * 100).toFixed(0)}% Conf.</span>
                                </div>
                            )) : (
                                <div className="no-data">No aspect details available.</div>
                            )}
                        </div>
                    </div>
                </div>
            </motion.div>
        </div>
    );
}
