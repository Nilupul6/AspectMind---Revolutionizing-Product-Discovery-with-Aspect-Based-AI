# 🚀 Quick Start Guide - AspectMind Enhanced

## Prerequisites
- Python 3.8+ installed
- Node.js 16+ installed
- All models downloaded (run `python setup_offline.py` if needed)

## Starting the Application

### Option 1: Using the Batch File (Windows)
```bash
# Simply double-click or run:
start_app.bat
```

### Option 2: Manual Start

#### 1. Start Backend Server
```bash
cd server
python main.py
```
Wait for the message: "✅ Model loaded successfully!"

#### 2. Start Frontend (New Terminal)
```bash
cd client
npm run dev
```

#### 3. Open Browser
Navigate to: `http://localhost:5173` (or the URL shown in terminal)

---

## 🎯 Testing the New Features

### 1. Test Analytics Dashboard 📊
1. Click the **"Analytics Dashboard"** button on the homepage
2. Explore the charts:
   - Sentiment Distribution (Pie Chart)
   - Top Aspects (Bar Chart)
   - Category Statistics (Horizontal Bar Chart)
3. Scroll through the detailed aspect breakdown table
4. Close the dashboard

### 2. Test Comparison Mode ⚖️
1. Search for products (e.g., "tasty milk")
2. Check the **"Compare"** checkbox on 2-4 products
3. Click the **"Compare (N)"** button that appears
4. View the comparison:
   - Product overview cards
   - Aspect comparison matrix
   - Top strengths visualization
   - Winner summary
5. Close the comparison modal

### 3. Test Filtering & Sorting 🔍
1. Search for products
2. Click the **"Filters"** button (top right corner)
3. Try different filters:
   - **Category**: Select a category from dropdown
   - **Sentiment Slider**: Drag to set minimum sentiment
   - **Sort By**: Choose Relevance, Sentiment, or Name
4. Perform a new search to see filtered results
5. Click **"Clear All Filters"** to reset

---

## 🎨 Feature Highlights

### Analytics Dashboard
- **Real-time Metrics**: Total products, aspects, reviews, categories
- **Interactive Charts**: Hover over charts for detailed information
- **Responsive Design**: Works on all screen sizes
- **Glassmorphism UI**: Modern frosted glass effect

### Comparison Mode
- **Visual Indicators**: ✓ (Positive), ✗ (Negative), — (Neutral)
- **Confidence Scores**: Percentage confidence for each aspect
- **Winner Detection**: Automatically highlights best product
- **Strength Bars**: Visual representation of positive aspects

### Enhanced Filtering
- **Category Filter**: Filter by product category
- **Sentiment Range**: -1.0 (Negative) to 1.0 (Positive)
- **Multiple Sort Options**: Relevance, Sentiment, Name
- **Active Filter Badge**: Shows when filters are applied

---

## 📝 Example Searches to Try

1. **"tasty milk but cool design"**
   - Tests aspect detection and matching
   - Good for comparison (multiple milk products)

2. **"comfortable shoes"**
   - Filter by category: "Shoes" or "Footwear"
   - Sort by sentiment to see best-rated

3. **"durable phone"**
   - Use sentiment slider to filter high-quality products
   - Compare top 3 results

---

## 🐛 Troubleshooting

### Backend Issues
- **Models not loading**: Run `python setup_offline.py` first
- **Port 8000 in use**: Change port in `main.py`
- **Memory errors**: Reduce `max_dataset_size` in recommender.py

### Frontend Issues
- **Port 5173 in use**: Vite will auto-increment to 5174
- **Dependencies missing**: Run `npm install`
- **Charts not showing**: Verify recharts is installed

### Common Errors
- **"Failed to fetch recommendations"**: Backend not running
- **"Model is still loading"**: Wait for backend to fully initialize
- **Empty analytics**: Dataset needs to be processed first

---

## 🎯 API Endpoints

### Existing Endpoints
- `GET /` - Health check
- `GET /search?q=query&category=&min_sentiment=&sort_by=` - Search with filters
- `POST /analyze` - Analyze text for aspects
- `POST /feedback` - Submit product feedback

### New Endpoints
- `GET /analytics` - Get dashboard analytics data
- `POST /compare` - Compare multiple products
  ```json
  {
    "product_ids": ["id1", "id2", "id3"]
  }
  ```

---

## 💡 Tips for Best Experience

1. **First Search**: May take longer as models initialize
2. **Comparison**: Select products with similar categories for better insights
3. **Filters**: Combine category + sentiment for precise results
4. **Analytics**: Refresh periodically to see updated stats
5. **Mobile**: Use landscape mode for better chart visibility

---

## 🎉 Enjoy Your Enhanced AspectMind!

You now have a powerful product recommendation system with:
- ✅ Comprehensive analytics dashboard
- ✅ Intelligent product comparison
- ✅ Advanced filtering and sorting
- ✅ Beautiful, modern UI
- ✅ Enterprise-ready features

Happy searching! 🚀
