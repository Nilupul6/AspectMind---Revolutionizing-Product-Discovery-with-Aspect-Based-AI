import pandas as pd

CSV_PATH = r"c:\Users\Nilupul Nishitha\Desktop\requirments\data\Second_fixed_image_urls.csv"

print("=== IMAGE URL QUICK CHECK ===\n")

df = pd.read_csv(CSV_PATH, low_memory=False)

print(f"Total rows: {len(df)}")
print(f"Non-null images: {df['image'].notna().sum()}")
print(f"Null images: {df['image'].isna().sum()}")

print(f"\nSample valid URLs:")
for i, url in enumerate(df['image'].dropna().head(10)):
    print(f"  {i+1}. {url}")

print(f"\nChecking for corrupted URLs...")
all_urls = df['image'].dropna().astype(str)
corrupted = sum(1 for url in all_urls if url.count('https://') > 1)
missing_protocol = sum(1 for url in all_urls if not url.startswith(('http://', 'https://')))

print(f"\nCorrupted (multiple https://): {corrupted}")
print(f"Missing protocol: {missing_protocol}")
print(f"Valid URLs: {len(all_urls) - corrupted - missing_protocol}")

if corrupted > 0:
    print(f"\n!!! PROBLEM DETECTED: {corrupted} corrupted URLs found !!!")
    print("Run: python repair_images_fixed.py")
elif missing_protocol > 100:
    print(f"\n!!! PROBLEM DETECTED: {missing_protocol} URLs missing protocol !!!")
    print("Run: python repair_images_fixed.py")
else:
    print("\n=== DATA LOOKS GOOD ===")
