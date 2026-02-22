"""
pages/molinos.py
────────────────────────────────────────────────────────────────────────────────
Dashboard de monitoreo de 4 molinos HPGR (High Pressure Grinding Rolls).

Variables monitoreadas por molino:
  · Throughput (t/h)               · Energía específica (kWh/t)
  · Potencia consumida (kW)         · Presión hidráulica (bar)
  · Brecha entre rodillos (mm)      · Velocidad rodillo (m/s)
  · Alimentación F80 (mm)           · Producto P80 (mm)
  · Razón de reducción              · Desgaste rodillos (g/t)
  · Desgaste acumulado (mm)         · Temperatura cojinetes (°C)
  · Vibración (mm/s)                · Humedad alimentación (%)
  · Disponibilidad (%)              · Utilización (%)
  · Alarmas: temperatura, vibración, desgaste
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from dash import html, dcc
import dash_bootstrap_components as dbc
from data.mining_data import get_hpgr_df, HPGR_TARGETS, HPGR_MILLS

# ── Constantes de estilo ──────────────────────────────────────────────────────
PLOTLY_TEMPLATE = "plotly_dark"
CARD_BG  = "#161b22"
GRID_CLR = "#30363d"
MILL_COLORS = {
    "HPGR-01": "#58a6ff",
    "HPGR-02": "#e8a020",
    "HPGR-03": "#2ea44f",
    "HPGR-04": "#da3633",
}
MILL_COLORS_RGBA = {
    "HPGR-01": "rgba(88,166,255,0.12)",
    "HPGR-02": "rgba(232,160,32,0.12)",
    "HPGR-03": "rgba(46,164,79,0.12)",
    "HPGR-04": "rgba(218,54,51,0.12)",
}
ALARM_RED    = "#da3633"
ALARM_ORANGE = "#e8a020"
OK_GREEN     = "#2ea44f"


def _plot_cfg(fig, title=""):
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor=CARD_BG,
        plot_bgcolor=CARD_BG,
        margin=dict(l=10, r=10, t=40, b=10),
        font=dict(color="#c9d1d9", size=11),
        title=dict(text=title, font=dict(size=13, color="#8b949e")),
        xaxis=dict(gridcolor=GRID_CLR),
        yaxis=dict(gridcolor=GRID_CLR),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    return fig


def _status_color(value, target, higher_is_better=True):
    """Devuelve color de semáforo según umbral."""
    ratio = value / target if target else 1
    if higher_is_better:
        return OK_GREEN if ratio >= 0.97 else ALARM_ORANGE if ratio >= 0.88 else ALARM_RED
    else:
        return OK_GREEN if ratio <= 1.0 else ALARM_ORANGE if ratio <= 1.15 else ALARM_RED


# ── Tarjeta de estado por molino ─────────────────────────────────────────────
def _mill_status_card(molino, last_row):
    """Genera una mini tarjeta con KPIs en tiempo real del último día."""
    tp   = last_row["throughput_tph"]
    eng  = last_row["specific_energy"]
    avl  = last_row["availability_pct"]
    wear = last_row["roll_wear_gpt"]
    temp = last_row["bearing_temp_c"]
    vib  = last_row["vibration_mms"]

    alarm_count = int(last_row["alarm_temp"]) + int(last_row["alarm_vibration"]) + int(last_row["alarm_wear"])
    status_label = "ALARMA" if alarm_count > 0 else "NORMAL"
    status_color = ALARM_RED if alarm_count > 0 else OK_GREEN
    border_color = ALARM_RED if alarm_count > 0 else "#30363d"

    return dbc.Col(
        html.Div([
            # Header molino
            html.Div([
                html.Span(molino, style={"fontWeight": "700", "fontSize": "1rem", "color": MILL_COLORS[molino]}),
                html.Span(
                    status_label,
                    style={
                        "fontSize": ".65rem", "fontWeight": "700",
                        "color": status_color,
                        "border": f"1px solid {status_color}",
                        "borderRadius": "4px",
                        "padding": "1px 6px",
                        "marginLeft": "8px",
                    },
                ),
            ], style={"marginBottom": "10px"}),
            # KPIs en grid 2×3
            html.Div([
                _mini_kpi("Throughput", f"{tp:.0f} t/h", _status_color(tp, HPGR_TARGETS["throughput_tph"])),
                _mini_kpi("Energía", f"{eng:.2f} kWh/t", _status_color(eng, HPGR_TARGETS["specific_energy_kwht"], False)),
                _mini_kpi("Disponib.", f"{avl:.1f}%", _status_color(avl, HPGR_TARGETS["availability_pct"])),
                _mini_kpi("Desgaste", f"{wear:.3f} g/t", _status_color(wear, HPGR_TARGETS["roll_wear_gpt"], False)),
                _mini_kpi("Temp. Coj.", f"{temp:.1f} °C", _status_color(temp, HPGR_TARGETS["bearing_temp_c"], False)),
                _mini_kpi("Vibración", f"{vib:.2f} mm/s", _status_color(vib, HPGR_TARGETS["vibration_mms"], False)),
            ], style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "6px"}),
            # Alarmas activas
            html.Div(
                f"⚠ {alarm_count} alarma{'s' if alarm_count != 1 else ''} activa{'s' if alarm_count != 1 else ''}" if alarm_count else "✓ Sin alarmas",
                style={"fontSize": ".72rem", "color": status_color, "marginTop": "8px", "fontWeight": "600"},
            ),
        ], style={
            "backgroundColor": CARD_BG,
            "border": f"1px solid {border_color}",
            "borderRadius": "8px",
            "padding": "14px",
            "height": "100%",
        }),
        xs=12, sm=6, md=3,
    )


def _mini_kpi(label, value, color):
    return html.Div([
        html.Div(label, style={"fontSize": ".65rem", "color": "#8b949e", "textTransform": "uppercase"}),
        html.Div(value, style={"fontSize": ".88rem", "fontWeight": "700", "color": color}),
    ])


# ── Layout principal ──────────────────────────────────────────────────────────
def layout():
    df = get_hpgr_df()

    # Columnas de tiempo auxiliares
    df["month"] = pd.to_datetime(df["date"]).dt.to_period("M").dt.to_timestamp()
    df["week"]  = pd.to_datetime(df["date"]).dt.isocalendar().week.astype(int)

    # Últimos 90 días para gráficos de tendencia
    recent = df[df["date"] >= df["date"].max() - pd.Timedelta(days=89)].copy()

    # Promedios mensuales por molino
    monthly = (
        df.groupby(["month", "molino"])
        .agg(
            throughput_tph=("throughput_tph", "mean"),
            specific_energy=("specific_energy", "mean"),
            power_draw_kw=("power_draw_kw", "mean"),
            availability_pct=("availability_pct", "mean"),
            utilization_pct=("utilization_pct", "mean"),
            roll_wear_gpt=("roll_wear_gpt", "mean"),
            bearing_temp_c=("bearing_temp_c", "mean"),
            vibration_mms=("vibration_mms", "mean"),
            product_p80_mm=("product_p80_mm", "mean"),
            hydraulic_pressure=("hydraulic_pressure", "mean"),
        )
        .reset_index()
        .round(3)
    )

    # Último día registrado por molino (para status cards)
    last_day = df[df["date"] == df["date"].max()].set_index("molino")

    # Promedios anuales por molino (tabla + radar)
    annual_avg = (
        df.groupby("molino")
        .agg(
            throughput_tph=("throughput_tph", "mean"),
            specific_energy=("specific_energy", "mean"),
            availability_pct=("availability_pct", "mean"),
            utilization_pct=("utilization_pct", "mean"),
            roll_wear_gpt=("roll_wear_gpt", "mean"),
            bearing_temp_c=("bearing_temp_c", "mean"),
            vibration_mms=("vibration_mms", "mean"),
            product_p80_mm=("product_p80_mm", "mean"),
            power_draw_kw=("power_draw_kw", "mean"),
            alarm_temp=("alarm_temp", "sum"),
            alarm_vibration=("alarm_vibration", "sum"),
            alarm_wear=("alarm_wear", "sum"),
        )
        .reset_index()
        .round(2)
    )

    # ── Fig 1: Throughput diario — últimos 90 días ────────────────────────────
    fig_tp = go.Figure()
    for molino, color in MILL_COLORS.items():
        sub = recent[recent["molino"] == molino]
        fig_tp.add_scatter(
            x=sub["date"], y=sub["throughput_tph"],
            name=molino, line=dict(color=color, width=1.8),
            mode="lines",
        )
    fig_tp.add_hline(
        y=HPGR_TARGETS["throughput_tph"],
        line_dash="dash", line_color="#c9d1d9",
        annotation_text=f"Meta {HPGR_TARGETS['throughput_tph']} t/h",
        annotation_font_color="#c9d1d9",
    )
    _plot_cfg(fig_tp, "Throughput Diario por Molino — Últimos 90 Días (t/h)")

    # ── Fig 2: Energía específica mensual (bar grouped) ───────────────────────
    fig_energy = go.Figure()
    for molino, color in MILL_COLORS.items():
        sub = monthly[monthly["molino"] == molino]
        fig_energy.add_bar(
            x=sub["month"], y=sub["specific_energy"],
            name=molino, marker_color=color,
        )
    fig_energy.add_hline(
        y=HPGR_TARGETS["specific_energy_kwht"],
        line_dash="dot", line_color=ALARM_RED,
        annotation_text=f"Límite {HPGR_TARGETS['specific_energy_kwht']} kWh/t",
        annotation_font_color=ALARM_RED,
    )
    fig_energy.update_layout(barmode="group")
    _plot_cfg(fig_energy, "Energía Específica Mensual por Molino (kWh/t)")

    # ── Fig 3: Heatmap disponibilidad semanal (molino × semana) ──────────────
    pivot_avail = df.pivot_table(
        index="molino", columns="week",
        values="availability_pct", aggfunc="mean",
    ).round(1)
    pivot_avail = pivot_avail.iloc[:, :26]  # 26 semanas para legibilidad
    fig_heat_avail = px.imshow(
        pivot_avail,
        color_continuous_scale=[[0, "#3d1212"], [0.5, "#3d2f0a"], [1, "#1a4731"]],
        zmin=70, zmax=100,
        labels=dict(x="Semana", y="Molino", color="Disp. (%)"),
    )
    _plot_cfg(fig_heat_avail, "Disponibilidad Semanal por Molino (%) — H1 2024")

    # ── Fig 4: Desgaste rodillos mensual (línea) ──────────────────────────────
    fig_wear = go.Figure()
    for molino, color in MILL_COLORS.items():
        sub = monthly[monthly["molino"] == molino]
        fig_wear.add_scatter(
            x=sub["month"], y=sub["roll_wear_gpt"],
            name=molino, line=dict(color=color, width=2),
            mode="lines+markers",
        )
    fig_wear.add_hline(
        y=HPGR_TARGETS["roll_wear_gpt"],
        line_dash="dash", line_color=ALARM_RED,
        annotation_text=f"Límite {HPGR_TARGETS['roll_wear_gpt']} g/t",
        annotation_font_color=ALARM_RED,
    )
    _plot_cfg(fig_wear, "Tasa de Desgaste de Rodillos Mensual (g/t)")

    # ── Fig 5: Temperatura cojinetes (box por molino) ─────────────────────────
    fig_temp = px.box(
        df, x="molino", y="bearing_temp_c",
        color="molino",
        color_discrete_map=MILL_COLORS,
        labels={"bearing_temp_c": "Temperatura (°C)", "molino": ""},
    )
    fig_temp.add_hline(
        y=HPGR_TARGETS["bearing_temp_c"],
        line_dash="dash", line_color=ALARM_RED,
        annotation_text=f"Alarma {HPGR_TARGETS['bearing_temp_c']}°C",
        annotation_font_color=ALARM_RED,
    )
    _plot_cfg(fig_temp, "Distribución de Temperatura de Cojinetes (°C)")

    # ── Fig 6: Evolución P80 producto mensual ────────────────────────────────
    fig_p80 = go.Figure()
    for molino, color in MILL_COLORS.items():
        sub = monthly[monthly["molino"] == molino]
        fig_p80.add_scatter(
            x=sub["month"], y=sub["product_p80_mm"],
            name=molino, line=dict(color=color, width=2),
            mode="lines+markers",
        )
    fig_p80.add_hline(
        y=HPGR_TARGETS["product_p80_mm"],
        line_dash="dot", line_color=ALARM_ORANGE,
        annotation_text=f"Meta P80 ≤ {HPGR_TARGETS['product_p80_mm']} mm",
        annotation_font_color=ALARM_ORANGE,
    )
    _plot_cfg(fig_p80, "Tamaño de Producto P80 Mensual (mm)")

    # ── Fig 7: Radar comparación KPIs anuales ────────────────────────────────
    categories = ["Throughput\n(norm)", "Eficiencia\nEnergética", "Disponib.", "Utiliz.", "Calidad\nP80"]
    fig_radar = go.Figure()
    for _, row in annual_avg.iterrows():
        molino = row["molino"]
        # Normalizar 0-1 (1 = óptimo)
        tp_n    = min(row["throughput_tph"] / HPGR_TARGETS["throughput_tph"], 1.0)
        en_n    = max(1 - (row["specific_energy"] - 1.5) / 3.0, 0)
        av_n    = row["availability_pct"] / 100
        ut_n    = row["utilization_pct"] / 100
        p80_n   = max(1 - (row["product_p80_mm"] - 3) / 12, 0)
        values  = [tp_n, en_n, av_n, ut_n, p80_n]
        values += [values[0]]  # cerrar radar

        fig_radar.add_scatterpolar(
            r=values,
            theta=categories + [categories[0]],
            fill="toself",
            name=molino,
            line=dict(color=MILL_COLORS[molino]),
            fillcolor=MILL_COLORS_RGBA[molino],
            opacity=0.85,
        )
    fig_radar.update_layout(
        polar=dict(
            bgcolor=CARD_BG,
            radialaxis=dict(visible=True, range=[0, 1], gridcolor=GRID_CLR, color="#8b949e"),
            angularaxis=dict(gridcolor=GRID_CLR, color="#8b949e"),
        ),
        paper_bgcolor=CARD_BG,
        margin=dict(l=40, r=40, t=50, b=40),
        font=dict(color="#c9d1d9", size=10),
        title=dict(text="Radar Comparativo KPIs Anuales (normalizado)", font=dict(size=13, color="#8b949e")),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )

    # ── Fig 8: Scatter throughput vs energía (todos los días, muestra 400) ──
    sample = df.sample(400, random_state=7)
    fig_scatter = px.scatter(
        sample,
        x="throughput_tph", y="specific_energy",
        color="molino",
        color_discrete_map=MILL_COLORS,
        size="roll_wear_gpt",
        hover_data={"date": True, "availability_pct": ":.1f", "bearing_temp_c": ":.1f"},
        labels={
            "throughput_tph": "Throughput (t/h)",
            "specific_energy": "Energía Específica (kWh/t)",
        },
    )
    fig_scatter.add_vline(
        x=HPGR_TARGETS["throughput_tph"], line_dash="dash", line_color="#c9d1d9",
    )
    fig_scatter.add_hline(
        y=HPGR_TARGETS["specific_energy_kwht"], line_dash="dash", line_color=ALARM_RED,
    )
    _plot_cfg(fig_scatter, "Throughput vs Energía Específica (muestra 400 días)")

    # ── Tabla resumen anual ───────────────────────────────────────────────────
    table_rows = []
    for _, row in annual_avg.iterrows():
        molino  = row["molino"]
        tp_ok   = row["throughput_tph"] >= HPGR_TARGETS["throughput_tph"]
        en_ok   = row["specific_energy"] <= HPGR_TARGETS["specific_energy_kwht"]
        av_ok   = row["availability_pct"] >= HPGR_TARGETS["availability_pct"]
        wr_ok   = row["roll_wear_gpt"] <= HPGR_TARGETS["roll_wear_gpt"]
        total_alarms = int(row["alarm_temp"] + row["alarm_vibration"] + row["alarm_wear"])
        health_score = round(100 * (tp_ok + en_ok + av_ok + wr_ok) / 4)
        hs_color = OK_GREEN if health_score >= 75 else ALARM_ORANGE if health_score >= 50 else ALARM_RED

        table_rows.append(html.Tr([
            html.Td(molino, style={"color": MILL_COLORS[molino], "fontWeight": "700"}),
            html.Td(f"{row['throughput_tph']:.1f}", style={"color": OK_GREEN if tp_ok else ALARM_RED}),
            html.Td(f"{row['specific_energy']:.3f}", style={"color": OK_GREEN if en_ok else ALARM_RED}),
            html.Td(f"{row['power_draw_kw']:,.0f}"),
            html.Td(f"{row['availability_pct']:.1f}%", style={"color": OK_GREEN if av_ok else ALARM_RED}),
            html.Td(f"{row['utilization_pct']:.1f}%"),
            html.Td(f"{row['roll_wear_gpt']:.4f}", style={"color": OK_GREEN if wr_ok else ALARM_RED}),
            html.Td(f"{row['bearing_temp_c']:.1f} °C",
                    style={"color": OK_GREEN if row["bearing_temp_c"] <= HPGR_TARGETS["bearing_temp_c"] else ALARM_RED}),
            html.Td(f"{row['product_p80_mm']:.2f}"),
            html.Td(str(total_alarms),
                    style={"color": ALARM_RED if total_alarms > 30 else ALARM_ORANGE if total_alarms > 10 else OK_GREEN}),
            html.Td(
                html.Div([
                    html.Div(style={
                        "width": f"{health_score}%", "height": "8px",
                        "backgroundColor": hs_color, "borderRadius": "4px",
                        "display": "inline-block",
                    }),
                    html.Span(f" {health_score}%", style={"color": hs_color, "fontSize": ".8rem"}),
                ]),
            ),
        ]))

    tabla = html.Table(
        [
            html.Thead(html.Tr([
                html.Th(h) for h in [
                    "Molino", "Throughput\n(t/h)", "Energía\n(kWh/t)", "Potencia\n(kW)",
                    "Disponib.", "Utiliz.", "Desgaste\n(g/t)", "Temp. Coj.",
                    "P80 (mm)", "Alarmas/año", "Health Score",
                ]
            ], style={"color": "#8b949e", "fontSize": ".75rem", "textTransform": "uppercase"})),
            html.Tbody(table_rows),
        ],
        style={"width": "100%", "fontSize": ".82rem", "borderCollapse": "collapse"},
        className="table-hover",
    )

    # ── Status cards por molino ───────────────────────────────────────────────
    status_cards = dbc.Row(
        [_mill_status_card(m, last_day.loc[m]) for m in HPGR_MILLS],
        className="g-3 mb-4",
    )

    # ── KPI banner global ─────────────────────────────────────────────────────
    total_alarm_days = int(df[["alarm_temp", "alarm_vibration", "alarm_wear"]].any(axis=1).sum())
    avg_tp   = df["throughput_tph"].mean()
    avg_eng  = df["specific_energy"].mean()
    avg_avl  = df["availability_pct"].mean()
    total_tp = df.groupby("date")["throughput_tph"].sum().mean()  # t/h combinado

    global_kpis = dbc.Row([
        dbc.Col(html.Div([
            html.Div("⚙️", className="kpi-icon"),
            html.Div(f"{total_tp:,.0f} t/h", className="kpi-value", style={"color": "#58a6ff"}),
            html.Div("Throughput Combinado", className="kpi-label"),
        ], className="kpi-card"), xs=6, md=3),
        dbc.Col(html.Div([
            html.Div("⚡", className="kpi-icon"),
            html.Div(f"{avg_eng:.2f} kWh/t", className="kpi-value",
                     style={"color": OK_GREEN if avg_eng <= HPGR_TARGETS["specific_energy_kwht"] else ALARM_ORANGE}),
            html.Div("Energía Específica Prom.", className="kpi-label"),
        ], className="kpi-card"), xs=6, md=3),
        dbc.Col(html.Div([
            html.Div("📊", className="kpi-icon"),
            html.Div(f"{avg_avl:.1f}%", className="kpi-value",
                     style={"color": OK_GREEN if avg_avl >= HPGR_TARGETS["availability_pct"] else ALARM_ORANGE}),
            html.Div("Disponibilidad Flota", className="kpi-label"),
        ], className="kpi-card"), xs=6, md=3),
        dbc.Col(html.Div([
            html.Div("🔴", className="kpi-icon"),
            html.Div(str(total_alarm_days), className="kpi-value",
                     style={"color": ALARM_RED if total_alarm_days > 100 else ALARM_ORANGE}),
            html.Div("Días-Equipo con Alarma", className="kpi-label"),
        ], className="kpi-card"), xs=6, md=3),
    ], className="g-3 mb-4")

    # ── Ensamble del layout ───────────────────────────────────────────────────
    return html.Div([
        html.Div([
            html.H2("Molinos HPGR"),
            html.P(
                "Monitoreo de 4 molinos de rodillos de alta presión (HPGR) — "
                "Throughput · Energía · Desgaste · Temperatura · Disponibilidad · 2024"
            ),
        ], className="page-header"),

        global_kpis,
        status_cards,

        # Throughput + Radar
        dbc.Row([
            dbc.Col(html.Div([dcc.Graph(figure=fig_tp, config={"displayModeBar": False})], className="chart-card"), md=8),
            dbc.Col(html.Div([dcc.Graph(figure=fig_radar, config={"displayModeBar": False})], className="chart-card"), md=4),
        ], className="g-3"),

        # Energía + Heatmap disponibilidad
        dbc.Row([
            dbc.Col(html.Div([dcc.Graph(figure=fig_energy, config={"displayModeBar": False})], className="chart-card"), md=6),
            dbc.Col(html.Div([dcc.Graph(figure=fig_heat_avail, config={"displayModeBar": False})], className="chart-card"), md=6),
        ], className="g-3"),

        # Desgaste + Temperatura cojinetes
        dbc.Row([
            dbc.Col(html.Div([dcc.Graph(figure=fig_wear, config={"displayModeBar": False})], className="chart-card"), md=6),
            dbc.Col(html.Div([dcc.Graph(figure=fig_temp, config={"displayModeBar": False})], className="chart-card"), md=6),
        ], className="g-3"),

        # P80 + Scatter throughput vs energía
        dbc.Row([
            dbc.Col(html.Div([dcc.Graph(figure=fig_p80, config={"displayModeBar": False})], className="chart-card"), md=5),
            dbc.Col(html.Div([dcc.Graph(figure=fig_scatter, config={"displayModeBar": False})], className="chart-card"), md=7),
        ], className="g-3"),

        # Tabla resumen
        dbc.Row([
            dbc.Col(html.Div([
                html.Div("Resumen Anual de KPIs por Molino HPGR", className="chart-title"),
                html.Div(tabla, style={"overflowX": "auto"}),
                html.Div([
                    html.Span("Metas: ", style={"color": "#8b949e", "fontSize": ".75rem"}),
                    html.Span(f"Throughput ≥ {HPGR_TARGETS['throughput_tph']} t/h  |  "
                              f"Energía ≤ {HPGR_TARGETS['specific_energy_kwht']} kWh/t  |  "
                              f"Disponib. ≥ {HPGR_TARGETS['availability_pct']}%  |  "
                              f"Desgaste ≤ {HPGR_TARGETS['roll_wear_gpt']} g/t  |  "
                              f"Temp. Coj. ≤ {HPGR_TARGETS['bearing_temp_c']} °C",
                              style={"color": "#8b949e", "fontSize": ".75rem"}),
                ], style={"marginTop": "10px", "paddingTop": "8px", "borderTop": "1px solid #30363d"}),
            ], className="chart-card"), md=12),
        ], className="g-3"),

    ], style={"padding": "1.5rem"})
