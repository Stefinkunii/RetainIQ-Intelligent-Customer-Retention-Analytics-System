"""
RetainIQ — Module 3: Customer Purchase Analytics
Simple, maintainable backend module analyzing customer purchasing behavior.

Assigned Developer: Mahad
"""

import pandas as pd


# ---------------------------------------------------------------------------
# Data Filtering Helper (Completed Orders + Date Filters)
# ---------------------------------------------------------------------------

def filter_data(df, period="all"):
    """
    Filter data for completed orders and apply the requested date filter.
    
    Completed order rules:
    - Exclude cancelled orders (InvoiceNo starting with 'C' or 'c')
    - Quantity must be greater than 0
    - UnitPrice must be greater than 0
    
    Supported date filters:
    - '7d'  : Last 7 days
    - '30d' : Last 30 days
    - '90d' : Last 90 days
    - 'all' : All available history
    """
    valid_periods = ["7d", "30d", "90d", "all"]
    if period not in valid_periods:
        raise ValueError(
            f"Invalid period '{period}'. Supported periods are: '7d', '30d', '90d', 'all'."
        )

    if df.empty:
        return df

    filtered_df = df.copy()

    # Rule 1: Exclude cancelled orders if InvoiceNo column exists
    if "InvoiceNo" in filtered_df.columns:
        filtered_df = filtered_df[~filtered_df["InvoiceNo"].astype(str).str.startswith(("C", "c"))]

    # Rule 2: Keep only valid positive quantity and price
    if "Quantity" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Quantity"] > 0]
    if "UnitPrice" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["UnitPrice"] > 0]

    # Rule 3: Ensure UK-style date parsing (dayfirst=True) if InvoiceDate is string
    if "InvoiceDate" in filtered_df.columns and not pd.api.types.is_datetime64_any_dtype(filtered_df["InvoiceDate"]):
        try:
            filtered_df["InvoiceDate"] = pd.to_datetime(filtered_df["InvoiceDate"], dayfirst=True)
        except Exception:
            filtered_df["InvoiceDate"] = pd.to_datetime(filtered_df["InvoiceDate"])

    # Rule 4: Apply date filter if requested
    if period in ["7d", "30d", "90d"] and "InvoiceDate" in filtered_df.columns:
        days_lookup = {"7d": 7, "30d": 30, "90d": 90}
        days = days_lookup[period]
        max_date = filtered_df["InvoiceDate"].max()
        cutoff_date = max_date - pd.Timedelta(days=days)
        filtered_df = filtered_df[filtered_df["InvoiceDate"] >= cutoff_date]

    return filtered_df


# ---------------------------------------------------------------------------
# Requirement 1: Completed-Order Revenue
# ---------------------------------------------------------------------------

def calculate_completed_revenue(df, period="all"):
    """Calculate total revenue from completed orders (Revenue = Quantity * UnitPrice)."""
    df_filtered = filter_data(df, period)
    if df_filtered.empty or "Quantity" not in df_filtered.columns or "UnitPrice" not in df_filtered.columns:
        return 0.0

    total_revenue = (df_filtered["Quantity"] * df_filtered["UnitPrice"]).sum()
    return round(float(total_revenue), 2)


# ---------------------------------------------------------------------------
# Requirement 2: Distinct Completed Invoices
# ---------------------------------------------------------------------------

def calculate_distinct_invoices(df, period="all"):
    """Count the number of unique completed invoices."""
    df_filtered = filter_data(df, period)
    if df_filtered.empty or "InvoiceNo" not in df_filtered.columns:
        return 0

    return int(df_filtered["InvoiceNo"].nunique())


# ---------------------------------------------------------------------------
# Requirement 3: Average Order Value (AOV)
# ---------------------------------------------------------------------------

def calculate_average_order_value(df, period="all"):
    """Calculate Average Order Value (AOV = Total Revenue / Unique Invoices)."""
    revenue = calculate_completed_revenue(df, period)
    invoices = calculate_distinct_invoices(df, period)

    if invoices == 0:
        return 0.0

    return round(revenue / invoices, 2)


# ---------------------------------------------------------------------------
# Combined Purchase Metrics (Helper for Dashboard)
# ---------------------------------------------------------------------------

def calculate_purchase_metrics(df, period="all"):
    """Calculate core purchase metrics: revenue, unique orders, units sold, and AOV."""
    df_filtered = filter_data(df, period)
    if df_filtered.empty:
        return {
            "total_revenue": 0.0,
            "unique_orders": 0,
            "units_sold": 0,
            "average_order_value": 0.0
        }

    revenue = calculate_completed_revenue(df, period)
    orders = calculate_distinct_invoices(df, period)
    units_sold = int(df_filtered["Quantity"].sum()) if "Quantity" in df_filtered.columns else 0
    aov = round(revenue / orders, 2) if orders > 0 else 0.0

    return {
        "total_revenue": revenue,
        "unique_orders": orders,
        "units_sold": units_sold,
        "average_order_value": aov
    }


