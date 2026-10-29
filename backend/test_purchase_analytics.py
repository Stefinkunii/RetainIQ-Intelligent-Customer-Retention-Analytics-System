"""
RetainIQ — Module 3: Customer Purchase Analytics Tests
Simple and meaningful tests for all 11 core requirements:
1. Basic calculation tests using a small sample DataFrame.
2. Overall verification test using the actual cleaned retail dataset.

Run with: python backend/test_purchase_analytics.py
Or with: pytest backend/test_purchase_analytics.py
"""

from pathlib import Path
import pytest
import pandas as pd

from purchase_analytics import (
    filter_data,
    calculate_completed_revenue,
    calculate_distinct_invoices,
    calculate_average_order_value,
    calculate_repeat_customers,
    calculate_purchase_frequency,
    calculate_buying_intervals,
    calculate_revenue_trends,
    calculate_top_spending_customers,
    calculate_popular_products,
    calculate_country_purchasing,
    get_purchase_analytics_summary
)


# ---------------------------------------------------------------------------
# Test 1: Small Sample DataFrame Test (Core Logic & All 11 Requirements)
# ---------------------------------------------------------------------------

def test_basic_calculations():
    """Verify all 11 core analytics requirements on a small controlled dataset."""
    sample_data = {
        "InvoiceNo": ["1001", "1001", "1002", "C1003", "1004", "1005", "1006", "1007"],
        "StockCode": ["ITEM_A", "ITEM_B", "ITEM_A", "ITEM_C", "ITEM_B", "ITEM_A", "ITEM_D", "ITEM_E"],
        "Description": ["Alpha", "Beta", "Alpha", "Cancelled", "Beta", "Alpha", "Invalid", "No Customer"],
        "Quantity": [2, 3, 5, -1, 4, 10, -5, 2],
        "UnitPrice": [10.0, 20.0, 10.0, 15.0, 20.0, 10.0, 5.0, 10.0],
        "InvoiceDate": [
            "01/01/2025 10:00",  # UK format DD/MM/YYYY
            "01/01/2025 10:00",
            "15/01/2025 11:00",
            "16/01/2025 12:00",  # Cancelled (C1003)
            "01/02/2025 14:00",
            "20/02/2025 09:30",
            "22/02/2025 10:00",  # Negative quantity (-5)
            "20/02/2025 11:00"   # Missing CustomerID (None)
        ],
        "CustomerID": [101, 101, 101, 101, 102, 102, 103, None],
        "Country": ["United Kingdom", "United Kingdom", "United Kingdom", "United Kingdom",
                    "Germany", "Germany", "France", "United Kingdom"]
    }
    df = pd.DataFrame(sample_data)

    print("\n--- Running Test 1: Basic Calculations on Sample Data ---")

    # 1. Completed-Order Revenue
    # Valid completed rows:
    # 1001: 2*10 + 3*20 = 80
    # 1002: 5*10 = 50
    # 1004: 4*20 = 80
    # 1005: 10*10 = 100
    # 1007 (guest/no customer): 2*10 = 20
    # Total revenue = 80 + 50 + 80 + 100 + 20 = 330.0
    revenue = calculate_completed_revenue(df)
    assert revenue == 330.0, f"Expected 330.0, got {revenue}"
    print(f"[OK] 1. Completed Revenue: {revenue}")

    # 2. Distinct Invoices
    # 5 completed invoices: 1001, 1002, 1004, 1005, 1007
    invoices = calculate_distinct_invoices(df)
    assert invoices == 5, f"Expected 5, got {invoices}"
    print(f"[OK] 2. Distinct Invoices: {invoices}")

    # 3. Average Order Value (AOV = 330.0 / 5 = 66.0)
    aov = calculate_average_order_value(df)
    assert aov == 66.0, f"Expected 66.0, got {aov}"
    print(f"[OK] 3. Average Order Value: {aov}")

    # 4. Repeat Customers (Excludes missing CustomerID)
    # Valid customers:
    # Customer 101: 2 orders (1001, 1002) -> Repeat
    # Customer 102: 2 orders (1004, 1005) -> Repeat
    # Invoice 1007 (None CustomerID) is excluded
    # Total valid customers = 2, Repeat = 2, Rate = 100.0%
    repeat = calculate_repeat_customers(df)
    assert repeat["total_customers"] == 2
    assert repeat["repeat_customers"] == 2
    assert repeat["repeat_rate"] == 100.0
    print(f"[OK] 4. Repeat Customers: {repeat['repeat_customers']} / {repeat['total_customers']} ({repeat['repeat_rate']}%)")

    # 5. Purchase Frequency
    # Total distinct completed invoices belonging to customers with valid CustomerIDs = 4 (1001, 1002, 1004, 1005)
    # Valid customers = 2 (101, 102)
    # Frequency = 4 / 2 = 2.0
    freq = calculate_purchase_frequency(df)
    assert freq == 2.0, f"Expected 2.0, got {freq}"
    print(f"[OK] 5. Purchase Frequency: {freq} orders/customer")

    # 6. Buying Intervals (Distinct completed invoices, excludes missing CustomerID)
    # 101: Jan 1 to Jan 15 = 14.04 days
    # 102: Feb 1 to Feb 20 = 18.81 days
    # Average ~ 16.43 days
    interval = calculate_buying_intervals(df)
    assert 16.0 <= interval <= 17.0, f"Expected ~16.43, got {interval}"
    print(f"[OK] 6. Buying Intervals: {interval} days")

    # 7. Revenue Trends (Monthly with UK-style date parsing)
    # Jan 2025: 130.0, Feb 2025: 200.0
    trends = calculate_revenue_trends(df)
    assert len(trends) == 2
    assert trends[0]["Month"] == "2025-01" and trends[0]["Revenue"] == 130.0
    assert trends[1]["Month"] == "2025-02" and trends[1]["Revenue"] == 200.0
    print(f"[OK] 7. Revenue Trends: {trends}")

    # 8. Top-Spending Customers (Excludes missing CustomerID)
    top_cust = calculate_top_spending_customers(df, limit=2)
    assert len(top_cust) == 2
    assert top_cust[0]["CustomerID"] == 102 and top_cust[0]["TotalSpend"] == 180.0
    assert top_cust[1]["CustomerID"] == 101 and top_cust[1]["TotalSpend"] == 130.0
    print(f"[OK] 8. Top Spenders: {top_cust}")

    # 9. Popular Products (by quantity)
    top_prod = calculate_popular_products(df, limit=2)
    assert top_prod[0]["StockCode"] == "ITEM_A" and top_prod[0]["Quantity"] == 17
    assert top_prod[1]["StockCode"] == "ITEM_B" and top_prod[1]["Quantity"] == 7
    print(f"[OK] 9. Popular Products: {top_prod}")

    # 10. Country-Wise Purchasing
    by_country = calculate_country_purchasing(df)
    assert by_country[0]["Country"] == "Germany" and by_country[0]["Revenue"] == 180.0
    assert by_country[1]["Country"] == "United Kingdom" and by_country[1]["Revenue"] == 150.0
    print(f"[OK] 10. Country Purchasing: {by_country}")

    # 11. Date Filters & Period Validation
    # Latest date is 2025-02-20
    # 7-day: 2025-02-20 (Invoice 1005: 100, Invoice 1007: 20) -> 120.0
    # 30-day: 2025-02-01 and 2025-02-20 -> 200.0
    # 90-day / all: all completed orders -> 330.0
    assert calculate_completed_revenue(df, period="7d") == 120.0
    assert calculate_completed_revenue(df, period="30d") == 200.0
    assert calculate_completed_revenue(df, period="90d") == 330.0
    assert calculate_completed_revenue(df, period="all") == 330.0

    # Period validation: should raise ValueError for invalid periods
    try:
        filter_data(df, period="invalid_period")
        assert False, "Should have raised ValueError for invalid period"
    except ValueError as e:
        assert "Invalid period" in str(e)

    print(f"[OK] 11. Date Filters & Validation (7d, 30d, 90d, all, invalid check): Tested successfully")
    print("All basic calculation tests PASSED!\n")


