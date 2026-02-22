# Molinos HPGR — Documentación Técnica

> Fecha: 2026-02-22 · Módulo: `pages/molinos.py` · Datos: `data/mining_data.py`

---

## Tabla de Contenidos

1. [¿Qué es un molino HPGR?](#1-qué-es-un-molino-hpgr)
2. [Modelo de datos simulados](#2-modelo-de-datos-simulados)
3. [Parámetros monitoreados](#3-parámetros-monitoreados)
4. [Perfiles de los 4 molinos](#4-perfiles-de-los-4-molinos)
5. [Sistema de alarmas](#5-sistema-de-alarmas)
6. [Flujo de generación de datos](#6-flujo-de-generación-de-datos)
7. [Arquitectura de la página](#7-arquitectura-de-la-página)
8. [Layout y gráficos](#8-layout-y-gráficos)
9. [Transformaciones de datos](#9-transformaciones-de-datos)
10. [Dependencias del módulo](#10-dependencias-del-módulo)

---

## 1. ¿Qué es un molino HPGR?

Los **HPGR (High Pressure Grinding Rolls)** son equipos de conminución que aplican alta presión a través de dos rodillos contrarotantes, generando fractura interparticular dentro de un lecho comprimido de mineral.

```mermaid
graph LR
    FEED["Alimentación\nF80 ~35 mm"] --> HPGR_UNIT["🔩 HPGR\nRodillos contrarotantes\nPresión hidráulica 150-165 bar"]
    HPGR_UNIT --> PRODUCT["Producto\nP80 ~5-10 mm"]
    HPGR_UNIT --> FLAKE["Flake / Edge material\n(recirculación parcial)"]

    MOTOR["Motor eléctrico\n2000-4500 kW"] --> HPGR_UNIT
    HYD["Sistema hidráulico\n120-180 bar"] --> HPGR_UNIT
```

### Ventajas principales
- **Eficiencia energética**: 20-40% menos energía vs molinos convencionales
- **Alta disponibilidad**: > 92% mecánica operativa
- **Reducción de tamaño controlada**: F80/P80 ratio ~4-6x

---

## 2. Modelo de datos simulados

```mermaid
erDiagram
    HPGR_DATA {
        date        date        "Fecha (2024-01-01 a 2024-12-31)"
        molino      string      "HPGR-01 / 02 / 03 / 04"
        throughput_tph      float   "Tonelaje procesado (t/h)"
        specific_energy     float   "Energía específica (kWh/t)"
        power_draw_kw       float   "Potencia consumida (kW)"
        hydraulic_pressure  float   "Presión hidráulica (bar)"
        roll_gap_mm         float   "Brecha entre rodillos (mm)"
        roll_speed_ms       float   "Velocidad superficial rodillo (m/s)"
        feed_f80_mm         float   "Tamaño alimentación F80 (mm)"
        product_p80_mm      float   "Tamaño producto P80 (mm)"
        reduction_ratio     float   "Razón de reducción F80/P80"
        roll_wear_gpt       float   "Tasa de desgaste rodillos (g/t)"
        roll_wear_accum_mm  float   "Desgaste acumulado estimado (mm)"
        bearing_temp_c      float   "Temperatura cojinetes (°C)"
        vibration_mms       float   "Vibración carcasa (mm/s)"
        feed_moisture_pct   float   "Humedad alimentación (%)"
        availability_pct    float   "Disponibilidad mecánica (%)"
        utilization_pct     float   "Utilización efectiva (%)"
        alarm_temp          bool    "Alarma temperatura > 70°C"
        alarm_vibration     bool    "Alarma vibración > 4.5 mm/s"
        alarm_wear          bool    "Alarma desgaste > 0.5 g/t"
    }
```

**Dimensiones del dataset:** 4 molinos × 365 días = **1.460 filas**, 21 columnas.

---

## 3. Parámetros monitoreados

| Parámetro | Unidad | Rango típico | Meta / Límite | Categoría |
|---|---|---|---|---|
| Throughput | t/h | 600 – 950 | ≥ 800 | Producción |
| Energía específica | kWh/t | 1.2 – 4.5 | ≤ 2.5 | Eficiencia |
| Potencia consumida | kW | 800 – 4.500 | — | Energía |
| Presión hidráulica | bar | 100 – 200 | 150 – 165 | Proceso |
| Brecha rodillos | mm | 10 – 40 | 20 – 27 | Proceso |
| Velocidad rodillo | m/s | 0.6 – 2.0 | 1.2 – 1.5 | Proceso |
| Alimentación F80 | mm | 18 – 55 | ≤ 45 | Feed |
| Producto P80 | mm | 3 – 15 | ≤ 9 | Calidad |
| Razón reducción | — | 2 – 10 | ≥ 4 | Calidad |
| Desgaste rodillos | g/t | 0.05 – 1.5 | ≤ 0.5 | Mantenimiento |
| Desgaste acumulado | mm | — | — | Mantenimiento |
| Temp. cojinetes | °C | 35 – 95 | ≤ 70 (alarma) | Condición |
| Vibración | mm/s | 0.5 – 9.0 | ≤ 4.5 (alarma) | Condición |
| Humedad feed | % | 1 – 12 | ≤ 8 | Feed |
| Disponibilidad | % | 60 – 100 | ≥ 92 | Confiabilidad |
| Utilización | % | 55 – 100 | ≥ 80 | Confiabilidad |

---

## 4. Perfiles de los 4 molinos

```mermaid
quadrantChart
    title Throughput vs Eficiencia Energética (promedios anuales)
    x-axis "Energía Específica baja → alta (kWh/t)"
    y-axis "Throughput bajo → alto (t/h)"
    quadrant-1 Alto rendimiento
    quadrant-2 Alta producción, baja eficiencia
    quadrant-3 Bajo rendimiento
    quadrant-4 Eficiente pero baja producción
    HPGR-01: [0.47, 0.51]
    HPGR-02: [0.73, 0.39]
    HPGR-03: [0.33, 0.62]
    HPGR-04: [0.64, 0.31]
```

| Molino | Perfil | Throughput base | Energía base | Disponib. | Observación |
|---|---|---|---|---|---|
| **HPGR-01** | Estable | 820 t/h | 2.20 kWh/t | 94% | Operación nominal, referencia de planta |
| **HPGR-02** | Degradado | 780 t/h | 2.60 kWh/t | 91% | Rodillos con desgaste moderado |
| **HPGR-03** | Óptimo | 860 t/h | 1.98 kWh/t | 96% | Unidad más nueva, mejor eficiencia |
| **HPGR-04** | Crítico | 750 t/h | 2.45 kWh/t | 87% | Alto desgaste, menor disponibilidad |

---

## 5. Sistema de alarmas

```mermaid
flowchart TD
    SENSOR["Lectura diaria\npor molino"] --> EVAL["Evaluación de umbrales"]

    EVAL --> T1{"bearing_temp_c\n> 70°C ?"}
    EVAL --> T2{"vibration_mms\n> 4.5 mm/s ?"}
    EVAL --> T3{"roll_wear_gpt\n> 0.5 g/t ?"}

    T1 -->|Sí| A1["alarm_temp = True\n🔴 Riesgo falla cojinete"]
    T2 -->|Sí| A2["alarm_vibration = True\n🔴 Inspección mecánica"]
    T3 -->|Sí| A3["alarm_wear = True\n🔴 Revisar programa\nde cambio de rodillos"]

    T1 -->|No| OK1["✓"]
    T2 -->|No| OK2["✓"]
    T3 -->|No| OK3["✓"]

    A1 & A2 & A3 --> SUM["Conteo alarmas activas\npor equipo"]

    SUM --> CARD["Status Card molino\nNORMAL / ALARMA"]
    SUM --> TABLE["Health Score %\n= KPIs dentro de meta / 4"]
```

### Colores semáforo en UI

```mermaid
graph LR
    V1["Valor ≥ 97% meta"] --> C1["🟢 Verde #2ea44f"]
    V2["Valor 88-97% meta"] --> C2["🟡 Naranja #e8a020"]
    V3["Valor < 88% meta"] --> C3["🔴 Rojo #da3633"]
```

---

## 6. Flujo de generación de datos

```mermaid
flowchart TD
    SEED["np.random.default_rng(99)\nseed independiente para HPGR"] --> MILLS["Iterar 4 molinos\n× 365 días = 1460 filas"]

    MILLS --> TREND["Tendencia anual de degradación\nwear_trend = linspace(1.0, 1.18)\ntemp_trend = linspace(1.0, 1.10)"]

    TREND --> VARS["Calcular variables por día"]

    VARS --> TP["throughput = Normal(base, 35)\n× factor desgaste inverso"]
    VARS --> PRES["hydraulic_pressure = Normal(base, 6)\nclip [100, 200]"]
    VARS --> GAP["roll_gap = Normal(base, 1.5)\nclip [10, 40]"]
    VARS --> SPEED["roll_speed = Normal(base, 0.06)\nclip [0.6, 2.0]"]
    VARS --> ENG["specific_energy = Normal(base × wear_trend, 0.18)\nclip [1.2, 4.5]"]
    VARS --> F80["feed_f80 = Normal(35, 4)\nclip [18, 55]"]
    VARS --> P80["product_p80 = Normal(F80/4.5, 0.8)\nclip [3, 15]"]
    VARS --> WEAR["roll_wear = Normal(base × wear_trend, 0.07)\nclip [0.05, 1.5]"]
    VARS --> TEMP["bearing_temp = Normal(base × temp_trend, 3.5)\nclip [35, 95]"]
    VARS --> VIB["vibration = Normal(2.2, 0.8)\nclip [0.5, 9.0]"]
    VARS --> AVAIL["availability = Normal(base, 3.5)\nclip [60, 100]"]

    TP & ENG --> PWR["power_draw = throughput × specific_energy"]
    F80 & P80 --> RR["reduction_ratio = F80 / P80"]
    WEAR --> WACC["roll_wear_accum = wear × días × 24h / 1000"]

    TEMP --> ALM1["alarm_temp = temp > 70°C"]
    VIB --> ALM2["alarm_vibration = vib > 4.5 mm/s"]
    WEAR --> ALM3["alarm_wear = wear > 0.5 g/t"]
```

---

## 7. Arquitectura de la página

```mermaid
graph TD
    FN["molinos.layout()"] --> DATA["get_hpgr_df()\n1460 filas, 21 columnas"]

    DATA --> T1["Columnas auxiliares\nmonth · week"]
    T1 --> RECENT["recent = últimos 90 días"]
    T1 --> MONTHLY["monthly = groupby month+molino\n.agg(mean de KPIs)"]
    T1 --> LASTDAY["last_day = último día\npor molino"]
    T1 --> ANNUAL["annual_avg = groupby molino\n.agg(mean + sum alarmas)"]

    ANNUAL --> HEALTH["Health Score\n= KPIs dentro de meta / 4 × 100"]

    LASTDAY --> STATUS_CARDS["4 × Mill Status Cards\n6 mini-KPIs + alarmas activas"]
    ANNUAL --> GLOBAL_KPI["4 KPI Cards globales\nThroughput · Energía · Disponib · Alarmas"]

    RECENT --> FIG1["fig_tp\nLine chart throughput\n90 días × 4 molinos"]
    ANNUAL --> FIG7["fig_radar\nScatter polar\n5 dimensiones normalizadas"]
    MONTHLY --> FIG2["fig_energy\nBar grouped energía\nkWh/t mensual"]
    DATA --> FIG3["fig_heat_avail\npx.imshow molino×semana\ndisponibilidad"]
    MONTHLY --> FIG4["fig_wear\nLine desgaste g/t\nmensual"]
    DATA --> FIG5["fig_temp\npx.box temp cojinetes\npor molino"]
    MONTHLY --> FIG6["fig_p80\nLine P80 producto\nmensual"]
    DATA --> FIG8["fig_scatter\npx.scatter tp vs energía\nmuestra 400 días"]
    ANNUAL --> TABLE["html.Table\nResumen KPIs + Health Score"]
```

---

## 8. Layout y gráficos

```mermaid
graph TD
    PAGE["pages/molinos.py — layout final"]

    PAGE --> HDR["page-header\nH2 + descripción"]
    PAGE --> G_KPI["dbc.Row — 4 KPI Cards globales"]
    PAGE --> STATUS["dbc.Row — 4 Mill Status Cards"]

    PAGE --> R1["dbc.Row md=8+4"]
    R1 --> G1["fig_tp\nThroughput diario 90d"]
    R1 --> G7["fig_radar\nRadar KPIs normalizados"]

    PAGE --> R2["dbc.Row md=6+6"]
    R2 --> G2["fig_energy\nEnergía específica mensual"]
    R2 --> G3["fig_heat_avail\nHeatmap disponibilidad"]

    PAGE --> R3["dbc.Row md=6+6"]
    R3 --> G4["fig_wear\nDesgaste rodillos mensual"]
    R3 --> G5["fig_temp\nBox temperatura cojinetes"]

    PAGE --> R4["dbc.Row md=5+7"]
    R4 --> G6["fig_p80\nEvolución P80 mensual"]
    R4 --> G8["fig_scatter\nThroughput vs Energía"]

    PAGE --> R5["dbc.Row md=12"]
    R5 --> TB["html.Table\nResumen anual + Health Score bars"]
```

### Descripción de cada gráfico

| # | Figura | Tipo | Datos fuente | Insight principal |
|---|---|---|---|---|
| 1 | Throughput diario | `go.Scatter` líneas × 4 | `recent` (90 días) | Variabilidad y tendencia de producción |
| 2 | Energía específica mensual | `go.Bar` agrupado | `monthly` | Comparar eficiencia entre molinos |
| 3 | Heatmap disponibilidad | `px.imshow` | `df` pivot semana | Detectar semanas problemáticas |
| 4 | Desgaste rodillos | `go.Scatter` líneas × 4 | `monthly` | Tendencia de desgaste y vida útil |
| 5 | Temperatura cojinetes | `px.box` | `df` completo | Distribución y outliers de temperatura |
| 6 | Producto P80 mensual | `go.Scatter` líneas × 4 | `monthly` | Calidad de producto vs meta |
| 7 | Radar KPIs | `go.Scatterpolar` | `annual_avg` | Comparación global normalizada |
| 8 | Scatter tp vs energía | `px.scatter` | muestra 400 filas | Correlación operación vs eficiencia |

---

## 9. Transformaciones de datos

```mermaid
flowchart LR
    RAW["get_hpgr_df()\n1460 filas"] --> M1["+ month\n+ week"]

    M1 --> RECENT_F["recent = últimos 90 días\n360 filas"]
    M1 --> MONTHLY_G["groupby month+molino\n.agg(mean)\n48 filas"]
    M1 --> LASTDAY_F["date == max(date)\n4 filas"]
    M1 --> ANNUAL_G["groupby molino\n.agg(mean + sum)\n4 filas"]
    M1 --> PIVOT["pivot_table\nmolino × week\ndisponibilidad media"]

    ANNUAL_G --> HS["Health Score\ntp_ok + en_ok + av_ok + wr_ok\n/4 × 100"]
    ANNUAL_G --> RADAR_N["Normalización 0-1\n5 dimensiones KPI"]
    ANNUAL_G --> SAMPLE_400["df.sample(400)\npara scatter"]
```

---

## 10. Dependencias del módulo

```mermaid
graph LR
    MOL["pages/molinos.py"] --> DM["data/mining_data.py\nget_hpgr_df\nHPGR_TARGETS\nHPGR_MILLS"]
    MOL --> GO["plotly.graph_objects\nFigure, Scatter, Bar\nBox, Indicator, Scatterpolar"]
    MOL --> PX["plotly.express\nimshow, box, scatter"]
    MOL --> DBC["dash_bootstrap_components\nRow, Col, Navbar"]
    MOL --> DASH["dash\nhtml, dcc"]
    MOL --> PANDAS["pandas"]
    MOL --> NUMPY["numpy"]

    APP["app.py"] --> MOL
    APP -->|"/molinos route"| MOL
    NAV["components/navbar.py"] -->|"NavLink Molinos HPGR"| MOL
```

---

## Referencias técnicas

- [Metso HPGRSense™ — monitoreo digital de HPGR](https://www.metso.com/portfolio/hrc-series/hrce/)
- [FLS High Pressure Grinding Rolls](https://fls.com/en/equipment/grinding/high-pressure-grinding-rolls)
- [TAKRAF HPGR — parámetros de optimización](https://www.takraf.com/portfolio/detail/high-pressure-grinding-rolls-hpgr/)
- [Weir ENDURON® HPGR](https://www.global.weir/product-catalogue/high-pressure-grinding-rolls/enduron-high-pressure-grinding-rolls/)
- [911Metallurgist — HPGR parámetros clave](https://www.911metallurgist.com/blog/high-pressure-grinding-rolls/)
