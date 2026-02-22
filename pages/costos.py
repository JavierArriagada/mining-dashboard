import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from dash import html, dcc
import dash_bootstrap_components as dbc
from data.mining_data import get_costs_df, get_production_df

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
    costs = get_costs_df()
    prod = get_production_df()

    total_by_cat = costs.groupby("categoria")["costo"].sum().reset_index()
    monthly_total = costs.groupby("mes")["costo"].sum().reset_index()
    monthly_cat = costs.pivot_table(index="mes", columns="categoria", values="costo", aggfunc="sum").reset_index()

    # Costo por tonelada
    prod["month"] = pd.to_datetime(prod["date"]).dt.to_period("M").dt.to_timestamp()
    monthly_ton = prod.groupby("month")["tonnage"].sum().reset_index()
    monthly_ton.columns = ["mes", "tonnage"]
    cost_per_ton = monthly_total.merge(monthly_ton, on="mes")
    cost_per_ton["costo_t"] = (cost_per_ton["costo"] / cost_per_ton["tonnage"]).round(2)

    # ── Fig 1: Distribución de costos (donut) ────────────────────────────────
    fig_donut = go.Figure(go.Pie(
        labels=total_by_cat["categoria"],
        values=total_by_cat["costo"],
        hole=0.5,
        marker_colors=["#e8a020", "#2ea44f", "#58a6ff", "#da3633", "#9b59b6", "#8b949e"],
        textinfo="label+percent",
        hovertemplate="%{label}<br>$%{value:,.0f}<extra></extra>",
    ))
    fig_donut.update_layout(
        title="Distribución de Costos Anual",
        paper_bgcolor=CARD_BG,
        font=dict(color="#c9d1d9"),
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )

    # ── Fig 2: Costo total mensual (línea + área) ────────────────────────────
    fig_monthly = go.Figure()
    fig_monthly.add_scatter(
        x=monthly_total["mes"], y=monthly_total["costo"],
        fill="tozeroy",
        line=dict(color="#58a6ff", width=2),
        fillcolor="rgba(88,166,255,.15)",
        name="Costo Total",
        hovertemplate="$%{y:,.0f}<extra></extra>",
    )
    budget_line = monthly_total["costo"].mean() * 1.05
    fig_monthly.add_hline(y=budget_line, line_dash="dash", line_color="#da3633",
                          annotation_text="Presupuesto +5%", annotation_font_color="#da3633")
    plot_cfg(fig_monthly, "Costo Total Mensual (USD)")

    # ── Fig 3: Stack bar por categoría ───────────────────────────────────────
    cols = [c for c in monthly_cat.columns if c != "mes"]
    colors = ["#e8a020", "#2ea44f", "#58a6ff", "#da3633", "#9b59b6", "#8b949e"]
    fig_stack = go.Figure()
    for col, color in zip(cols, colors):
        fig_stack.add_bar(
            x=monthly_cat["mes"], y=monthly_cat[col],
            name=col, marker_color=color,
        )
    fig_stack.update_layout(barmode="stack")
    plot_cfg(fig_stack, "Costos por Categoría Mensual (USD)")

    # ── Fig 4: Costo por tonelada procesada ──────────────────────────────────
    fig_cpt = go.Figure()
    fig_cpt.add_bar(
        x=cost_per_ton["mes"], y=cost_per_ton["costo_t"],
        marker_color=[
            "#2ea44f" if v < 1300 else "#e8a020" if v < 1500 else "#da3633"
            for v in cost_per_ton["costo_t"]
        ],
        name="$/t",
        hovertemplate="$%{y:.1f}/t<extra></extra>",
    )
    fig_cpt.add_hline(y=1300, line_dash="dot", line_color="#2ea44f",
                      annotation_text="Meta $1,300/t")
    plot_cfg(fig_cpt, "Costo por Tonelada Procesada (USD/t)")

    # ── Fig 5: Waterfall variación vs promedio ────────────────────────────────
    avg = monthly_total["costo"].mean()
    diff = (monthly_total["costo"] - avg).values
    mes_labels = monthly_total["mes"].dt.strftime("%b").tolist()
    colors_wf = ["#2ea44f" if d < 0 else "#da3633" for d in diff]

    fig_wf = go.Figure(go.Bar(
        x=mes_labels, y=diff,
        marker_color=colors_wf,
        text=[f"${d:+,.0f}" for d in diff],
        textposition="outside",
        textfont=dict(size=9),
    ))
    fig_wf.add_hline(y=0, line_color="#c9d1d9", line_width=0.5)
    plot_cfg(fig_wf, "Variación Mensual vs Costo Promedio (USD)")

    # ── Fig 6: Scatter costo vs tonelaje ─────────────────────────────────────
    fig_scatter = px.scatter(
        cost_per_ton,
        x="tonnage", y="costo",
        size="costo_t",
        color="costo_t",
        color_continuous_scale="RdYlGn_r",
        hover_data={"mes": True, "costo_t": ":.1f"},
        title="Costo Total vs Tonelaje Mensual",
        labels={"tonnage": "Tonelaje (t/mes)", "costo": "Costo Total (USD)", "costo_t": "$/t"},
    )
    plot_cfg(fig_scatter)

    # KPI banner costos
    total_costo = costs["costo"].sum()
    avg_cpt = cost_per_ton["costo_t"].mean()
    max_cat = total_by_cat.loc[total_by_cat["costo"].idxmax(), "categoria"]
    max_cat_pct = round(total_by_cat["costo"].max() / total_by_cat["costo"].sum() * 100, 1)

    cost_kpis = dbc.Row([
        dbc.Col(html.Div([
            html.Div("💰", className="kpi-icon"),
            html.Div(f"${total_costo/1e6:.1f}M", className="kpi-value", style={"color": "#58a6ff"}),
            html.Div("Costo Total Anual", className="kpi-label"),
        ], className="kpi-card"), xs=6, md=3),
        dbc.Col(html.Div([
            html.Div("⚖️", className="kpi-icon"),
            html.Div(f"${avg_cpt:.0f}", className="kpi-value", style={"color": "#e8a020"}),
            html.Div("Costo Prom. / Tonelada", className="kpi-label"),
        ], className="kpi-card"), xs=6, md=3),
        dbc.Col(html.Div([
            html.Div("📦", className="kpi-icon"),
            html.Div(max_cat, className="kpi-value", style={"color": "#c9d1d9", "fontSize": "1.1rem"}),
            html.Div(f"Mayor costo ({max_cat_pct}%)", className="kpi-label"),
        ], className="kpi-card"), xs=6, md=3),
        dbc.Col(html.Div([
            html.Div("📅", className="kpi-icon"),
            html.Div(f"${monthly_total['costo'].mean()/1e6:.2f}M", className="kpi-value", style={"color": "#2ea44f"}),
            html.Div("Costo Promedio Mensual", className="kpi-label"),
        ], className="kpi-card"), xs=6, md=3),
    ], className="g-3 mb-4")

    return html.Div([
        html.Div([
            html.H2("Costos"),
            html.P("Análisis de costos operacionales por categoría y período · 2024"),
        ], className="page-header"),

        cost_kpis,

        dbc.Row([
            dbc.Col(html.Div([dcc.Graph(figure=fig_donut, config={"displayModeBar": False})], className="chart-card"), md=4),
            dbc.Col(html.Div([dcc.Graph(figure=fig_monthly, config={"displayModeBar": False})], className="chart-card"), md=8),
        ], className="g-3"),

        dbc.Row([
            dbc.Col(html.Div([dcc.Graph(figure=fig_stack, config={"displayModeBar": False})], className="chart-card"), md=6),
            dbc.Col(html.Div([dcc.Graph(figure=fig_cpt, config={"displayModeBar": False})], className="chart-card"), md=6),
        ], className="g-3"),

        dbc.Row([
            dbc.Col(html.Div([dcc.Graph(figure=fig_wf, config={"displayModeBar": False})], className="chart-card"), md=7),
            dbc.Col(html.Div([dcc.Graph(figure=fig_scatter, config={"displayModeBar": False})], className="chart-card"), md=5),
        ], className="g-3"),
    ], style={"padding": "1.5rem"})
