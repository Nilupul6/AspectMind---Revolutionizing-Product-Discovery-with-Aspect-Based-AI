import pandas as pd
import os

CSV_PATH = r"c:\Users\Nilupul Nishitha\Desktop\requirments\data\Second_fixed_image_urls.csv"
BACKUP_PATH = r"c:\Users\Nilupul Nishitha\Desktop\requirments\data\Second_fixed_image_urls_backup_svg.csv"
CACHE_PATH = r"c:\Users\Nilupul Nishitha\Desktop\requirments\data\Second_fixed_image_urls.csv_processed.pkl"

# Base64 encoded SVG placeholder (works offline, no network needed)
# SVG: 300x200, dark background (#1e293b), gray text (#64748b), "No Image Available"
SVG_PLACEHOLDER = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iIzFlMjkzYiIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwsIHNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iMTYiIGZpbGw9IiM2NDc0OGIiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5ObyBJbWFnZSBBdmFpbGFibGU8L3RleHQ+PC9zdmc+'

print("=" * 80)
print("REPLACING EXTERNAL PLACEHOLDERS WITH OFFLINE SVG")
print("=" * 80)

# Load data
print("\n1. Loading CSV...")
df = pd.read_csv(CSV_PATH, low_memory=False)
print(f"   Total rows: {len(df)}")

# Find via.placeholder.com URLs
print("\n2. Finding external placeholder URLs...")
placeholder_mask = df['image'].astype(str).str.contains('via.placeholder.com', case=False, na=False)
placeholder_count = placeholder_mask.sum()
print(f"   Found {placeholder_count} external placeholders")

if placeholder_count == 0:
    print("\n✓ No external placeholders found!")
    exit(0)

# Create backup
print("\n3. Creating backup...")
import shutil
shutil.copy2(CSV_PATH, BACKUP_PATH)
print(f"   ✓ Backup: {BACKUP_PATH}")

# Replace with SVG placeholder
print("\n4. Replacing with offline SVG placeholder...")
df.loc[placeholder_mask, 'image'] = SVG_PLACEHOLDER
print(f"   ✓ Replaced {placeholder_count} URLs")

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
still_external = df_verify['image'].astype(str).str.contains('via.placeholder.com', case=False, na=False).sum()
svg_count = df_verify['image'].astype(str).str.contains('data:image/svg', case=False, na=False).sum()
print(f"   External placeholders remaining: {still_external}")
print(f"   SVG placeholders: {svg_count}")

print("\n" + "=" * 80)
print("REPLACEMENT COMPLETE!")
print("=" * 80)
print(f"\nReplaced: {placeholder_count} URLs")
print(f"New placeholder: Base64 SVG (works offline)")
print("\nBenefits:")
print("✓ No network requests needed")
print("✓ Works offline")
print("✓ No DNS/connection errors")
print("✓ Instant loading")
print("\nNext steps:")
print("1. Restart the server")
print("2. Refresh the frontend")
print("3. No more ERR_NAME_NOT_RESOLVED errors!")
