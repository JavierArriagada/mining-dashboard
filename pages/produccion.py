import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from dash import html, dcc
import dash_bootstrap_components as dbc
from data.mining_data import get_production_df

PLOTLY_TEMPLATE = "plotly_dark"
CARD_BG = "#161b22"
GRID_COLOR = "#30363d"

def plot_cfg(fig, title=""):
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor=CARD_BG,
        plot_bgcolor=CARD_BG,
        margin=dict(l=10, r=10, t=40, b=10),
        font=dict(color="#c9d1d9", size=11),
        title=dict(text=title, font=dict(size=13, color="#8b949e")),
        xaxis=dict(gridcolor=GRID_COLOR),
        yaxis=dict(gridcolor=GRID_COLOR),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    return fig


def layout():
    prod = get_production_df()
    prod["month"] = pd.to_datetime(prod["date"]).dt.to_period("M").dt.to_timestamp()
    monthly = prod.groupby("month").agg(
        tonnage=("tonnage", "sum"),
        grade_cu=("grade_cu", "mean"),
        grade_au=("grade_au", "mean"),
        recovery_cu=("recovery_cu", "mean"),
        recovery_au=("recovery_au", "mean"),
        fine_cu_t=("fine_cu_t", "sum"),
        fine_au_oz=("fine_au_oz", "sum"),
    ).reset_index()

    # ── Fig 1: Tonelaje + Ley Cu diaria (últimos 90 días) ───────────────────
    recent = prod.tail(90)
    fig_daily = go.Figure()
    fig_daily.add_bar(
        x=recent["date"], y=recent["tonnage"],
        name="Tonelaje (t)", marker_color="#30363d",
    )
    fig_daily.add_scatter(
        x=recent["date"], y=recent["grade_cu"],
        name="Ley Cu (%)", yaxis="y2",
        line=dict(color="#e8a020", width=2),
    )
    fig_daily.update_layout(
        title="Tonelaje y Ley Cu · Últimos 90 Días",
        yaxis=dict(title="Tonelaje (t)", gridcolor=GRID_COLOR),
        yaxis2=dict(title="Ley Cu (%)", overlaying="y", side="right", gridcolor=GRID_COLOR),
    )
    plot_cfg(fig_daily)

    # ── Fig 2: Curva de recuperación mensual ─────────────────────────────────
    fig_rec = go.Figure()
    fig_rec.add_scatter(
        x=monthly["month"], y=monthly["recovery_cu"],
        name="Rec. Cu (%)", line=dict(color="#2ea44f", width=2.5), mode="lines+markers",
    )
    fig_rec.add_scatter(
        x=monthly["month"], y=monthly["recovery_au"],
        name="Rec. Au (%)", line=dict(color="#ffd700", width=2.5, dash="dot"), mode="lines+markers",
    )
    fig_rec.add_hline(y=88, line_dash="dash", line_color="#da3633", annotation_text="Meta Cu 88%")
    fig_rec.add_hline(y=82, line_dash="dash", line_color="#ffa500", annotation_text="Meta Au 82%")
    plot_cfg(fig_rec, "Recuperación Metalúrgica Mensual (%)")

    # ── Fig 3: Scatter ley vs tonelaje ───────────────────────────────────────
    fig_scatter = px.scatter(
        prod.sample(200, random_state=1),
        x="tonnage", y="grade_cu", color="recovery_cu",
        color_continuous_scale="Viridis",
        labels={"tonnage": "Tonelaje (t)", "grade_cu": "Ley Cu (%)", "recovery_cu": "Rec. Cu (%)"},
        title="Ley Cu vs Tonelaje (muestra 200 días)",
    )
    plot_cfg(fig_scatter)

    # ── Fig 4: Producción de finos acumulada ─────────────────────────────────
    prod_sorted = prod.sort_values("date")
    fig_acum = go.Figure()
    fig_acum.add_scatter(
        x=prod_sorted["date"],
        y=prod_sorted["fine_cu_t"].cumsum(),
        name="Cu fino acum. (t)",
        fill="tozeroy",
        line=dict(color="#2ea44f"),
        fillcolor="rgba(46,164,79,.15)",
    )
    fig_acum.add_scatter(
        x=prod_sorted["date"],
        y=prod_sorted["fine_au_oz"].cumsum(),
        name="Au fino acum. (oz)",
        fill="tozeroy",
        yaxis="y2",
        line=dict(color="#ffd700"),
        fillcolor="rgba(255,215,0,.08)",
    )
    fig_acum.update_layout(
        title="Producción de Finos Acumulada",
        yaxis=dict(title="Cu fino (t)", gridcolor=GRID_COLOR),
        yaxis2=dict(title="Au fino (oz)", overlaying="y", side="right", gridcolor=GRID_COLOR),
    )
    plot_cfg(fig_acum)

    # ── Fig 5: Box plot ley Cu por trimestre ─────────────────────────────────
    prod["trimestre"] = "T" + pd.to_datetime(prod["date"]).dt.quarter.astype(str)
    fig_box = px.box(
        prod, x="trimestre", y="grade_cu", color="trimestre",
        color_discrete_sequence=["#e8a020", "#2ea44f", "#58a6ff", "#da3633"],
        title="Distribución Ley Cu por Trimestre",
        labels={"grade_cu": "Ley Cu (%)", "trimestre": "Trimestre"},
    )
    plot_cfg(fig_box)

    # ── Fig 6: Heatmap tonelaje semana × hora (sintético) ────────────────────
    weeks = list(range(1, 13))
    days = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    import numpy as np
    heat_data = pd.DataFrame(
        data=np.random.normal(5000, 300, (len(weeks), len(days))).round(0),
        index=[f"S{w}" for w in weeks],
        columns=days,
    )
    fig_heat = px.imshow(
        heat_data, color_continuous_scale="YlOrBr",
        title="Tonelaje Promedio por Día de Semana (Q1)",
        labels=dict(color="t/día"),
    )
    plot_cfg(fig_heat)

    return html.Div([
        html.Div([
            html.H2("Producción"),
            html.P("Análisis detallado de tonelaje, leyes y recuperación metalúrgica · 2024"),
        ], className="page-header"),

        dbc.Row([
            dbc.Col(html.Div([dcc.Graph(figure=fig_daily, config={"displayModeBar": False})], className="chart-card"), md=8),
            dbc.Col(html.Div([dcc.Graph(figure=fig_box, config={"displayModeBar": False})], className="chart-card"), md=4),
        ], className="g-3"),

        dbc.Row([
            dbc.Col(html.Div([dcc.Graph(figure=fig_rec, config={"displayModeBar": False})], className="chart-card"), md=6),
            dbc.Col(html.Div([dcc.Graph(figure=fig_scatter, config={"displayModeBar": False})], className="chart-card"), md=6),
        ], className="g-3"),

        dbc.Row([
            dbc.Col(html.Div([dcc.Graph(figure=fig_acum, config={"displayModeBar": False})], className="chart-card"), md=7),
            dbc.Col(html.Div([dcc.Graph(figure=fig_heat, config={"displayModeBar": False})], className="chart-card"), md=5),
        ], className="g-3"),
    ], style={"padding": "1.5rem"})
