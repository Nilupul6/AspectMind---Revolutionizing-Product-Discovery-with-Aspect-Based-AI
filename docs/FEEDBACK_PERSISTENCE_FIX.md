# Feedback Persistence Fix

## Problem
When users submitted feedback for products, the changes were being applied in memory but not saved to disk. This meant that when the server restarted, all feedback updates were lost.

## Root Cause
The `add_feedback()` method in `recommender.py` was only updating the in-memory dataframes (`self.unique_df` and `self.df`) but never persisting these changes to:
1. The pickle cache file (`Second_fixed_image_urls.csv_processed.pkl`)
2. The original CSV file (`Second_fixed_image_urls.csv`)

## Solution Implemented

### 1. **Persist to Cache File**
Added code to save the updated dataframe to the pickle cache file using `_save_data_cache()`. This ensures that the next time the server starts, it loads the updated data from cache.

```python
# Save to cache file for persistence
try:
    self._save_data_cache(self.df)
    print(f"✅ Feedback persisted to cache for product: {product_id}")
except Exception as e:
    print(f"⚠️ Failed to save cache after feedback: {e}")
```

### 2. **Persist to CSV File**
Added code to also update the original CSV file as a backup. This involves:
- Ensuring the `item_unique_id` column exists in `df_original`
- Updating all matching rows with the new aspects
- Saving the CSV file

```python
# Also update the CSV file as backup
try:
    # Ensure item_unique_id exists in df_original
    if "item_unique_id" not in self.df_original.columns:
        # Create the column if it doesn't exist
        ...
    
    # Update the original dataframe
    csv_mask = self.df_original["item_unique_id"] == product_id
    if csv_mask.any():
        self.df_original.loc[csv_mask, "aspects_sentiments"] = json.dumps(current_aspects)
        self.df_original.to_csv(self.dataframe_path, index=False)
        print(f"✅ Feedback persisted to CSV for product: {product_id}")
except Exception as e:
    print(f"⚠️ Failed to save CSV after feedback: {e}")
```

### 3. **Consistent Display Format**
Updated the `compare_products()` method to show only:
- **Top 4 positive aspects** (strengths)
- **Top 2 negative aspects** (weaknesses)

This matches the format already used in the `recommend()` method.

## How It Works Now

1. **User submits feedback** → API receives feedback text
2. **ABSA analysis** → Extracts aspects and sentiments from feedback
3. **Update in-memory data** → Updates `self.unique_df` and `self.df`
4. **Save to cache** → Persists to `.pkl` file for fast loading
5. **Save to CSV** → Persists to original CSV as backup
6. **Return confirmation** → User sees updated aspects immediately

## Benefits

✅ **Persistent feedback** - Changes survive server restarts  
✅ **Dual persistence** - Both cache (fast) and CSV (reliable) are updated  
✅ **Consistent display** - All product views show top 4 strengths, top 2 weaknesses  
✅ **Error handling** - Graceful fallback if saving fails  
✅ **Logging** - Console messages confirm successful persistence  

## Testing

To test the fix:

1. Start the server
2. Submit feedback for a product
3. Verify the console shows:
   - `✅ Feedback persisted to cache for product: [product_id]`
   - `✅ Feedback persisted to CSV for product: [product_id]`
4. Restart the server
5. Search for the same product
6. Verify the feedback changes are still present

## Files Modified

- `server/recommender.py`:
  - `add_feedback()` method - Added persistence logic
  - `compare_products()` method - Limited to top 4 positive, top 2 negative