# ---------------------------------------------------------------------------
# Requirement 4: Repeat Customers
# ---------------------------------------------------------------------------

def calculate_repeat_customers(df, period="all"):
    """
    Identify customers who have made more than one completed purchase.
    Excludes records with missing CustomerID.
    """
    df_filtered = filter_data(df, period)
    if df_filtered.empty or "CustomerID" not in df_filtered.columns or "InvoiceNo" not in df_filtered.columns:
        return {"total_customers": 0, "repeat_customers": 0, "repeat_rate": 0.0}

    # Exclude customers with missing CustomerID
    valid_customers = df_filtered[df_filtered["CustomerID"].notna()]
    if valid_customers.empty:
        return {"total_customers": 0, "repeat_customers": 0, "repeat_rate": 0.0}

    order_counts = valid_customers.groupby("CustomerID")["InvoiceNo"].nunique()
    total_customers = len(order_counts)
    repeat_customers = int((order_counts > 1).sum())
    repeat_rate = round((repeat_customers / total_customers) * 100, 2) if total_customers > 0 else 0.0

    return {
        "total_customers": total_customers,
        "repeat_customers": repeat_customers,
        "repeat_rate": repeat_rate
    }


# ---------------------------------------------------------------------------
# Requirement 5: Purchase Frequency
# ---------------------------------------------------------------------------

def calculate_purchase_frequency(df, period="all"):
    """
    Calculate purchase frequency for customers with valid CustomerIDs:
    Total distinct completed invoices of valid customers / Number of valid unique customers.
    """
    df_filtered = filter_data(df, period)
    if df_filtered.empty or "CustomerID" not in df_filtered.columns or "InvoiceNo" not in df_filtered.columns:
        return 0.0

    # Consider only distinct completed invoices for customers with valid CustomerIDs
    valid_customers = df_filtered[df_filtered["CustomerID"].notna()]
    if valid_customers.empty:
        return 0.0

    total_orders = valid_customers["InvoiceNo"].nunique()
    total_customers = valid_customers["CustomerID"].nunique()

    if total_customers == 0:
        return 0.0

    return round(float(total_orders / total_customers), 2)


# ---------------------------------------------------------------------------
# Requirement 6: Buying Intervals
# ---------------------------------------------------------------------------

def calculate_buying_intervals(df, period="all"):
    """
    Calculate average time (in days) between consecutive purchases for repeat customers.
    Uses distinct completed invoices and excludes records with missing CustomerID.
    """
    df_filtered = filter_data(df, period)
    if df_filtered.empty or "CustomerID" not in df_filtered.columns or "InvoiceDate" not in df_filtered.columns or "InvoiceNo" not in df_filtered.columns:
        return 0.0

    # Exclude customers without valid CustomerID
    valid_customers = df_filtered[df_filtered["CustomerID"].notna()].copy()
    if valid_customers.empty:
        return 0.0

    # Ensure UK-style date parsing (dayfirst=True) if not already datetime
    if not pd.api.types.is_datetime64_any_dtype(valid_customers["InvoiceDate"]):
        try:
            valid_customers["InvoiceDate"] = pd.to_datetime(valid_customers["InvoiceDate"], dayfirst=True)
        except Exception:
            valid_customers["InvoiceDate"] = pd.to_datetime(valid_customers["InvoiceDate"])

    # Group by CustomerID and InvoiceNo to get distinct completed invoice timestamps
    orders = (
        valid_customers.groupby(["CustomerID", "InvoiceNo"])["InvoiceDate"]
        .min()
        .reset_index()
        .sort_values(["CustomerID", "InvoiceDate"])
    )

    # Compute difference in days between consecutive purchases for each customer
    orders["previous_date"] = orders.groupby("CustomerID")["InvoiceDate"].shift(1)
    orders["days_between"] = (orders["InvoiceDate"] - orders["previous_date"]).dt.total_seconds() / 86400

    intervals = orders["days_between"].dropna()
    if intervals.empty:
        return 0.0

    return round(float(intervals.mean()), 2)


# ---------------------------------------------------------------------------
# Requirement 7: Revenue Trends
# ---------------------------------------------------------------------------

