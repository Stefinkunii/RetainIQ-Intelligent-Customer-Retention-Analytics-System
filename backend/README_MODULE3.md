# RetainIQ — Module 3: Customer Purchase Analytics

**Developer:** Mahad  
**Module:** Module 3 — Customer Purchase Analytics  

---

## 1. Overview

Module 3 analyzes validated customer transaction records from Module 2 (`data/Cleaned_Online_Retail.csv`) and calculates 11 core purchase metrics. The implementation is lightweight, beginner-friendly, and uses straightforward Pandas operations without unnecessary complexity.

---

## 2. Core Analytics Functions (`backend/purchase_analytics.py`)

All 11 required functions are implemented directly:

| # | Requirement | Function Name | Return Type | Description |
|---|---|---|---|---|
| 1 | **Completed-Order Revenue** | `calculate_completed_revenue(df, period="all")` | `float` | Total revenue (`Quantity * UnitPrice`) from completed orders. |
| 2 | **Distinct Invoices** | `calculate_distinct_invoices(df, period="all")` | `int` | Count of unique completed invoice numbers. |
| 3 | **Average Order Value (AOV)** | `calculate_average_order_value(df, period="all")` | `float` | `Total Revenue / Distinct Invoices`. |
| 4 | **Repeat Customers** | `calculate_repeat_customers(df, period="all")` | `dict` | Total valid customers, repeat customers (>1 orders), and repeat rate (%). Excludes missing CustomerIDs. |
| 5 | **Purchase Frequency** | `calculate_purchase_frequency(df, period="all")` | `float` | Distinct completed invoices of valid customers / valid unique customers. |
| 6 | **Buying Intervals** | `calculate_buying_intervals(df, period="all")` | `float` | Average days between consecutive distinct purchases for repeat customers (excludes missing CustomerIDs). |
| 7 | **Revenue Trends** | `calculate_revenue_trends(df, period="all")` | `list[dict]` | Monthly revenue breakdown (`[{"Month": "YYYY-MM", "Revenue": float}, ...]`). |
| 8 | **Top-Spending Customers** | `calculate_top_spending_customers(df, limit=10, period="all")` | `list[dict]` | Ranked list of top customers by total spend (excludes missing CustomerIDs). |
| 9 | **Popular Products** | `calculate_popular_products(df, limit=10, period="all")` | `list[dict]` | Products with highest purchase quantity. |
| 10 | **Country-Wise Purchasing** | `calculate_country_purchasing(df, limit=10, period="all")` | `list[dict]` | Revenue, order count, and customer count grouped by country. |
| 11 | **Date Filters** | `filter_data(df, period="all")` | `pd.DataFrame` | Filters by `'7d'`, `'30d'`, `'90d'`, or `'all'`. Raises `ValueError` for unsupported periods. |

---

## 3. Verified Results on Cleaned Dataset

Ran on `data/Cleaned_Online_Retail.csv` (360,147 records):

- **Completed Revenue (All-Time):** £4,349,152.62
- **Distinct Completed Invoices:** 16,680
- **Average Order Value (AOV):** £260.74
- **Repeat Customers:** 2,704 out of 4,189 (64.55%)
- **Purchase Frequency:** 3.98 orders/customer
- **Buying Intervals:** 42.99 average days between repeat orders
- **Date Filters Comparison:**
  - `7d`  : 569 invoices, £140,156.50 revenue, £246.32 AOV
  - `30d` : 2,510 invoices, £639,009.86 revenue, £254.59 AOV
  - `90d` : 5,991 invoices, £1,688,663.52 revenue, £281.87 AOV
  - `all` : 16,680 invoices, £4,349,152.62 revenue, £260.74 AOV

---

## 4. Flask API Endpoints (`backend/app.py`)

A clean, RESTful Flask API with CORS enabled for frontend connection:

- `GET /api/health` — Health check status and dataset records.
- `GET /api/purchase-analytics/overview?period=all|7d|30d|90d` — Core metrics summary.
- `GET /api/purchase-analytics/revenue-trends?period=all|7d|30d|90d` — Monthly revenue trend.
- `GET /api/purchase-analytics/top-customers?period=all|7d|30d|90d&limit=10` — Top customer spenders.
- `GET /api/purchase-analytics/popular-products?period=all|7d|30d|90d&limit=10` — Popular products.
- `GET /api/purchase-analytics/country-purchasing?period=all|7d|30d|90d&limit=10` — Country sales breakdown.
- `GET /api/purchase-analytics/summary?period=all|7d|30d|90d` — Complete dashboard payload.

---

## 5. How to Run and Test

### Run All Tests:
```bash
python backend/test_purchase_analytics.py
```
*(Includes basic calculation tests on small sample data and full verification on the cleaned dataset).*

### Start Flask API Server:
```bash
python backend/app.py
```
Runs at `http://127.0.0.1:5000`.
