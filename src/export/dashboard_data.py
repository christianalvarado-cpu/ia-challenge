"""Generate a self-contained HTML dashboard from the comercial Parquet dataset."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
COMERCIAL_PATH = PROJECT_ROOT / "data" / "analytics" / "comercial"
DASHBOARD_PATH = PROJECT_ROOT / "dashboard" / "index.html"


def _money(value: float) -> float:
    return round(float(value or 0), 2)


def load_comercial_dataset(path: Path = COMERCIAL_PATH) -> pd.DataFrame:
    """Load the comercial Parquet dataset as a pandas DataFrame."""
    if not path.exists():
        raise FileNotFoundError(f"Missing comercial Parquet dataset: {path}")
    df = pd.read_parquet(path)
    if df.empty:
        raise ValueError(f"Comercial dataset is empty: {path}")
    return df


def build_dashboard_payload(df: pd.DataFrame) -> dict[str, Any]:
    """Build all aggregates required by the HTML dashboard."""
    required = {"sale_date", "subtotal", "shop_name", "product_name", "customer_status"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required comercial columns for dashboard: {sorted(missing)}")

    data = df.copy()
    data["sale_date"] = pd.to_datetime(data["sale_date"]).dt.date
    data["subtotal"] = pd.to_numeric(data["subtotal"], errors="coerce").fillna(0.0)
    data["shop_name"] = data["shop_name"].fillna("Sin tienda")
    data["product_name"] = data["product_name"].fillna("Sin producto")
    data["customer_status"] = data["customer_status"].fillna("Sin estado")

    max_date = data["sale_date"].max()
    min_date = data["sale_date"].min()
    last_30_start = pd.Timestamp(max_date) - pd.Timedelta(days=29)
    full_range = pd.date_range(last_30_start, pd.Timestamp(max_date), freq="D")

    daily = (
        data[data["sale_date"] >= last_30_start.date()]
        .groupby("sale_date", as_index=True)["subtotal"]
        .sum()
        .reindex([day.date() for day in full_range], fill_value=0.0)
        .reset_index()
    )
    daily.columns = ["sale_date", "total_sold"]

    sales_by_shop = (
        data.groupby("shop_name", as_index=False)["subtotal"]
        .sum()
        .sort_values("subtotal", ascending=False)
    )

    sales_by_product = (
        data.groupby("product_name", as_index=False)["subtotal"]
        .sum()
        .sort_values("subtotal", ascending=False)
    )

    sales_by_customer_status = (
        data.groupby("customer_status", as_index=False)["subtotal"]
        .sum()
        .sort_values("subtotal", ascending=False)
    )

    return {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "source_dataset": "data/analytics/comercial",
            "row_count": int(len(data)),
        },
        "kpis": {
            "total_sold": _money(data["subtotal"].sum()),
            "total_rows": int(len(data)),
            "date_start": str(min_date),
            "date_end": str(max_date),
        },
        "daily_sales_last_30_days": [
            {"sale_date": str(row.sale_date), "total_sold": _money(row.total_sold)}
            for row in daily.itertuples(index=False)
        ],
        "sales_by_shop": [
            {"shop_name": str(row.shop_name), "total_sold": _money(row.subtotal)}
            for row in sales_by_shop.itertuples(index=False)
        ],
        "sales_by_product": [
            {"product_name": str(row.product_name), "total_sold": _money(row.subtotal)}
            for row in sales_by_product.itertuples(index=False)
        ],
        "sales_by_customer_status": [
            {"customer_status": str(row.customer_status), "total_sold": _money(row.subtotal)}
            for row in sales_by_customer_status.itertuples(index=False)
        ],
    }


def render_dashboard_html(payload: dict[str, Any]) -> str:
    """Render a self-contained dashboard HTML document."""
    dashboard_json = json.dumps(payload, ensure_ascii=False, indent=2)
    template = """<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Dashboard Comercial</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    :root {
      color-scheme: light;
      --bg: #f6f7f9;
      --panel: #ffffff;
      --ink: #17202a;
      --muted: #657080;
      --line: #d9dee7;
      --accent: #2563eb;
      --shadow: 0 1px 3px rgba(15, 23, 42, 0.12);
    }
    * { box-sizing: border-box; }
    body { margin: 0; font-family: Arial, Helvetica, sans-serif; background: var(--bg); color: var(--ink); }
    header { padding: 28px 32px 18px; border-bottom: 1px solid var(--line); background: var(--panel); }
    h1 { margin: 0 0 8px; font-size: 28px; }
    .subtitle { margin: 0; color: var(--muted); }
    main { width: min(1180px, calc(100% - 32px)); margin: 22px auto 36px; }
    .grid { display: grid; grid-template-columns: repeat(12, 1fr); gap: 16px; }
    .card { background: var(--panel); border: 1px solid var(--line); border-radius: 8px; box-shadow: var(--shadow); padding: 18px; }
    .kpi { grid-column: span 4; }
    .wide { grid-column: span 12; }
    .half { grid-column: span 6; }
    .label { color: var(--muted); font-size: 13px; margin-bottom: 8px; }
    .value { font-size: 34px; font-weight: 700; letter-spacing: 0; }
    .small { color: var(--muted); font-size: 13px; margin-top: 6px; }
    h2 { margin: 0 0 14px; font-size: 18px; }
    .chart-wrap { height: 340px; }
    .chart-wrap.small { height: 320px; }
    footer { color: var(--muted); font-size: 12px; margin-top: 18px; }
    @media (max-width: 850px) {
      header { padding: 22px 18px 16px; }
      .kpi, .half, .wide { grid-column: span 12; }
      .chart-wrap, .chart-wrap.small { height: 300px; }
    }
  </style>
