import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from dash import html, dcc
import dash_bootstrap_components as dbc
from data.mining_data import get_production_df, get_safety_df, get_kpis

PLOTLY_TEMPLATE = "plotly_dark"
CARD_BG = "#161b22"
GRID_COLOR = "#30363d"

def plot_cfg(fig):
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor=CARD_BG,
        plot_bgcolor=CARD_BG,
        margin=dict(l=10, r=10, t=30, b=10),
        font=dict(color="#c9d1d9", size=11),
        xaxis=dict(gridcolor=GRID_COLOR, showgrid=True),
        yaxis=dict(gridcolor=GRID_COLOR, showgrid=True),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    return fig


def layout():
    prod = get_production_df()
    safety = get_safety_df()
    kpis = get_kpis()

    # Resample mensual
    prod["month"] = pd.to_datetime(prod["date"]).dt.to_period("M").dt.to_timestamp()
    monthly = prod.groupby("month").agg(
        tonnage=("tonnage", "sum"),
        fine_cu_t=("fine_cu_t", "sum"),
        fine_au_oz=("fine_au_oz", "sum"),
    ).reset_index()

    # ── Fig 1: Tonelaje mensual ──────────────────────────────────────────────
    fig_ton = go.Figure()
    fig_ton.add_bar(
        x=monthly["month"], y=monthly["tonnage"],
        name="Tonelaje", marker_color="#e8a020",
    )
    fig_ton.add_scatter(
        x=monthly["month"], y=monthly["tonnage"].rolling(3, min_periods=1).mean(),
        name="Promedio móvil", line=dict(color="#58a6ff", width=2),
    )
    fig_ton.update_layout(title="Tonelaje Mineral Procesado (mensual)", barmode="overlay")
    plot_cfg(fig_ton)

    # ── Fig 2: Producción de finos ───────────────────────────────────────────
    fig_finos = go.Figure()
    fig_finos.add_bar(
        x=monthly["month"], y=monthly["fine_cu_t"],
        name="Cu fino (t)", marker_color="#2ea44f", yaxis="y",
    )
    fig_finos.add_scatter(
        x=monthly["month"], y=monthly["fine_au_oz"],
        name="Au fino (oz)", line=dict(color="#ffd700", width=2), yaxis="y2",
    )
    fig_finos.update_layout(
        title="Producción de Finos",
        yaxis=dict(title="Cu fino (t)", gridcolor=GRID_COLOR),
        yaxis2=dict(title="Au fino (oz)", overlaying="y", side="right", gridcolor=GRID_COLOR),
    )
    plot_cfg(fig_finos)

    # ── Fig 3: Gauge días sin accidente ─────────────────────────────────────
    dsa = kpis["dias_sin_accidente"]
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=dsa,
        delta={"reference": 200, "valueformat": ".0f"},
        title={"text": "Días Sin Accidente", "font": {"size": 14, "color": "#c9d1d9"}},
        gauge={
            "axis": {"range": [0, 365], "tickcolor": "#8b949e"},
            "bar": {"color": "#2ea44f"},
            "bgcolor": "#0d1117",
            "steps": [
                {"range": [0, 90], "color": "#3d1212"},
                {"range": [90, 200], "color": "#3d2f0a"},
                {"range": [200, 365], "color": "#1a4731"},
            ],
            "threshold": {"line": {"color": "#e8a020", "width": 3}, "value": dsa},
        },
        number={"font": {"color": "#2ea44f", "size": 40}},
    ))
    fig_gauge.update_layout(
        paper_bgcolor=CARD_BG,
        margin=dict(l=20, r=20, t=50, b=20),
    )

    # ── Fig 4: Incidentes acumulados ─────────────────────────────────────────
    safety["month"] = pd.to_datetime(safety["date"]).dt.to_period("M").dt.to_timestamp()
    safety_m = safety.groupby("month").agg(
        incidentes=("incidentes", "sum"),
        casi_accidentes=("casi_accidentes", "sum"),
    ).reset_index()
    fig_safety = px.bar(
        safety_m, x="month", y=["incidentes", "casi_accidentes"],
        color_discrete_map={"incidentes": "#da3633", "casi_accidentes": "#e8a020"},
        title="Incidentes y Casi-Accidentes Mensuales",
        labels={"value": "Cantidad", "month": "Mes", "variable": "Tipo"},
        barmode="group",
    )
    plot_cfg(fig_safety)

    # ── KPI Cards ────────────────────────────────────────────────────────────
    kpi_data = [
        ("⛏", "Tonelaje Total", kpis["total_ton"], "#e8a020"),
        ("🔵", "Ley Cu", kpis["avg_grade_cu"], "#58a6ff"),
        ("🟢", "Cu Fino", kpis["total_fine_cu"], "#2ea44f"),
        ("🟡", "Au Fino", kpis["total_fine_au"], "#ffd700"),
        ("✅", "Días Sin Acc.", str(kpis["dias_sin_accidente"]), "#2ea44f"),
        ("⚠️", "Incidentes", str(kpis["total_incidentes"]), "#da3633"),
    ]

    kpi_cards = dbc.Row(
        [
            dbc.Col(
                html.Div([
                    html.Div(icon, className="kpi-icon"),
                    html.Div(val, className="kpi-value", style={"color": color}),
                    html.Div(label, className="kpi-label"),
                ], className="kpi-card"),
                xs=6, sm=4, md=2,
            )
            for icon, label, val, color in kpi_data
        ],
        className="g-3 mb-4",
    )

    return html.Div([
        html.Div([
            html.H2("Resumen Operacional"),
            html.P("Vista consolidada del desempeño de la operación minera · Año 2024"),
        ], className="page-header"),

        kpi_cards,

        dbc.Row([
            dbc.Col(html.Div([
                html.Div("Tonelaje Mensual", className="chart-title"),
                dcc.Graph(figure=fig_ton, config={"displayModeBar": False}),
            ], className="chart-card"), md=8),
            dbc.Col(html.Div([
                html.Div("Días Sin Accidente", className="chart-title"),
                dcc.Graph(figure=fig_gauge, config={"displayModeBar": False}),
            ], className="chart-card"), md=4),
        ], className="g-3"),

        dbc.Row([
            dbc.Col(html.Div([
                html.Div("Producción de Finos", className="chart-title"),
                dcc.Graph(figure=fig_finos, config={"displayModeBar": False}),
            ], className="chart-card"), md=6),
            dbc.Col(html.Div([
                html.Div("Registro de Seguridad", className="chart-title"),
                dcc.Graph(figure=fig_safety, config={"displayModeBar": False}),
            ], className="chart-card"), md=6),
        ], className="g-3"),
    ], style={"padding": "1.5rem"})
