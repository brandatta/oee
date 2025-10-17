import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

# ================= CONFIG =================
st.set_page_config(page_title="Calculadora OEE", layout="wide")

# ================= ESTILOS =================
st.markdown("""
<style>
.kpi-card {border-radius: 16px; padding: 14px 16px; background: #f7f7f8; border: 1px solid #e9eaee}
.kpi-title {font-size: 13px; color: #555; margin-bottom: 4px}
.kpi-value {font-size: 26px; font-weight: 700}
.small-muted {font-size:12px; color:#777}
.ok {color:#107c41}
.mid {color:#c77d00}
.bad {color:#b00020}
.note {background:#fff7e6; border:1px solid #ffe1ac; padding:12px 14px; border-radius:12px}
.formula {background:#eef6ff; border:1px solid #d3e6ff; padding:12px 14px; border-radius:12px}

/* 🎨 Fondo distinto solo para Factor A y Factor B */
div[data-testid="stNumberInput"][key="factor_a"],
div[data-testid="stNumberInput"][key="factor_b"] {
    background-color: #eef6ff !important;
    border: 1px solid #d3e6ff !important;
    border-radius: 8px;
    padding: 8px 10px;
}
</style>
""", unsafe_allow_html=True)

# ================= FUNCIONES =================
def calc_oee(tiempo_plan, tiempo_paro, ciclo_ideal, piezas_totales, piezas_buenas, factor_a, factor_b):
    tiempo_operacion = max(tiempo_plan - tiempo_paro, 0)
    A = tiempo_operacion / tiempo_plan if tiempo_plan > 0 else 0
    P = (ciclo_ideal * piezas_totales) / (tiempo_operacion * 60) if tiempo_operacion > 0 else 0
    Q = piezas_buenas / piezas_totales if piezas_totales > 0 else 0
    OEE = A * P * Q * factor_a * factor_b
    return A, P, Q, OEE, tiempo_operacion

# ================= SIDEBAR =================
# Logo arriba
st.sidebar.markdown("<div style='margin-top:-55px; text-align:center;'></div>", unsafe_allow_html=True)
logo_paths = [Path("brandatta_logo.png"), Path("assets/brandatta_logo.png")]
for p in logo_paths:
    if p.exists():
        st.sidebar.image(str(p), width=180)
        break
st.sidebar.markdown("<div style='margin-top:-5px'></div>", unsafe_allow_html=True)

# Parámetros
st.sidebar.header("Parámetros")
tiempo_plan = st.sidebar.number_input("Tiempo planificado (min)", min_value=0.0, value=480.0)
tiempo_paro = st.sidebar.number_input("Tiempo de paros (min)", min_value=0.0, value=60.0)
ciclo_ideal = st.sidebar.number_input("Ciclo ideal (seg/un)", min_value=0.0, value=1.5)
piezas_totales = st.sidebar.number_input("Piezas totales", min_value=0, value=18000)
piezas_buenas = st.sidebar.number_input("Piezas de Calidad Aprobada", min_value=0, value=17500)
factor_a = st.sidebar.number_input("Factor Operativo A", min_value=0.0, value=1.0, step=0.1, key="factor_a")
factor_b = st.sidebar.number_input("Factor Operativo B", min_value=0.0, value=1.0, step=0.1, key="factor_b")

# ================= CÁLCULO =================
A, P, Q, OEE, tiempo_operacion = calc_oee(
    tiempo_plan, tiempo_paro, ciclo_ideal, piezas_totales, piezas_buenas, factor_a, factor_b
)

# ================= INTERFAZ =================
st.title("Calculadora de OEE")
st.write("Mide **Disponibilidad (A)**, **Rendimiento (P)**, **Calidad (Q)** y **Factores Operativos (A y B)** para obtener el OEE ajustado de tu línea de producción.")

cols = st.columns(5)
for c, name, val, desc in zip(
    cols,
    ["Disponibilidad (A)", "Rendimiento (P)", "Calidad (Q)", "OEE", "Tiempo Operación (min)"],
    [A, P, Q, OEE, tiempo_operacion],
    ["Operación / Plan", "(Ciclo ideal × Pzas) / (Operación × 60)", "Buenas / Totales", "A × P × Q × Factores", "Plan − Paros"]
):
    color = "ok" if (val >= 0.85 and name != "Tiempo Operación (min)") else ("mid" if (val >= 0.6 and name != "Tiempo Operación (min)") else "bad")
    val_txt = f"{val*100:.2f}%" if name != "Tiempo Operación (min)" else f"{val:.2f}"
    st.markdown(f"""
    <div class='kpi-card'>
      <div class='kpi-title'>{name}</div>
      <div class='kpi-value {color}'>{val_txt}</div>
      <div class='small-muted'>{desc}</div>
    </div>
    """, unsafe_allow_html=True)

# ================= CONCEPTOS =================
st.subheader("Conceptos")
st.markdown("""
<div class='formula'><b>Disponibilidad (A)</b> = Tiempo de operación / Tiempo planificado</div>
<div class='formula'><b>Rendimiento (P)</b> = (Ciclo ideal × Piezas totales) / Tiempo de operación real</div>
<div class='formula'><b>Calidad (Q)</b> = Piezas de Calidad Aprobada / Piezas totales</div>
<div class='formula'><b>Factores Operativos (A y B)</b> = Variables ajustables que representan condiciones adicionales de la operación (por ejemplo, eficiencia energética, desempeño del equipo o entorno).</div>
<div class='note'>
<b>OEE = A × P × Q × FactorA × FactorB</b><br>
• Mide la eficiencia global del equipo considerando factores adicionales.<br>
• OEE ≥ 85% suele considerarse “clase mundial”.<br>
• Analiza los factores A, P, Q y los factores operativos para identificar oportunidades de mejora.
</div>
""", unsafe_allow_html=True)

st.caption(f"© {datetime.now().year} — Brandatta • Calculadora OEE")