</head>
<body>
  <header>
    <h1>Dashboard Comercial</h1>
    <p class="subtitle">Analisis de ventas construido desde el dataset Parquet comercial.</p>
  </header>
  <main>
    <section class="grid">
      <article class="card kpi">
        <div class="label">Total vendido</div>
        <div class="value" id="totalSold">$0.00</div>
        <div class="small" id="dateRange"></div>
      </article>
      <article class="card kpi">
        <div class="label">Filas analiticas</div>
        <div class="value" id="totalRows">0</div>
        <div class="small">Grano: linea de venta</div>
      </article>
      <article class="card kpi">
        <div class="label">Dataset fuente</div>
        <div class="value" style="font-size: 20px;" id="sourceDataset">comercial</div>
        <div class="small" id="generatedAt"></div>
      </article>
      <article class="card wide">
        <h2>Tendencia diaria de ventas - ultimos 30 dias</h2>
        <div class="chart-wrap"><canvas id="dailySalesChart"></canvas></div>
      </article>
      <article class="card half">
        <h2>Participacion de ventas por tienda</h2>
        <div class="chart-wrap small"><canvas id="shopPieChart"></canvas></div>
      </article>
      <article class="card half">
        <h2>Ventas por producto</h2>
        <div class="chart-wrap small"><canvas id="productBarChart"></canvas></div>
      </article>
      <article class="card wide">
        <h2>Ventas por estado de cliente</h2>
        <div class="chart-wrap small"><canvas id="customerStatusChart"></canvas></div>
      </article>
    </section>
    <footer>Archivo local: dashboard/index.html</footer>
  </main>

  <script>
    const dashboardData = __DASHBOARD_JSON__;

    const currency = new Intl.NumberFormat('es-EC', { style: 'currency', currency: 'USD' });
    const colors = ['#2563eb', '#0f766e', '#dc2626', '#9333ea', '#ca8a04', '#0891b2', '#4f46e5', '#16a34a'];

    document.getElementById('totalSold').textContent = currency.format(dashboardData.kpis.total_sold);
    document.getElementById('totalRows').textContent = dashboardData.kpis.total_rows.toLocaleString('es-EC');
    document.getElementById('dateRange').textContent = `${dashboardData.kpis.date_start} a ${dashboardData.kpis.date_end}`;
    document.getElementById('sourceDataset').textContent = dashboardData.metadata.source_dataset;
    document.getElementById('generatedAt').textContent = `Generado: ${dashboardData.metadata.generated_at}`;

    new Chart(document.getElementById('dailySalesChart'), {
      type: 'line',
      data: {
        labels: dashboardData.daily_sales_last_30_days.map(row => row.sale_date),
        datasets: [{ label: 'Ventas diarias', data: dashboardData.daily_sales_last_30_days.map(row => row.total_sold), borderColor: '#2563eb', backgroundColor: 'rgba(37, 99, 235, 0.12)', fill: true, tension: 0.25, pointRadius: 3 }]
      },
      options: { responsive: true, maintainAspectRatio: false, scales: { y: { ticks: { callback: value => currency.format(value) } } }, plugins: { tooltip: { callbacks: { label: ctx => currency.format(ctx.raw) } } } }
    });

    new Chart(document.getElementById('shopPieChart'), {
      type: 'pie',
      data: { labels: dashboardData.sales_by_shop.map(row => row.shop_name), datasets: [{ data: dashboardData.sales_by_shop.map(row => row.total_sold), backgroundColor: colors }] },
      options: { responsive: true, maintainAspectRatio: false, plugins: { tooltip: { callbacks: { label: ctx => `${ctx.label}: ${currency.format(ctx.raw)}` } } } }
    });

    new Chart(document.getElementById('productBarChart'), {
      type: 'bar',
      data: { labels: dashboardData.sales_by_product.map(row => row.product_name), datasets: [{ label: 'Ventas por producto', data: dashboardData.sales_by_product.map(row => row.total_sold), backgroundColor: '#0f766e' }] },
      options: { responsive: true, maintainAspectRatio: false, scales: { y: { ticks: { callback: value => currency.format(value) } } }, plugins: { legend: { display: false }, tooltip: { callbacks: { label: ctx => currency.format(ctx.raw) } } } }
    });

    new Chart(document.getElementById('customerStatusChart'), {
      type: 'bar',
      data: { labels: dashboardData.sales_by_customer_status.map(row => row.customer_status), datasets: [{ label: 'Ventas por estado de cliente', data: dashboardData.sales_by_customer_status.map(row => row.total_sold), backgroundColor: '#9333ea' }] },
      options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false, scales: { x: { ticks: { callback: value => currency.format(value) } } }, plugins: { legend: { display: false }, tooltip: { callbacks: { label: ctx => currency.format(ctx.raw) } } } }
    });
  </script>
</body>
</html>
"""
    return template.replace("__DASHBOARD_JSON__", dashboard_json)


def write_dashboard(html: str, output_path: Path = DASHBOARD_PATH) -> None:
    """Write the final dashboard HTML."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")


def generate_dashboard(
    comercial_path: Path = COMERCIAL_PATH,
    output_path: Path = DASHBOARD_PATH,
) -> dict[str, Any]:
    """Generate dashboard/index.html and return the payload used."""
    df = load_comercial_dataset(comercial_path)
    payload = build_dashboard_payload(df)
    html = render_dashboard_html(payload)
    write_dashboard(html, output_path)
    return payload


if __name__ == "__main__":
    payload = generate_dashboard()
    print(f"Dashboard written to {DASHBOARD_PATH}")
    print(f"Rows: {payload['metadata']['row_count']}")
    print(f"Total sold: {payload['kpis']['total_sold']}")
