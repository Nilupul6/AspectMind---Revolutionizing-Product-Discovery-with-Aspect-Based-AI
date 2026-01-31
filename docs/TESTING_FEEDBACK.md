# Testing Guide: Feedback Persistence

## Quick Test Steps

### Test 1: Verify Feedback Persistence

1. **Start the server**
   ```bash
   cd server
   python main.py
   ```

2. **Search for a product**
   - Open the client application
   - Search for any product (e.g., "laptop")
   - Note the current strengths and weaknesses displayed

3. **Submit feedback**
   - Click on a product
   - Submit feedback like: "The battery life is excellent but the screen quality is poor"
   - You should see the feedback analysis appear

4. **Check server console**
   - Look for these messages:
     ```
     ✅ Feedback persisted to cache for product: [product_id]
     ✅ Feedback persisted to CSV for product: [product_id]
     ```

5. **Restart the server**
   - Stop the server (Ctrl+C)
   - Start it again: `python main.py`

6. **Verify persistence**
   - Search for the same product again
   - The feedback you submitted should still be visible
   - The new aspects should appear in the strengths/weaknesses

### Test 2: Verify Display Format

1. **Check product cards**
   - Each product should show:
     - **Maximum 4 strengths** (positive aspects)
     - **Maximum 2 weaknesses** (negative aspects)
   - If a product has fewer aspects, it's fine to show less

2. **Check comparison view**
   - Compare multiple products
   - Each product should show:
     - Top 4 positive aspects
     - Top 2 negative aspects

## Expected Behavior

### ✅ What Should Work

- Feedback is saved immediately
- Server restart preserves feedback
- Products show up to 4 strengths
- Products show up to 2 weaknesses
- Console shows confirmation messages
- Both cache (.pkl) and CSV files are updated

### ❌ What to Watch For

- If you see "⚠️ Failed to save cache" - check file permissions
- If you see "⚠️ Failed to save CSV" - check if CSV file is open in Excel
- If feedback disappears after restart - check the error messages in console

## Troubleshooting

### Problem: Feedback not persisting

**Check:**
1. Server console for error messages
2. File permissions on `data/` and `embeddings/` folders
3. Whether CSV file is locked by another program

**Solution:**
- Close any programs that might have the CSV file open
- Ensure write permissions on the data directory

### Problem: More than 4 strengths showing

**Check:**
- Frontend code might not be limiting the display
- Verify the API response has `top_pos_aspects` with max 4 items

**Solution:**
- The backend now limits to 4, but frontend should also respect this

### Problem: Feedback not analyzing correctly

**Check:**
- The feedback text should be descriptive
- Example good feedback: "Great battery life, poor screen quality"
- Example bad feedback: "good" (too vague)

## API Endpoints to Test

### POST /feedback
```json
{
  "product_id": "Samsung Galaxy...",
  "feedback": "Excellent camera quality but battery drains quickly"
}
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "Feedback analyzed and product updated.",
  "feedback_analysis": {
    "camera quality": {
      "sentiment": "Positive",
      "confidence": 0.95
    },
    "battery": {
      "sentiment": "Negative",
      "confidence": 0.87
    }
  }
}
```

### GET /search?q=laptop
**Check the response:**
- Each product in `results` should have:
  - `top_pos_aspects`: array with max 4 items
  - `top_neg_aspects`: array with max 2 items

### POST /compare
```json
{
  "product_ids": ["product1_id", "product2_id"]
}
```

**Check the response:**
- Each product should have:
  - `positive_aspects`: max 4 items
  - `negative_aspects`: max 2 items
