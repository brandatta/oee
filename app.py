import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

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
</style>
""", unsafe_allow_html=True)

# ================= FUNCIONES =================
def calc_oee(tiempo_plan, tiempo_paro, ciclo_ideal, piezas_totales, piezas_buenas):
    tiempo_operacion = max(tiempo_plan - tiempo_paro, 0)
    A = tiempo_operacion / tiempo_plan if tiempo_plan > 0 else 0
    P = (ciclo_ideal * piezas_totales) / (tiempo_operacion * 60) if tiempo_operacion > 0 else 0
    Q = piezas_buenas / piezas_totales if piezas_totales > 0 else 0
    OEE = A * P * Q
    return A, P, Q, OEE, tiempo_operacion

# ================= SIDEBAR =================
st.sidebar.header("⚙️ Parámetros")
tiempo_plan = st.sidebar.number_input("Tiempo planificado (min)", min_value=0.0, value=480.0)
tiempo_paro = st.sidebar.number_input("Tiempo de paros (min)", min_value=0.0, value=60.0)
ciclo_ideal = st.sidebar.number_input("Ciclo ideal (seg/un)", min_value=0.0, value=1.5)
piezas_totales = st.sidebar.number_input("Piezas totales", min_value=0, value=18000)
piezas_buenas = st.sidebar.number_input("Piezas buenas", min_value=0, value=17500)

# ================= CÁLCULO =================
A, P, Q, OEE, tiempo_operacion = calc_oee(
    tiempo_plan, tiempo_paro, ciclo_ideal, piezas_totales, piezas_buenas
)

# ================= INTERFAZ =================
st.title("📊 Calculadora de OEE")
st.write("Mide **Disponibilidad (A)**, **Rendimiento (P)**, **Calidad (Q)** y **OEE** en tu línea de producción.")

cols = st.columns(5)
for c, name, val, desc in zip(
    cols,
    ["Disponibilidad (A)", "Rendimiento (P)", "Calidad (Q)", "OEE", "Tiempo Operación (min)"],
    [A, P, Q, OEE, tiempo_operacion],
    ["Operación / Plan", "(Ciclo ideal × Pzas) / (Operación × 60)", "Buenas / Totales", "A × P × Q", "Plan − Paros"]
):
    color = "ok" if val >= 0.85 else "mid" if val >= 0.6 else "bad"
    val_txt = f"{val*100:.2f}%" if name != "Tiempo Operación (min)" else f"{val:.2f}"
    st.markdown(f"""
    <div class='kpi-card'>
      <div class='kpi-title'>{name}</div>
      <div class='kpi-value {color}'>{val_txt}</div>
      <div class='small-muted'>{desc}</div>
    </div>
    """, unsafe_allow_html=True)

# ================= CONCEPTOS =================
st.subheader("📘 Conceptos clave")
st.markdown("""
<div class='formula'><b>Disponibilidad (A)</b> = Tiempo de operación / Tiempo planificado</div>
<div class='formula'><b>Rendimiento (P)</b> = (Ciclo ideal × Piezas totales) / Tiempo de operación real</div>
<div class='formula'><b>Calidad (Q)</b> = Piezas buenas / Piezas totales</div>
<div class='note'>
<b>OEE = A × P × Q</b><br>
• Mide la eficiencia global del equipo.<br>
• OEE ≥ 85% suele considerarse “clase mundial”.<br>
• Analiza los factores A, P y Q para identificar oportunidades de mejora.
</div>
""", unsafe_allow_html=True)

st.caption(f"© {datetime.now().year} — Interfaces Brandatta • Calculadora OEE")
