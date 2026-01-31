# Product Recommender System

An intelligent product recommendation system using advanced NLP and sentiment analysis.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 14+

### Installation

1. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

2. **Install client dependencies**
```bash
cd client
npm install
```

### Running the Application

1. **Start the backend server**
```bash
cd server
python main.py
```
Server will run on `http://localhost:8000`

2. **Start the frontend** (in a new terminal)
```bash
cd client
npm run dev
```
Client will run on `http://localhost:5173`

### Quick Health Check
```bash
python scripts/quick_check.py
```

## 📁 Project Structure

```
requirments/
├── client/              # React frontend application
├── server/              # FastAPI backend server
├── data/                # Dataset files
├── models/              # Pre-trained ML models
├── embeddings/          # Cached embeddings
├── scripts/             # Utility scripts
│   ├── quick_check.py           # Quick data health check
│   ├── diagnose_images.py       # Full diagnostic tool
│   ├── repair_images_fixed.py   # Image URL repair tool
│   └── test_data_loading.py     # Server compatibility test
├── docs/                # Documentation
├── archive/             # Old/debug files (safe to ignore)
├── start_app.bat        # Windows quick start script
└── README.md            # This file
```

## 🛠️ Key Features

- **Semantic Search**: Find products using natural language queries
- **Sentiment Analysis**: Aspect-based sentiment analysis of reviews
- **Smart Recommendations**: AI-powered product suggestions
- **Product Comparison**: Side-by-side product comparison
- **Analytics Dashboard**: Insights and statistics
- **Category Filtering**: Filter by product categories
- **Sentiment Filtering**: Filter by sentiment scores

## 📚 Documentation

- **[Quick Start Guide](docs/QUICK_START.md)** - Get started quickly
- **[Features](docs/FEATURES_IMPLEMENTED.md)** - Detailed feature list
- **[Image Fix Guide](docs/README_IMAGE_FIX.md)** - Image URL troubleshooting

## 🔧 Maintenance Scripts

### Check Data Health
```bash
python scripts/quick_check.py
```

### Run Full Diagnostic
```bash
python scripts/diagnose_images.py
```

### Repair Image URLs (if needed)
```bash
python scripts/repair_images_fixed.py
```

### Test Server Compatibility
```bash
python scripts/test_data_loading.py
```

## 🏗️ Technology Stack

### Backend
- **FastAPI** - Modern web framework
- **PyTorch** - Deep learning framework
- **Transformers** - NLP models
- **Sentence-BERT** - Semantic embeddings
- **spaCy** - NLP processing

### Frontend
- **React** - UI framework
- **Vite** - Build tool
- **Recharts** - Data visualization
- **Lucide React** - Icons

### ML Models
- **all-MiniLM-L6-v2** - Semantic search
- **ms-marco-MiniLM-L-6-v2** - Cross-encoder reranking
- **deberta-v3-base-absa** - Aspect-based sentiment analysis

## 📊 Data

- **Dataset**: Amazon product reviews
- **Size**: 134,520 products
- **Valid Images**: 110,330 (82%)
- **Location**: `data/Second_fixed_image_urls.csv`

## ⚠️ Important Notes

- Always run `scripts/quick_check.py` before starting the server
- Delete cache file (`data/*.pkl`) after modifying CSV files
- Keep backups before running repair scripts
- See `docs/` folder for detailed documentation

## 🐛 Troubleshooting

### Server won't start?
1. Check Python version: `python --version`
2. Verify dependencies: `pip install -r requirements.txt`
3. Check data health: `python scripts/quick_check.py`

### Images not loading?
1. Run diagnostic: `python scripts/diagnose_images.py`
2. Repair if needed: `python scripts/repair_images_fixed.py`
3. Clear cache and restart server

### Frontend issues?
1. Clear browser cache
2. Check console for errors
3. Verify backend is running on port 8000

## 📝 License

This project is for educational purposes.

## 🤝 Contributing

This is a personal project. For issues or suggestions, please document them in the `docs/` folder.

---

**Status**: ✅ Production Ready
**Last Updated**: 2026-01-30
**Version**: 1.0.0
