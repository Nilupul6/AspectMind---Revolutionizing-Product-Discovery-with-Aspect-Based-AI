import pandas as pd
import re

CSV_PATH = r"c:\Users\Nilupul Nishitha\Desktop\requirments\data\Second_fixed_image_urls.csv"
BACKUP_PATH = r"c:\Users\Nilupul Nishitha\Desktop\requirments\data\Second_fixed_image_urls_backup_ames.csv"

print("=" * 80)
print("FIXING AMES COMPANIES PRODUCT IMAGE")
print("=" * 80)

# Load data
print("\n1. Loading CSV...")
df = pd.read_csv(CSV_PATH, low_memory=False)
print(f"   Loaded {len(df)} rows")

# Find the product
print("\n2. Searching for AMES COMPANIES product...")
mask = df['itemName'].str.contains('AMES COMPANIES', case=False, na=False)
matches = df[mask]

if len(matches) == 0:
    print("   ✗ Product not found!")
    exit(1)

print(f"   ✓ Found {len(matches)} match(es)")

# Create backup
print("\n3. Creating backup...")
import shutil
shutil.copy2(CSV_PATH, BACKUP_PATH)
print(f"   ✓ Backup created: {BACKUP_PATH}")

# Show current state
print("\n4. Current state:")
for idx, row in matches.iterrows():
    print(f"   Row {idx}: {row['itemName'][:60]}...")
    print(f"   Current image: {row.get('image', 'N/A')}")
    
    # Try to find a valid image URL
    # Option 1: Check description field
    desc = str(row.get('description', ''))
    img_from_desc = None
    if desc and desc != 'nan':
        # Try to extract URL from description
        url_match = re.search(r'https?://[^\s<>"]+\.(?:jpg|jpeg|png)', desc, re.IGNORECASE)
        if url_match:
            img_from_desc = url_match.group(0)
            print(f"   Found URL in description: {img_from_desc}")
    
    # Option 2: Use a placeholder or default Amazon image pattern
    # For this product, let's try to construct a generic Amazon image URL
    # or use a placeholder
    
    if img_from_desc:
        print(f"\n5. Fixing with URL from description...")
        df.at[idx, 'image'] = img_from_desc
        print(f"   ✓ Updated row {idx}")
    else:
        # Use a placeholder image or mark for manual review
        print(f"\n5. No valid URL found in description")
        print(f"   Options:")
        print(f"   a) Use placeholder: https://via.placeholder.com/300x300?text=No+Image")
        print(f"   b) Leave as is and handle in frontend")
        print(f"   c) Manually find the correct image URL")
        
        # For now, let's use a placeholder
        placeholder = "https://via.placeholder.com/300x300?text=No+Image+Available"
        df.at[idx, 'image'] = placeholder
        print(f"\n   Using placeholder image")

# Save
print("\n6. Saving changes...")
df.to_csv(CSV_PATH, index=False)
print(f"   ✓ Saved to {CSV_PATH}")

# Clear cache
import os
cache_path = CSV_PATH.replace('.csv', '.csv_processed.pkl')
if os.path.exists(cache_path):
    print("\n7. Clearing cache...")
    os.remove(cache_path)
    print(f"   ✓ Removed {cache_path}")

print("\n" + "=" * 80)
print("FIX COMPLETE!")
print("=" * 80)
print("\nNext steps:")
print("1. Restart the server")
print("2. Test the product search")
print("3. If still flashing, check browser console for errors")
