import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from dash import html, dcc
import dash_bootstrap_components as dbc
from data.mining_data import get_safety_df

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
    df = get_safety_df()
    df["month"] = pd.to_datetime(df["date"]).dt.to_period("M").dt.to_timestamp()
    df["week"] = pd.to_datetime(df["date"]).dt.isocalendar().week.astype(int)
    df["dayofweek"] = pd.to_datetime(df["date"]).dt.day_name()

    monthly = df.groupby("month").agg(
        incidentes=("incidentes", "sum"),
        casi_accidentes=("casi_accidentes", "sum"),
        horas_hombre=("horas_hombre", "sum"),
        inspecciones=("inspecciones", "sum"),
    ).reset_index()
    monthly["trir"] = (monthly["incidentes"] * 200_000 / monthly["horas_hombre"]).round(2)

    # ── Fig 1: Días sin accidente (área) ─────────────────────────────────────
    fig_dsa = go.Figure()
    fig_dsa.add_scatter(
        x=df["date"], y=df["dias_sin_accidente"],
        fill="tozeroy",
        line=dict(color="#2ea44f", width=1.5),
        fillcolor="rgba(46,164,79,.2)",
        name="Días sin accidente",
    )
    incidentes_days = df[df["incidentes"] > 0]
    fig_dsa.add_scatter(
        x=incidentes_days["date"],
        y=[0] * len(incidentes_days),
        mode="markers",
        marker=dict(color="#da3633", size=10, symbol="x"),
        name="Incidente registrado",
    )
    plot_cfg(fig_dsa, "Días Sin Accidente Acumulados")

    # ── Fig 2: TRIR mensual ───────────────────────────────────────────────────
    fig_trir = go.Figure()
    fig_trir.add_bar(
        x=monthly["month"], y=monthly["trir"],
        marker_color=[
            "#da3633" if v > 1.5 else "#e8a020" if v > 0.8 else "#2ea44f"
            for v in monthly["trir"]
        ],
        name="TRIR",
    )
    fig_trir.add_hline(y=1.5, line_dash="dash", line_color="#da3633",
                       annotation_text="Límite crítico 1.5")
    fig_trir.add_hline(y=0.8, line_dash="dot", line_color="#e8a020",
                       annotation_text="Meta 0.8")
    plot_cfg(fig_trir, "TRIR – Tasa de Incidencia Total Registrable")

    # ── Fig 3: Casi-accidentes vs inspecciones ────────────────────────────────
    fig_ca = go.Figure()
    fig_ca.add_bar(
        x=monthly["month"], y=monthly["casi_accidentes"],
        name="Casi-Accidentes", marker_color="#e8a020",
    )
    fig_ca.add_scatter(
        x=monthly["month"], y=monthly["inspecciones"],
        name="Inspecciones", yaxis="y2",
        line=dict(color="#58a6ff", width=2), mode="lines+markers",
    )
    fig_ca.update_layout(
        yaxis=dict(title="Casi-Accidentes", gridcolor=GRID_COLOR),
        yaxis2=dict(title="Inspecciones", overlaying="y", side="right", gridcolor=GRID_COLOR),
    )
    plot_cfg(fig_ca, "Casi-Accidentes e Inspecciones Mensuales")

    # ── Fig 4: Heatmap incidentes por semana y día ────────────────────────────
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_labels = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    pivot = df.pivot_table(index="dayofweek", columns="week", values="incidentes", aggfunc="sum")
    pivot = pivot.reindex(day_order).iloc[:, :26]
    pivot.index = day_labels
    fig_heat = px.imshow(
        pivot.fillna(0),
        color_continuous_scale=[[0, "#0d1117"], [0.5, "#3d2f0a"], [1, "#da3633"]],
        title="Distribución de Incidentes: Día × Semana",
        labels=dict(x="Semana", y="Día", color="Incidentes"),
    )
    plot_cfg(fig_heat)

    # ── Fig 5: Categorías de incidentes (sunburst simulado) ──────────────────
    categorias = {
        "Mecánico": 35, "Eléctrico": 18, "Ergonómico": 22,
        "Caída de Rocas": 12, "Incendio/Explosión": 5, "Otros": 8,
    }
    fig_sunburst = go.Figure(go.Pie(
        labels=list(categorias.keys()),
        values=list(categorias.values()),
        hole=0.3,
        marker_colors=["#e8a020", "#58a6ff", "#2ea44f", "#da3633", "#9b59b6", "#8b949e"],
    ))
    fig_sunburst.update_layout(
        title="Distribución por Tipo de Incidente",
        paper_bgcolor=CARD_BG,
        font=dict(color="#c9d1d9"),
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )

    # ── Fig 6: Horas-hombre acumuladas ────────────────────────────────────────
    df_sorted = df.sort_values("date")
    fig_hh = go.Figure()
    fig_hh.add_scatter(
        x=df_sorted["date"],
        y=df_sorted["horas_hombre"].cumsum(),
        fill="tozeroy",
        line=dict(color="#58a6ff"),
        fillcolor="rgba(88,166,255,.15)",
        name="Horas-Hombre Acum.",
    )
    plot_cfg(fig_hh, "Horas-Hombre Trabajadas Acumuladas")

    # KPI banner seguridad
    total_inc = int(df["incidentes"].sum())
    total_ca = int(df["casi_accidentes"].sum())
    dsa_actual = int(df["dias_sin_accidente"].iloc[-1])
    trir_anual = round(total_inc * 200_000 / df["horas_hombre"].sum(), 2)

    safety_kpis = dbc.Row([
        dbc.Col(html.Div([
            html.Div("✅", className="kpi-icon"),
            html.Div(str(dsa_actual), className="kpi-value", style={"color": "#2ea44f"}),
            html.Div("Días Sin Accidente", className="kpi-label"),
        ], className="kpi-card"), xs=6, md=3),
        dbc.Col(html.Div([
            html.Div("⚠️", className="kpi-icon"),
            html.Div(str(total_inc), className="kpi-value", style={"color": "#da3633"}),
            html.Div("Incidentes Totales", className="kpi-label"),
        ], className="kpi-card"), xs=6, md=3),
        dbc.Col(html.Div([
            html.Div("🔶", className="kpi-icon"),
            html.Div(str(total_ca), className="kpi-value", style={"color": "#e8a020"}),
            html.Div("Casi-Accidentes", className="kpi-label"),
        ], className="kpi-card"), xs=6, md=3),
        dbc.Col(html.Div([
            html.Div("📊", className="kpi-icon"),
            html.Div(str(trir_anual), className="kpi-value", style={"color": "#58a6ff"}),
            html.Div("TRIR Anual", className="kpi-label"),
        ], className="kpi-card"), xs=6, md=3),
    ], className="g-3 mb-4")

    return html.Div([
        html.Div([
            html.H2("Seguridad"),
            html.P("Indicadores de seguridad, incidentes y desempeño HSE · 2024"),
        ], className="page-header"),

        safety_kpis,

        dbc.Row([
            dbc.Col(html.Div([dcc.Graph(figure=fig_dsa, config={"displayModeBar": False})], className="chart-card"), md=8),
            dbc.Col(html.Div([dcc.Graph(figure=fig_sunburst, config={"displayModeBar": False})], className="chart-card"), md=4),
        ], className="g-3"),

        dbc.Row([
            dbc.Col(html.Div([dcc.Graph(figure=fig_trir, config={"displayModeBar": False})], className="chart-card"), md=6),
            dbc.Col(html.Div([dcc.Graph(figure=fig_ca, config={"displayModeBar": False})], className="chart-card"), md=6),
        ], className="g-3"),

        dbc.Row([
            dbc.Col(html.Div([dcc.Graph(figure=fig_heat, config={"displayModeBar": False})], className="chart-card"), md=7),
            dbc.Col(html.Div([dcc.Graph(figure=fig_hh, config={"displayModeBar": False})], className="chart-card"), md=5),
        ], className="g-3"),
    ], style={"padding": "1.5rem"})
