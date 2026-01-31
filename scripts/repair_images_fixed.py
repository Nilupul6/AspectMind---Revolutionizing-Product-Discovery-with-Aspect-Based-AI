import pandas as pd
import os
import re

DATA_DIR = r"c:\Users\Nilupul Nishitha\Desktop\requirments\data"
ROOT_DIR = r"c:\Users\Nilupul Nishitha\Desktop\requirments"
second_csv = os.path.join(DATA_DIR, "Second_fixed_image_urls.csv")
root_csv = os.path.join(ROOT_DIR, "fixed_image_urls.csv")
cache_pkl = os.path.join(DATA_DIR, "Second_fixed_image_urls.csv_processed.pkl")
backup_csv = os.path.join(DATA_DIR, "Second_fixed_image_urls_backup.csv")

def clean_image_url(url):
    """Clean and validate image URLs with improved logic"""
    # Handle None, NaN, or empty values
    if not url or pd.isna(url):
        return None
    
    url = str(url).strip()
    
    # Skip if it's literally the string 'nan'
    if url.lower() == 'nan' or url == '':
        return None
    
    # Pattern 1: Extract valid HTTPS URL (most common case)
    # This handles URLs that might have extra text around them
    https_match = re.search(r'(https?://[^\s\'"<>]+\.(?:jpg|jpeg|png|gif))', url, re.IGNORECASE)
    if https_match:
        clean_url = https_match.group(1)
        # Remove any trailing punctuation or special characters
        clean_url = re.sub(r'[,;)\]}\'"]+$', '', clean_url)
        return clean_url
    
    # Pattern 2: Amazon image path format (images/I/...)
    amazon_path_match = re.search(r'(images/)?I/([a-zA-Z0-9\-_%]+\.(jpg|png|jpeg))', url, re.IGNORECASE)
    if amazon_path_match:
        path = amazon_path_match.group(0)
        if not path.startswith("images/"):
            path = "images/" + path
        return f"https://images-na.ssl-images-amazon.com/{path}"
    
    # Pattern 3: Just the image filename (fallback)
    filename_match = re.search(r'([a-zA-Z0-9]{8,}%?\.(?:jpg|jpeg|png))', url, re.IGNORECASE)
    if filename_match:
        filename = filename_match.group(1)
        return f"https://images-na.ssl-images-amazon.com/images/I/{filename}"
    
    return None

def validate_url(url):
    """Validate that a URL looks reasonable"""
    if not url:
        return False
    
    # Check if it's a valid HTTP/HTTPS URL
    if not url.startswith(('http://', 'https://')):
        return False
    
    # Check if it has a valid image extension
    if not re.search(r'\.(jpg|jpeg|png|gif)$', url, re.IGNORECASE):
        return False
    
    # Check for multiple https:// (corrupted URLs)
    if url.count('https://') > 1 or url.count('http://') > 1:
        return False
    
    return True

def main():
    print("=" * 60)
    print("FIXED IMAGE URL REPAIR SCRIPT")
    print("=" * 60)
    
    # Create backup first
    print("\n1. Creating backup...")
    if os.path.exists(second_csv):
        import shutil
        shutil.copy2(second_csv, backup_csv)
        print(f"   ✓ Backup created: {backup_csv}")
    
    # Load data
    print("\n2. Loading data...")
    try:
        df_root = pd.read_csv(root_csv)
        print(f"   ✓ Loaded root CSV: {len(df_root)} rows")
    except Exception as e:
        print(f"   ⚠ Could not load root CSV: {e}")
        df_root = None
    
    df_second = pd.read_csv(second_csv)
    print(f"   ✓ Loaded target CSV: {len(df_second)} rows")
    
    # Build mapping from root CSV
    root_map = {}
    if df_root is not None:
        print("\n3. Building image mapping from root CSV...")
        for idx, row in df_root.iterrows():
            if pd.notna(row.get('image')) and pd.notna(row.get('itemName')):
                cleaned = clean_image_url(row['image'])
                if cleaned and validate_url(cleaned):
                    item_name = str(row['itemName']).strip()
                    if item_name not in root_map:  # Only use first occurrence
                        root_map[item_name] = cleaned
        print(f"   ✓ Built mapping for {len(root_map)} items")
    
    # Fix images in target CSV
    print("\n4. Repairing image URLs...")
    fixed_count = 0
    from_root_count = 0
    failed_count = 0
    
    new_images = []
    
    for idx, row in df_second.iterrows():
        original_url = row.get('image')
        
        # Try to clean the existing URL first
        cleaned = clean_image_url(original_url)
        
        if cleaned and validate_url(cleaned):
            new_images.append(cleaned)
            if cleaned != original_url:
                fixed_count += 1
        else:
            # Try to get from root mapping
            item_name = str(row.get('itemName', '')).strip()
            if item_name in root_map:
                new_images.append(root_map[item_name])
                from_root_count += 1
            else:
                # Try to extract from description as last resort
                desc_url = clean_image_url(str(row.get('description', '')))
                if desc_url and validate_url(desc_url):
                    new_images.append(desc_url)
                    fixed_count += 1
                else:
                    new_images.append(None)
                    failed_count += 1
        
        # Progress indicator
        if (idx + 1) % 10000 == 0:
            print(f"   Processing... {idx + 1}/{len(df_second)} rows")
    
    # Update dataframe
    df_second['image'] = new_images
    
    print(f"\n   ✓ Fixed {fixed_count} URLs by cleaning")
    print(f"   ✓ Restored {from_root_count} URLs from root CSV")
    print(f"   ⚠ Could not fix {failed_count} URLs")
    
    # Validation check
    print("\n5. Validating results...")
    valid_urls = sum(1 for url in new_images if url and validate_url(url))
    print(f"   ✓ Valid URLs: {valid_urls}/{len(df_second)} ({valid_urls/len(df_second)*100:.1f}%)")
    
    # Check for corrupted URLs
    corrupted = sum(1 for url in new_images if url and url.count('https://') > 1)
    if corrupted > 0:
        print(f"   ⚠ WARNING: Found {corrupted} potentially corrupted URLs!")
    else:
        print(f"   ✓ No corrupted URLs detected")
    
    # Save results
    print("\n6. Saving repaired CSV...")
    df_second.to_csv(second_csv, index=False)
    print(f"   ✓ Saved to: {second_csv}")
    
    # Clear cache
    if os.path.exists(cache_pkl):
        print("\n7. Clearing cache...")
        os.remove(cache_pkl)
        print(f"   ✓ Removed: {cache_pkl}")
    
    # Show samples
    print("\n8. Sample URLs (first 5 valid):")
    sample_count = 0
    for url in new_images:
        if url and validate_url(url):
            print(f"   {url}")
            sample_count += 1
            if sample_count >= 5:
                break
    
    print("\n" + "=" * 60)
    print("REPAIR COMPLETE!")
    print("=" * 60)
    print(f"\nBackup saved to: {backup_csv}")
    print("If you need to restore, copy the backup file back.")

if __name__ == "__main__":
    main()