# ---------------------------------------------------------------------------
# Test 2: Real Cleaned Dataset Verification Test
# ---------------------------------------------------------------------------

def test_real_dataset_verification():
    """Verify all Module 3 functions on the actual cleaned retail dataset."""
    project_root = Path(__file__).resolve().parent.parent
    dataset_path = project_root / "data" / "Cleaned_Online_Retail.csv"

    print(f"--- Running Test 2: Cleaned Dataset Verification ---")
    print(f"Loading dataset: {dataset_path}")

    assert dataset_path.exists(), f"Dataset file not found at {dataset_path}"
    df = pd.read_csv(dataset_path)

    print(f"Records loaded: {len(df):,}")

    # 1. Completed Revenue
    revenue = calculate_completed_revenue(df)
    assert revenue > 0
    print(f"1. Completed Revenue (All-Time): GBP {revenue:,.2f}")

    # 2. Distinct Invoices
    invoices = calculate_distinct_invoices(df)
    assert invoices > 0
    print(f"2. Distinct Invoices: {invoices:,}")

    # 3. Average Order Value
    aov = calculate_average_order_value(df)
    assert aov > 0
    print(f"3. Average Order Value: GBP {aov:,.2f}")

    # 4. Repeat Customers
    repeat = calculate_repeat_customers(df)
    assert repeat["repeat_customers"] > 0
    print(f"4. Repeat Customers: {repeat['repeat_customers']:,} / {repeat['total_customers']:,} ({repeat['repeat_rate']}%)")

    # 5. Purchase Frequency
    freq = calculate_purchase_frequency(df)
    assert freq > 0
    print(f"5. Purchase Frequency: {freq} orders/customer")

    # 6. Buying Intervals
    interval = calculate_buying_intervals(df)
    assert interval > 0
    print(f"6. Buying Intervals: {interval} days")

    # 7. Revenue Trends
    trends = calculate_revenue_trends(df)
    assert len(trends) > 0
    print(f"7. Monthly Revenue Trends ({len(trends)} months): First={trends[0]}, Last={trends[-1]}")

    # 8. Top-Spending Customers
    top_cust = calculate_top_spending_customers(df, limit=3)
    assert len(top_cust) == 3
    print(f"8. Top 3 Spenders: {top_cust}")

    # 9. Popular Products
    top_prod = calculate_popular_products(df, limit=3)
    assert len(top_prod) == 3
    print(f"9. Top 3 Products: {top_prod}")

    # 10. Country Purchasing
    by_country = calculate_country_purchasing(df, limit=3)
    assert len(by_country) == 3
    print(f"10. Top 3 Countries: {by_country}")

    # 11. Date Filters Comparison
    print("11. Date Filter Verifications:")
    for period in ["7d", "30d", "90d", "all"]:
        p_rev = calculate_completed_revenue(df, period=period)
        p_inv = calculate_distinct_invoices(df, period=period)
        p_aov = calculate_average_order_value(df, period=period)
        print(f"   - Filter '{period:4}': Invoices = {p_inv:6,}, Revenue = GBP {p_rev:11,.2f}, AOV = GBP {p_aov:.2f}")

    # Period validation on real dataset
    try:
        filter_data(df, period="14d")
        assert False, "Should raise ValueError for 14d"
    except ValueError:
        pass

    # Summary payload test
    summary = get_purchase_analytics_summary(df, period="30d")
    assert "metrics" in summary
    assert "repeat_customers" in summary

    print("Cleaned dataset verification test PASSED!\n")


if __name__ == "__main__":
    test_basic_calculations()
    test_real_dataset_verification()
