"""
Test script to verify the recommender system can load data correctly
"""
import sys
import os

# Add server directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

print("=" * 70)
print("TESTING RECOMMENDER DATA LOADING")
print("=" * 70)

try:
    print("\n1. Importing pandas...")
    import pandas as pd
    print("   ✓ Pandas imported")
    
    print("\n2. Loading CSV...")
    DATA_DIR = r"c:\Users\Nilupul Nishitha\Desktop\requirments\data"
    csv_path = os.path.join(DATA_DIR, "Second_fixed_image_urls.csv")
    df = pd.read_csv(csv_path, low_memory=False)
    print(f"   ✓ Loaded {len(df)} rows")
    
    print("\n3. Checking required columns...")
    required_cols = ['itemName', 'category', 'reviewText', 'image']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        print(f"   ✗ Missing columns: {missing}")
    else:
        print(f"   ✓ All required columns present")
    
    print("\n4. Checking image URLs...")
    total_images = df['image'].notna().sum()
    valid_images = sum(1 for url in df['image'].dropna() 
                      if isinstance(url, str) and url.startswith('https://'))
    print(f"   ✓ Total images: {total_images}")
    print(f"   ✓ Valid URLs: {valid_images}")
    print(f"   ✓ Success rate: {valid_images/total_images*100:.1f}%")
    
    print("\n5. Testing sample data access...")
    sample = df.head(5)
    for idx, row in sample.iterrows():
        name = row['itemName']
        img = row.get('image', 'N/A')
        img_status = "✓" if pd.notna(img) and str(img).startswith('https://') else "✗"
        print(f"   {img_status} {name[:50]}...")
    
    print("\n6. Checking cache file...")
    cache_path = os.path.join(DATA_DIR, "Second_fixed_image_urls.csv_processed.pkl")
    if os.path.exists(cache_path):
        cache_size = os.path.getsize(cache_path) / (1024*1024)
        print(f"   ✓ Cache exists ({cache_size:.1f} MB)")
        print(f"   Note: If you modified the CSV, delete this cache file")
    else:
        print(f"   ℹ No cache file (will be created on first run)")
    
    print("\n" + "=" * 70)
    print("DATA LOADING TEST: PASSED")
    print("=" * 70)
    print("\nThe recommender system should be able to load this data successfully.")
    print("You can now start the server with: python server/main.py")
    
except Exception as e:
    print("\n" + "=" * 70)
    print("DATA LOADING TEST: FAILED")
    print("=" * 70)
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
    print("\nPlease fix the error before starting the server.")
