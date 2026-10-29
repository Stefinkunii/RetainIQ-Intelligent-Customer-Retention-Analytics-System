
from pathlib import Path
import pandas as pd

from purchase_analytics import calculate_top_products

project_folder = Path(__file__).resolve().parent.parent
file_path = project_folder / "data" / "Cleaned_Online_Retail.csv"

df = pd.read_csv(file_path)

print("TOP 10 PRODUCTS BY QUANTITY SOLD")
print("--------------------------------")

for product in calculate_top_products(df):
    print(product)
