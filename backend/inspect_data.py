
from pathlib import Path
import pandas as pd

project_folder = Path(__file__).resolve().parent.parent
file_path = project_folder / "data" / "Cleaned_Online_Retail.csv"

print("Checking dataset file...")

if file_path.exists():
    df = pd.read_csv(file_path)

    print("Dataset loaded successfully!")
    print("Number of rows and columns:", df.shape)

    print("\nColumn names:")
    print(df.columns.tolist())

    print("\nFirst five records:")
    print(df.head())

else:
    print("Dataset file not found.")
    print("Expected file location:", file_path)
print("\nAll column names:")
print(df.columns.tolist())