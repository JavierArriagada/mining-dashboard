import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)

# ── Fecha base ──────────────────────────────────────────────────────────────
START = datetime(2024, 1, 1)
DAYS = 365
DATES = [START + timedelta(days=i) for i in range(DAYS)]

# ── Producción diaria ────────────────────────────────────────────────────────
def get_production_df():
    trend = np.linspace(4800, 5500, DAYS)
    noise = np.random.normal(0, 200, DAYS)
    tonnage = np.clip(trend + noise, 3000, 7000)

    grade_cu = np.clip(np.random.normal(1.2, 0.15, DAYS), 0.5, 2.0)
    grade_au = np.clip(np.random.normal(0.45, 0.08, DAYS), 0.1, 0.9)

    recovery_cu = np.clip(np.random.normal(88, 3, DAYS), 75, 96)
    recovery_au = np.clip(np.random.normal(82, 4, DAYS), 68, 94)

    return pd.DataFrame({
        "date": DATES,
        "tonnage": tonnage.round(1),
        "grade_cu": grade_cu.round(3),
        "grade_au": grade_au.round(3),
        "recovery_cu": recovery_cu.round(2),
        "recovery_au": recovery_au.round(2),
        "fine_cu_t": (tonnage * grade_cu / 100 * recovery_cu / 100).round(2),
        "fine_au_oz": (tonnage * grade_au / 1000 * recovery_au / 100 * 32.15).round(1),
    })


# ── Equipos ──────────────────────────────────────────────────────────────────
EQUIPMENT = {
    "Palas": ["Pala-01", "Pala-02", "Pala-03"],
    "Camiones": ["CAM-01", "CAM-02", "CAM-03", "CAM-04", "CAM-05", "CAM-06"],
    "Perforadoras": ["PERF-01", "PERF-02"],
    "Chancadoras": ["CHAN-01", "CHAN-02"],
}

def get_equipment_df():
    rows = []
    all_equip = [(t, e) for t, lst in EQUIPMENT.items() for e in lst]
    for tipo, equipo in all_equip:
        for date in DATES:
            disp = np.random.uniform(72, 98)
            util = disp * np.random.uniform(0.75, 0.92)
            maint = 100 - disp
            rows.append({
                "date": date,
                "tipo": tipo,
                "equipo": equipo,
                "disponibilidad": round(disp, 1),
                "utilizacion": round(util, 1),
                "mantenimiento": round(maint, 1),
            })
    return pd.DataFrame(rows)


# ── Seguridad ────────────────────────────────────────────────────────────────
def get_safety_df():
    rows = []
    for date in DATES:
        rows.append({
            "date": date,
            "incidentes": int(np.random.poisson(0.3)),
            "casi_accidentes": int(np.random.poisson(2.5)),
            "dias_sin_accidente": None,  # calculado abajo
            "horas_hombre": int(np.random.normal(12000, 500)),
            "inspecciones": int(np.random.normal(8, 2)),
        })
    df = pd.DataFrame(rows)
    # Calcular días sin accidente acumulados
    counter = 0
    dsas = []
    for inc in df["incidentes"]:
        if inc > 0:
            counter = 0
        else:
            counter += 1
        dsas.append(counter)
    df["dias_sin_accidente"] = dsas
    return df


# ── Costos mensuales ─────────────────────────────────────────────────────────
def get_costs_df():
    months = pd.date_range("2024-01-01", periods=12, freq="MS")
    categorias = ["Energía", "Mano de Obra", "Repuestos", "Reactivos", "Combustible", "Otros"]
    base = [1_200_000, 2_800_000, 950_000, 480_000, 720_000, 350_000]
    rows = []
    for m in months:
        for cat, b in zip(categorias, base):
            rows.append({
                "mes": m,
                "categoria": cat,
                "costo": round(b * np.random.uniform(0.90, 1.10)),
            })
    return pd.DataFrame(rows)


# ── Molinos HPGR ─────────────────────────────────────────────────────────────
# High Pressure Grinding Rolls: 4 unidades con perfiles de operación distintos
HPGR_MILLS = {
    "HPGR-01": {  # Molino primario, desempeño estable
        "throughput_base": 820,
        "energy_base": 2.20,
        "pressure_base": 155,
        "gap_base": 22,
        "speed_base": 1.35,
        "wear_base": 0.35,
        "avail_base": 94,
        "bearing_temp_base": 55,
    },
    "HPGR-02": {  # Rodillos con desgaste moderado, mayor consumo energético
        "throughput_base": 780,
        "energy_base": 2.60,
        "pressure_base": 162,
        "gap_base": 25,
        "speed_base": 1.28,
        "wear_base": 0.52,
        "avail_base": 91,
        "bearing_temp_base": 62,
    },
    "HPGR-03": {  # Unidad más nueva, mejor eficiencia
        "throughput_base": 860,
        "energy_base": 1.98,
        "pressure_base": 150,
        "gap_base": 20,
        "speed_base": 1.45,
        "wear_base": 0.28,
        "avail_base": 96,
        "bearing_temp_base": 50,
    },
    "HPGR-04": {  # Alto desgaste, menor disponibilidad, requiere atención
        "throughput_base": 750,
        "energy_base": 2.45,
        "pressure_base": 160,
        "gap_base": 27,
        "speed_base": 1.22,
        "wear_base": 0.68,
        "avail_base": 87,
        "bearing_temp_base": 68,
    },
}

