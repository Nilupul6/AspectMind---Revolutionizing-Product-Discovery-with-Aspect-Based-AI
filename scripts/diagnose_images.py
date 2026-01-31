import pandas as pd
import os
import re

DATA_DIR = r"c:\Users\Nilupul Nishitha\Desktop\requirments\data"
second_csv = os.path.join(DATA_DIR, "Second_fixed_image_urls.csv")

def analyze_url(url):
    """Analyze a URL and categorize it"""
    if not url or pd.isna(url):
        return "MISSING"
    
    url = str(url).strip()
    
    if url.lower() == 'nan' or url == '':
        return "EMPTY"
    
    # Check for multiple https
    if url.count('https://') > 1 or url.count('http://') > 1:
        return "CORRUPTED_MULTIPLE_PROTOCOL"
    
    # Check if it's a valid URL
    if not url.startswith(('http://', 'https://')):
        return "INVALID_NO_PROTOCOL"
    
    # Check for valid extension
    if not re.search(r'\.(jpg|jpeg|png|gif)$', url, re.IGNORECASE):
        return "INVALID_NO_EXTENSION"
    
    # Check for weird characters
    if re.search(r'[\s<>"\']', url):
        return "INVALID_SPECIAL_CHARS"
    
    return "VALID"

def main():
    print("=" * 70)
    print("IMAGE URL DIAGNOSTIC REPORT")
    print("=" * 70)
    
    print("\nLoading CSV...")
    df = pd.read_csv(second_csv)
    print(f"Total rows: {len(df)}")
    
    print("\nAnalyzing image URLs...")
    categories = {}
    
    for idx, row in df.iterrows():
        category = analyze_url(row.get('image'))
        categories[category] = categories.get(category, 0) + 1
        
        if (idx + 1) % 10000 == 0:
            print(f"  Processed {idx + 1}/{len(df)} rows...")
    
    print("\n" + "=" * 70)
    print("RESULTS:")
    print("=" * 70)
    
    total = len(df)
    for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total) * 100
        print(f"{category:30s}: {count:8d} ({percentage:5.1f}%)")
    
    print("\n" + "=" * 70)
    
    # Show examples of problematic URLs
    if categories.get("CORRUPTED_MULTIPLE_PROTOCOL", 0) > 0:
        print("\nEXAMPLES OF CORRUPTED URLs (multiple protocols):")
        print("-" * 70)
        count = 0
        for idx, row in df.iterrows():
            url = row.get('image')
            if url and (str(url).count('https://') > 1 or str(url).count('http://') > 1):
                print(f"{count + 1}. {url[:100]}...")
                count += 1
                if count >= 5:
                    break
    
    if categories.get("INVALID_NO_PROTOCOL", 0) > 0:
        print("\nEXAMPLES OF URLs WITHOUT PROTOCOL:")
        print("-" * 70)
        count = 0
        for idx, row in df.iterrows():
            url = str(row.get('image', ''))
            if url and not url.startswith(('http://', 'https://')) and url.lower() != 'nan':
                print(f"{count + 1}. {url[:100]}")
                count += 1
                if count >= 5:
                    break
    
    # Show some valid URLs
    print("\nEXAMPLES OF VALID URLs:")
    print("-" * 70)
    count = 0
    for idx, row in df.iterrows():
        if analyze_url(row.get('image')) == "VALID":
            print(f"{count + 1}. {row.get('image')}")
            count += 1
            if count >= 5:
                break
    
    print("\n" + "=" * 70)
    print("RECOMMENDATION:")
    print("=" * 70)
    
    valid_count = categories.get("VALID", 0)
    valid_percentage = (valid_count / total) * 100
    
    if valid_percentage > 90:
        print("OK - Data looks good! Most URLs are valid.")
    elif valid_percentage > 70:
        print("WARNING - Some issues detected. Consider running the repair script.")
    else:
        print("ERROR - Significant issues detected! Run the repair script immediately.")
    
    corrupted = categories.get("CORRUPTED_MULTIPLE_PROTOCOL", 0)
    if corrupted > 0:
        print(f"\nCRITICAL: {corrupted} URLs have multiple protocols and need repair!")
    
    print("\n" + "=" * 70)
    print("To fix issues, run: python repair_images_fixed.py")
    print("=" * 70)

if __name__ == "__main__":
    main()