def calculate_revenue_trends(df, period="all"):
    """Analyze monthly revenue trends over time using UK-style dates."""
    df_filtered = filter_data(df, period).copy()
    if df_filtered.empty or "InvoiceDate" not in df_filtered.columns:
        return []

    if not pd.api.types.is_datetime64_any_dtype(df_filtered["InvoiceDate"]):
        try:
            df_filtered["InvoiceDate"] = pd.to_datetime(df_filtered["InvoiceDate"], dayfirst=True)
        except Exception:
            df_filtered["InvoiceDate"] = pd.to_datetime(df_filtered["InvoiceDate"])

    df_filtered["Revenue"] = df_filtered["Quantity"] * df_filtered["UnitPrice"]
    df_filtered["Month"] = df_filtered["InvoiceDate"].dt.to_period("M").astype(str)

    monthly_revenue = (
        df_filtered.groupby("Month")["Revenue"]
        .sum()
        .round(2)
        .reset_index()
    )

    return monthly_revenue.to_dict(orient="records")


# ---------------------------------------------------------------------------
# Requirement 8: Top-Spending Customers
# ---------------------------------------------------------------------------

def calculate_top_spending_customers(df, limit=10, period="all"):
    """Rank customers by total spending on completed orders (excluding missing CustomerIDs)."""
    df_filtered = filter_data(df, period).copy()
    if df_filtered.empty or "CustomerID" not in df_filtered.columns:
        return []

    valid_customers = df_filtered[df_filtered["CustomerID"].notna()].copy()
    if valid_customers.empty:
        return []

    valid_customers["Revenue"] = valid_customers["Quantity"] * valid_customers["UnitPrice"]

    top_customers = (
        valid_customers.groupby("CustomerID")
        .agg(
            TotalSpend=("Revenue", "sum"),
            OrderCount=("InvoiceNo", "nunique")
        )
        .round(2)
        .reset_index()
        .sort_values(by="TotalSpend", ascending=False)
        .head(limit)
    )

    return top_customers.to_dict(orient="records")


# ---------------------------------------------------------------------------
# Requirement 9: Popular Products
# ---------------------------------------------------------------------------

def calculate_popular_products(df, limit=10, period="all"):
    """Identify products with highest purchase quantity."""
    df_filtered = filter_data(df, period)
    if df_filtered.empty or "StockCode" not in df_filtered.columns:
        return []

    top_products = (
        df_filtered.groupby(["StockCode", "Description"])["Quantity"]
        .sum()
        .reset_index()
        .sort_values(by="Quantity", ascending=False)
        .head(limit)
    )

    return top_products.to_dict(orient="records")


# ---------------------------------------------------------------------------
# Requirement 10: Country-Wise Purchasing
# ---------------------------------------------------------------------------

def calculate_country_purchasing(df, limit=10, period="all"):
    """Analyze purchasing activity and revenue by country."""
    df_filtered = filter_data(df, period).copy()
    if df_filtered.empty or "Country" not in df_filtered.columns:
        return []

    df_filtered["Revenue"] = df_filtered["Quantity"] * df_filtered["UnitPrice"]

    country_summary = (
        df_filtered.groupby("Country")
        .agg(
            Revenue=("Revenue", "sum"),
            OrderCount=("InvoiceNo", "nunique"),
            CustomerCount=("CustomerID", "nunique")
        )
        .round(2)
        .reset_index()
        .sort_values(by="Revenue", ascending=False)
    )

    if limit:
        country_summary = country_summary.head(limit)

    return country_summary.to_dict(orient="records")


# ---------------------------------------------------------------------------
# Requirement 11: Date Filters & Summary Helper
# ---------------------------------------------------------------------------

def filter_by_date(df, period="all"):
    """Helper alias for date filtering."""
    return filter_data(df, period=period)


def get_purchase_analytics_summary(df, period="all"):
    """Consolidated summary of Module 3 analytics for frontend and API use."""
    return {
        "period": period,
        "metrics": calculate_purchase_metrics(df, period),
        "repeat_customers": calculate_repeat_customers(df, period),
        "purchase_frequency": calculate_purchase_frequency(df, period),
        "buying_intervals_days": calculate_buying_intervals(df, period),
        "revenue_trends": calculate_revenue_trends(df, period),
        "top_customers": calculate_top_spending_customers(df, limit=10, period=period),
        "popular_products": calculate_popular_products(df, limit=10, period=period),
        "country_purchasing": calculate_country_purchasing(df, limit=10, period=period)
    }


# ---------------------------------------------------------------------------
# Backward Compatibility Aliases
# ---------------------------------------------------------------------------

calculate_monthly_revenue = calculate_revenue_trends
calculate_top_products = calculate_popular_products
calculate_country_wise_purchasing = calculate_country_purchasing
