"""
RetainIQ — Module 3: Customer Purchase Analytics API
Simple Flask REST API service exposing customer purchase analytics.

Assigned Developer: Mahad
"""

import sys
from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd

# Add backend directory to sys.path so imports work seamlessly
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from purchase_analytics import (
    calculate_purchase_metrics,
    calculate_repeat_customers,
    calculate_purchase_frequency,
    calculate_buying_intervals,
    calculate_revenue_trends,
    calculate_top_spending_customers,
    calculate_popular_products,
    calculate_country_purchasing,
    get_purchase_analytics_summary
)

# Global dataset cache
_DATASET = None


def get_dataset():
    """Load and cache the cleaned retail dataset."""
    global _DATASET
    if _DATASET is None:
        file_path = backend_dir.parent / "data" / "Cleaned_Online_Retail.csv"
        if not file_path.exists():
            raise FileNotFoundError(f"Dataset not found at: {file_path}")
        _DATASET = pd.read_csv(file_path)
    return _DATASET


def create_app(test_df=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    CORS(app)

    def load_df():
        return test_df if test_df is not None else get_dataset()

    @app.errorhandler(ValueError)
    def handle_value_error(e):
        """Handle invalid parameters gracefully with HTTP 400."""
        return jsonify({"status": "error", "message": str(e)}), 400

    @app.route("/api/health", methods=["GET"])
    def health():
        """Health check endpoint."""
        try:
            df = load_df()
            return jsonify({
                "status": "healthy",
                "service": "RetainIQ Module 3 API",
                "records": len(df)
            }), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/api/purchase-analytics/overview", methods=["GET"])
    def overview():
        """Overview metrics for completed orders."""
        period = request.args.get("period", "all")
        df = load_df()
        return jsonify({
            "period": period,
            "metrics": calculate_purchase_metrics(df, period),
            "repeat_customers": calculate_repeat_customers(df, period),
            "purchase_frequency": calculate_purchase_frequency(df, period),
            "buying_intervals_days": calculate_buying_intervals(df, period)
        }), 200

    @app.route("/api/purchase-analytics/revenue-trends", methods=["GET"])
    def revenue_trends():
        """Monthly revenue trends."""
        period = request.args.get("period", "all")
        df = load_df()
        return jsonify({
            "period": period,
            "data": calculate_revenue_trends(df, period)
        }), 200

    @app.route("/api/purchase-analytics/top-customers", methods=["GET"])
    def top_customers():
        """Top-spending customers."""
        period = request.args.get("period", "all")
        limit = request.args.get("limit", 10, type=int)
        df = load_df()
        return jsonify({
            "period": period,
            "data": calculate_top_spending_customers(df, limit=limit, period=period)
        }), 200

    @app.route("/api/purchase-analytics/popular-products", methods=["GET"])
    def popular_products():
        """Most popular products by quantity sold."""
        period = request.args.get("period", "all")
        limit = request.args.get("limit", 10, type=int)
        df = load_df()
        return jsonify({
            "period": period,
            "data": calculate_popular_products(df, limit=limit, period=period)
        }), 200

    @app.route("/api/purchase-analytics/country-purchasing", methods=["GET"])
    def country_purchasing():
        """Country-wise purchasing and revenue."""
        period = request.args.get("period", "all")
        limit = request.args.get("limit", 10, type=int)
        df = load_df()
        return jsonify({
            "period": period,
            "data": calculate_country_purchasing(df, limit=limit, period=period)
        }), 200

    @app.route("/api/purchase-analytics/summary", methods=["GET"])
    def summary():
        """Consolidated summary for dashboard integration."""
        period = request.args.get("period", "all")
        df = load_df()
        return jsonify(get_purchase_analytics_summary(df, period)), 200

    return app


app = create_app()

if __name__ == "__main__":
    print("Starting RetainIQ Module 3 API on http://127.0.0.1:5000 ...")
    app.run(host="127.0.0.1", port=5000, debug=True)
