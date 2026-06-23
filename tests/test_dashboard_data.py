"""Tests for dashboard aggregate generation."""

import pandas as pd

from src.export.dashboard_data import build_dashboard_payload, render_dashboard_html


def test_build_dashboard_payload_aggregates_required_components():
    df = pd.DataFrame(
        [
            {
                "sale_date": "2025-06-01",
                "subtotal": 10.0,
                "shop_name": "Shop A",
                "product_name": "Prod 1",
                "customer_status": "activo",
            },
            {
                "sale_date": "2025-06-02",
                "subtotal": 20.5,
                "shop_name": "Shop A",
                "product_name": "Prod 2",
                "customer_status": "activo",
            },
            {
                "sale_date": "2025-06-02",
                "subtotal": 5.25,
                "shop_name": None,
                "product_name": "Prod 1",
                "customer_status": None,
            },
        ]
    )

    payload = build_dashboard_payload(df)

    assert payload["kpis"]["total_sold"] == 35.75
    assert payload["kpis"]["total_rows"] == 3
    assert len(payload["daily_sales_last_30_days"]) == 30
    assert payload["daily_sales_last_30_days"][-1] == {"sale_date": "2025-06-02", "total_sold": 25.75}
    assert payload["sales_by_shop"][0] == {"shop_name": "Shop A", "total_sold": 30.5}
    assert {row["shop_name"] for row in payload["sales_by_shop"]} == {"Shop A", "Sin tienda"}
    assert payload["sales_by_product"][0] == {"product_name": "Prod 2", "total_sold": 20.5}
    assert payload["sales_by_customer_status"][0] == {"customer_status": "activo", "total_sold": 30.5}
    assert {row["customer_status"] for row in payload["sales_by_customer_status"]} == {
        "activo",
        "Sin estado",
    }


def test_render_dashboard_html_embeds_data_and_chart_ids():
    payload = {
        "metadata": {
            "generated_at": "2026-01-01T00:00:00+00:00",
            "source_dataset": "data/analytics/comercial",
            "row_count": 1,
        },
        "kpis": {
            "total_sold": 10.0,
            "total_rows": 1,
            "date_start": "2025-06-01",
            "date_end": "2025-06-01",
        },
        "daily_sales_last_30_days": [{"sale_date": "2025-06-01", "total_sold": 10.0}],
        "sales_by_shop": [{"shop_name": "Shop A", "total_sold": 10.0}],
        "sales_by_product": [{"product_name": "Prod 1", "total_sold": 10.0}],
        "sales_by_customer_status": [{"customer_status": "activo", "total_sold": 10.0}],
    }

    html = render_dashboard_html(payload)

    assert "const dashboardData" in html
    assert "dailySalesChart" in html
    assert "shopPieChart" in html
    assert "productBarChart" in html
    assert "customerStatusChart" in html
    assert "Total vendido" in html