# Metas operacionales HPGR
HPGR_TARGETS = {
    "throughput_tph": 800,       # t/h mínimo
    "specific_energy_kwht": 2.5,  # kWh/t máximo
    "availability_pct": 92,      # % mínimo
    "roll_wear_gpt": 0.5,        # g/t máximo
    "bearing_temp_c": 70,        # °C máximo
    "vibration_mms": 4.5,        # mm/s máximo
    "product_p80_mm": 9.0,       # mm máximo
}


def get_hpgr_df():
    """
    Genera DataFrame con 4 molinos HPGR × 365 días.

    Columnas:
        date              : fecha
        molino            : identificador del molino (HPGR-01 … HPGR-04)
        throughput_tph    : tonelaje procesado (t/h)
        specific_energy   : energía específica (kWh/t)
        power_draw_kw     : potencia consumida (kW)
        hydraulic_pressure: presión hidráulica (bar)
        roll_gap_mm       : brecha entre rodillos (mm)
        roll_speed_ms     : velocidad superficial de rodillo (m/s)
        feed_f80_mm       : tamaño de alimentación F80 (mm)
        product_p80_mm    : tamaño de producto P80 (mm)
        reduction_ratio   : razón de reducción F80/P80
        roll_wear_gpt     : tasa de desgaste rodillos (g/t)
        roll_wear_accum_mm: desgaste acumulado rodillos (mm estimado)
        bearing_temp_c    : temperatura cojinetes (°C)
        vibration_mms     : vibración carcasa (mm/s)
        feed_moisture_pct : humedad alimentación (%)
        availability_pct  : disponibilidad mecánica (%)
        utilization_pct   : utilización efectiva (%)
        alarm_temp        : True si temp > 70 °C
        alarm_vibration   : True si vibración > 4.5 mm/s
        alarm_wear        : True si desgaste > 0.5 g/t
    """
    rng = np.random.default_rng(99)  # seed independiente para HPGR
    rows = []

    for molino, cfg in HPGR_MILLS.items():
        # Tendencia leve de degradación a lo largo del año
        wear_trend = np.linspace(1.0, 1.18, DAYS)
        temp_trend = np.linspace(1.0, 1.10, DAYS)

        for i, date in enumerate(DATES):
            tp = float(np.clip(
                rng.normal(cfg["throughput_base"], 35) * (1 - 0.04 * wear_trend[i] + 0.04),
                500, 1000,
            ))
            pressure = float(np.clip(rng.normal(cfg["pressure_base"], 6), 100, 200))
            gap = float(np.clip(rng.normal(cfg["gap_base"], 1.5), 10, 40))
            speed = float(np.clip(rng.normal(cfg["speed_base"], 0.06), 0.6, 2.0))
            energy = float(np.clip(
                rng.normal(cfg["energy_base"] * wear_trend[i], 0.18),
                1.2, 4.5,
            ))
            power = round(tp * energy, 1)
            feed_f80 = float(np.clip(rng.normal(35, 4), 18, 55))
            product_p80 = float(np.clip(
                rng.normal(feed_f80 / 4.5, 0.8), 3, 15,
            ))
            reduction_ratio = round(feed_f80 / max(product_p80, 0.1), 2)
            wear = float(np.clip(
                rng.normal(cfg["wear_base"] * wear_trend[i], 0.07), 0.05, 1.5,
            ))
            wear_accum = round(wear * (i + 1) * 24 / 1000, 3)  # mm estimado acumulado
            bear_temp = float(np.clip(
                rng.normal(cfg["bearing_temp_base"] * temp_trend[i], 3.5), 35, 95,
            ))
            vibration = float(np.clip(rng.normal(2.2, 0.8), 0.5, 9.0))
            moisture = float(np.clip(rng.normal(4.5, 1.2), 1.0, 12.0))
            avail = float(np.clip(rng.normal(cfg["avail_base"], 3.5), 60, 100))
            util = float(np.clip(avail * rng.uniform(0.78, 0.95), 55, 100))

            rows.append({
                "date": date,
                "molino": molino,
                "throughput_tph": round(tp, 1),
                "specific_energy": round(energy, 3),
                "power_draw_kw": round(power, 0),
                "hydraulic_pressure": round(pressure, 1),
                "roll_gap_mm": round(gap, 2),
                "roll_speed_ms": round(speed, 3),
                "feed_f80_mm": round(feed_f80, 1),
                "product_p80_mm": round(product_p80, 2),
                "reduction_ratio": reduction_ratio,
                "roll_wear_gpt": round(wear, 4),
                "roll_wear_accum_mm": wear_accum,
                "bearing_temp_c": round(bear_temp, 1),
                "vibration_mms": round(vibration, 2),
                "feed_moisture_pct": round(moisture, 1),
                "availability_pct": round(avail, 1),
                "utilization_pct": round(util, 1),
                "alarm_temp": bear_temp > HPGR_TARGETS["bearing_temp_c"],
                "alarm_vibration": vibration > HPGR_TARGETS["vibration_mms"],
                "alarm_wear": wear > HPGR_TARGETS["roll_wear_gpt"],
            })

    return pd.DataFrame(rows)


# ── KPIs resumen ─────────────────────────────────────────────────────────────
def get_kpis():
    prod = get_production_df()
    safety = get_safety_df()
    return {
        "total_ton": f"{prod['tonnage'].sum():,.0f} t",
        "avg_grade_cu": f"{prod['grade_cu'].mean():.3f} %",
        "total_fine_cu": f"{prod['fine_cu_t'].sum():,.1f} t",
        "total_fine_au": f"{prod['fine_au_oz'].sum():,.0f} oz",
        "dias_sin_accidente": int(safety["dias_sin_accidente"].iloc[-1]),
        "total_incidentes": int(safety["incidentes"].sum()),
    }
