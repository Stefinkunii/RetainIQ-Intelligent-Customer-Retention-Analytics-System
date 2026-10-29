
import pandas as pd
from purchase_analytics import calculate_monthly_revenue

data = {
    "InvoiceDate": [
        "2025-01-05",
        "2025-01-18",
        "2025-02-03"
    ],
    "Quantity": [2, 3, 4],
    "UnitPrice": [10, 10, 5]
}

df = pd.DataFrame(data)

result = calculate_monthly_revenue(df)

print("Monthly revenue:")
print(result)
