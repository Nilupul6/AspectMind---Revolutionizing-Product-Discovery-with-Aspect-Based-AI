import pandas as pd

CSV_PATH = r"c:\Users\Nilupul Nishitha\Desktop\requirments\data\Second_fixed_image_urls.csv"

print("Checking AMES COMPANIES product after fix...\n")

df = pd.read_csv(CSV_PATH, low_memory=False)
result = df[df['itemName'].str.contains('AMES COMPANIES', case=False, na=False)]

if len(result) > 0:
    print(f"Found {len(result)} match(es)\n")
    print("=" * 80)
    
    for idx, row in result.iterrows():
        print(f"\nRow Index: {idx}")
        print(f"Product: {row['itemName']}")
        print(f"Image URL: {row.get('image', 'N/A')}")
        print(f"Category: {row.get('category', 'N/A')}")
        
        # Check the status
        img_url = str(row.get('image', ''))
        if 'placeholder' in img_url.lower():
            print("\nSTATUS: ⚠️ Using placeholder image")
            print("RECOMMENDATION: Find actual product image URL")
        elif pd.notna(row.get('image')) and img_url.startswith('http'):
            print("\nSTATUS: ✓ Has valid image URL")
        else:
            print("\nSTATUS: ✗ Still missing image")
        
        print("-" * 80)
