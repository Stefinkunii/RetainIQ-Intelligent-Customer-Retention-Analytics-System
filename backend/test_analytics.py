
import pandas as pd
from purchase_analytics import calculate_purchase_metrics

data = {
    "InvoiceNo": ["A001", "A001", "A002"],
    "Quantity": [2, 3, 4],
    "UnitPrice": [10, 10, 5]
}

df = pd.DataFrame(data)

result = calculate_purchase_metrics(df)

print("Purchase metrics:")
print(result)
