import pandas as pd

CSV_PATH = r"c:\Users\Nilupul Nishitha\Desktop\requirments\data\Second_fixed_image_urls.csv"
ROOT_CSV = r"c:\Users\Nilupul Nishitha\Desktop\requirments\fixed_image_urls.csv"

print("Searching for AMES COMPANIES product...\n")

df = pd.read_csv(CSV_PATH, low_memory=False)
result = df[df['itemName'].str.contains('AMES COMPANIES', case=False, na=False)]

if len(result) > 0:
    print(f"Found {len(result)} matches\n")
    print("=" * 80)
    
    for idx, row in result.iterrows():
        print(f"\nRow Index: {idx}")
        print(f"Product: {row['itemName']}")
        print(f"Image URL: {row.get('image', 'N/A')}")
        print(f"Category: {row.get('category', 'N/A')}")
        print(f"Description: {str(row.get('description', 'N/A'))[:100]}...")
        
        # Check if image URL is missing
        if pd.isna(row.get('image')):
            print("\n⚠️ IMAGE URL IS MISSING!")
            
            # Try to find in root CSV
            print("\nSearching in root CSV for this product...")
            try:
                df_root = pd.read_csv(ROOT_CSV, low_memory=False)
                root_match = df_root[df_root['itemName'] == row['itemName']]
                
                if len(root_match) > 0:
                    root_img = root_match.iloc[0].get('image')
                    if pd.notna(root_img):
                        print(f"✓ Found in root CSV: {root_img}")
                        print(f"\nTo fix, update row {idx} with this URL")
                    else:
                        print("✗ Root CSV also has no image for this product")
                else:
                    print("✗ Product not found in root CSV")
            except Exception as e:
                print(f"Error reading root CSV: {e}")
        
        print("-" * 80)
else:
    print("No products found")
