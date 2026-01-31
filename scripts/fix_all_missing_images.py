import pandas as pd
import os

CSV_PATH = r"c:\Users\Nilupul Nishitha\Desktop\requirments\data\Second_fixed_image_urls.csv"
BACKUP_PATH = r"c:\Users\Nilupul Nishitha\Desktop\requirments\data\Second_fixed_image_urls_backup_bulk.csv"
CACHE_PATH = r"c:\Users\Nilupul Nishitha\Desktop\requirments\data\Second_fixed_image_urls.csv_processed.pkl"

print("=" * 80)
print("BULK FIX FOR MISSING IMAGES")
print("=" * 80)

# Load data
print("\n1. Loading CSV...")
df = pd.read_csv(CSV_PATH, low_memory=False)
print(f"   Total rows: {len(df)}")

# Count missing images
print("\n2. Analyzing missing images...")
missing_mask = df['image'].isna() | (df['image'].astype(str).str.lower() == 'nan') | (df['image'].astype(str).str.strip() == '')
missing_count = missing_mask.sum()
print(f"   Missing images: {missing_count} ({missing_count/len(df)*100:.1f}%)")

if missing_count == 0:
    print("\n✓ No missing images found!")
    exit(0)

# Create backup
print("\n3. Creating backup...")
import shutil
shutil.copy2(CSV_PATH, BACKUP_PATH)
print(f"   ✓ Backup: {BACKUP_PATH}")

# Fix missing images with a better placeholder
print("\n4. Fixing missing images...")
placeholder = "https://via.placeholder.com/300x200/1e293b/64748b?text=No+Image"

# Update all missing images
df.loc[missing_mask, 'image'] = placeholder
fixed_count = missing_mask.sum()

print(f"   ✓ Fixed {fixed_count} products")

# Save
print("\n5. Saving changes...")
df.to_csv(CSV_PATH, index=False)
print(f"   ✓ Saved to {CSV_PATH}")

# Clear cache
if os.path.exists(CACHE_PATH):
    print("\n6. Clearing cache...")
    os.remove(CACHE_PATH)
    print(f"   ✓ Removed cache")

# Verify
print("\n7. Verification...")
df_verify = pd.read_csv(CSV_PATH, low_memory=False)
still_missing = df_verify['image'].isna().sum()
print(f"   Remaining missing: {still_missing}")

print("\n" + "=" * 80)
print("BULK FIX COMPLETE!")
print("=" * 80)
print(f"\nFixed: {fixed_count} products")
print(f"Placeholder: {placeholder}")
print("\nNext steps:")
print("1. Restart the server: cd server && python main.py")
print("2. Refresh the frontend")
print("3. Images should load smoothly without flashing")
