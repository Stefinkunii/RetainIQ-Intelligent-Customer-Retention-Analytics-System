
from pathlib import Path
import pandas as pd

from purchase_analytics import calculate_purchase_metrics

project_folder = Path(__file__).resolve().parent.parent
file_path = project_folder / "data" / "Cleaned_Online_Retail.csv"

df = pd.read_csv(file_path)

print("Dataset loaded successfully!")
print("Dataset shape:", df.shape)

result = calculate_purchase_metrics(df)

print("\nPurchase metrics:")
print(result)
