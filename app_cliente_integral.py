# ============================================
# 🌟 CLIENTE INTEGRAL - DASHBOARD STREAMLIT (ACTUALIZADO)
# ============================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------
# ⚙️ Configuración general
# -----------------------------
st.set_page_config(page_title="Cliente Integral", layout="wide")
st.title("Cliente Integral")

# -----------------------------
# 🗂️ Cargar datos
# -----------------------------
@st.cache_data
def cargar_datos():
    df_residencial = pd.read_csv("base_clientes_residencial.csv")
    df_comercial = pd.read_csv("base_clientes_comercial.csv")
    df_dim_res = pd.read_csv("dimensiones_todas_residencial.csv")
    df_dim_com = pd.read_csv("dimensiones_todas_comercial.csv")
    return df_residencial, df_comercial, df_dim_res, df_dim_com

df_residencial, df_comercial, df_dim_res, df_dim_com = cargar_datos()

# -----------------------------
# 🎚️ Filtros en el sidebar
# -----------------------------
st.sidebar.header("⚙️ Configuración")
st.sidebar.markdown("Selecciona el tipo de cliente y las áreas de interés:")

# Paso 1️⃣: elegir tipo de cliente
tipo_cliente = st.sidebar.radio("Tipo de cliente:", ["Residencial", "Comercial"])

# Dependiendo del tipo, mostramos sus áreas
if tipo_cliente == "Residencial":
    df_clientes = df_residencial
    df_dim = df_dim_res
    areas_disponibles = ["brilla", "consumo", "sad"]
else:
    df_clientes = df_comercial
    df_dim = df_dim_com
    areas_disponibles = ["brilla", "consumo", "efisoluciones"]

areas_seleccionadas = st.sidebar.multiselect("Áreas disponibles", areas_disponibles, default=[areas_disponibles[0]])

if not areas_seleccionadas:
    st.warning("Selecciona al menos una área en el panel izquierdo.")
    st.stop()

# -----------------------------
# 🎯 Filtrado de clientes
# -----------------------------
filtro = np.logical_and.reduce([df_clientes[a] == 1 for a in areas_seleccionadas])
clientes_filtrados = df_clientes.loc[filtro, "id_cliente"].tolist()

col_info, col_img = st.columns([0.8, 0.2])
col_info.markdown(f"### Clientes seleccionados: {len(clientes_filtrados)}")
col_info.caption(f"Mostrando clientes **{tipo_cliente.lower()}s** que pertenecen a **todas las áreas seleccionadas:** {', '.join(areas_seleccionadas)}")

if len(clientes_filtrados) == 0:
    st.info("No hay clientes que pertenezcan simultáneamente a todas las áreas seleccionadas.")
    st.stop()

# -----------------------------
# 📊 Calcular promedios por cliente
# -----------------------------
df_dim_filtrado = df_dim[
    (df_dim["area"].isin(areas_seleccionadas)) &
    (df_dim["id_cliente"].isin(clientes_filtrados))
]

df_resultado = (
    df_dim_filtrado.groupby("id_cliente")[["dimension_economica", "dimension_relacional", "dimension_cumplimiento", "dimension_potencial"]]
    .mean()
    .reset_index()
)

# -----------------------------
# 📈 Promedios generales del grupo
# -----------------------------
promedios_generales = df_resultado.drop(columns="id_cliente").mean().to_frame("promedio").T

# -----------------------------
# 🧾 Layout principal
# -----------------------------
st.markdown("---")
st.subheader("📋 Promedios por cliente")
st.dataframe(df_resultado, use_container_width=True)

# Sección visual
st.markdown("---")
st.subheader("📊 Resumen visual de las dimensiones")

col1, col2 = st.columns(2)

# 📉 Radar Chart
categorias = list(promedios_generales.columns)
valores = list(promedios_generales.iloc[0])

fig_radar = go.Figure()
fig_radar.add_trace(go.Scatterpolar(
    r=valores + [valores[0]],
    theta=categorias + [categorias[0]],
    fill='toself',
    name='Promedio grupo',
    line_color="#0088cc"
))
fig_radar.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
    showlegend=False,
    template="plotly_white",
    height=400
)
col1.plotly_chart(fig_radar, use_container_width=True)
col1.caption("Perfil promedio del grupo por dimensión")

# 📊 Bar Chart
fig_bar = px.bar(
    promedios_generales.melt(var_name="Dimensión", value_name="Promedio"),
    x="Dimensión", y="Promedio",
    text_auto=".2f",
    color="Dimensión",
    color_discrete_sequence=px.colors.qualitative.Pastel
)
fig_bar.update_layout(
    template="plotly_white",
    showlegend=False,
    height=400,
    yaxis=dict(range=[0, 1])
)
col2.plotly_chart(fig_bar, use_container_width=True)
col2.caption("Comparativo de promedios por dimensión")

# -----------------------------
# 📥 Descargar resultados
# -----------------------------
st.markdown("---")
st.subheader("⬇️ Descargar resultados")
csv = df_resultado.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Descargar promedios por cliente (.csv)",
    data=csv,
    file_name=f"promedios_dimensiones_{tipo_cliente.lower()}.csv",
    mime="text/csv"
)

# -----------------------------
# 🆕 Segmentación básica
# -----------------------------
df_resultado["promedio_global"] = df_resultado[
    ["dimension_economica", "dimension_relacional", "dimension_cumplimiento", "dimension_potencial"]
].mean(axis=1)

p33 = df_resultado["promedio_global"].quantile(0.33)
p66 = df_resultado["promedio_global"].quantile(0.66)

def clasificar_cliente(valor):
    if valor <= p33:
        return "Malo"
    elif valor <= p66:
        return "Intermedio"
    else:
        return "Bueno"

df_resultado["segmento"] = df_resultado["promedio_global"].apply(clasificar_cliente)
df_resultado = df_resultado.sort_values("promedio_global", ascending=False).reset_index(drop=True)

st.markdown("---")
st.subheader("📋 Segmentación básica de clientes")
st.dataframe(df_resultado, use_container_width=True)

# -----------------------------
# 📊 Distribución de segmentos
# -----------------------------
st.markdown("---")
st.subheader("📊 Distribución de segmentos")

col1, col2 = st.columns(2)

fig_pie = px.pie(
    df_resultado,
    names="segmento",
    title="Distribución de clientes por segmento",
    color="segmento",
    color_discrete_map={"Bueno": "#6CC24A", "Intermedio": "#FFD700", "Malo": "#E74C3C"}
)
col1.plotly_chart(fig_pie, use_container_width=True)

fig_bar_segmentos = (
    df_resultado.groupby("segmento")["promedio_global"]
    .mean()
    .reset_index()
    .sort_values("promedio_global", ascending=False)
)
fig_bar = px.bar(
    fig_bar_segmentos,
    x="segmento",
    y="promedio_global",
    text_auto=".2f",
    color="segmento",
    color_discrete_map={"Bueno": "#6CC24A", "Intermedio": "#FFD700", "Malo": "#E74C3C"}
)
fig_bar.update_layout(template="plotly_white", showlegend=False, height=400, yaxis=dict(range=[0, 1]))
col2.plotly_chart(fig_bar, use_container_width=True)

# ==========================================================
# 🔍 SECCIÓN: Buscador de cliente (detalle individual)
# ==========================================================
st.markdown("---")
st.subheader("🔎 Consulta detallada de cliente")

lista_clientes = df_resultado["id_cliente"].tolist()
cliente_seleccionado = st.selectbox("Selecciona un cliente:", lista_clientes)

if cliente_seleccionado:
    cliente_data = df_resultado[df_resultado["id_cliente"] == cliente_seleccionado].iloc[0]

    st.markdown(f"### 🧍 Cliente seleccionado: `{cliente_seleccionado}`")
    st.markdown(f"**Segmento:** {cliente_data['segmento']}  \n**Promedio global:** {cliente_data['promedio_global']:.2f}")

    # Indicadores personalizados según tipo
    if tipo_cliente == "Residencial":
        indicadores = {
            "brilla": [
                {"indicador": "Número de compras", "valor": np.random.randint(0, 11), "unidad": "compras"},
                {"indicador": "Monto promedio por compra", "valor": round(np.random.uniform(100000, 1000000), -3), "unidad": "COP"},
                {"indicador": "Pagos a tiempo", "valor": round(np.random.uniform(60, 100), 1), "unidad": "%"}
            ],
            "consumo": [
                {"indicador": "Consumo mensual promedio", "valor": round(np.random.uniform(0, 200), 1), "unidad": "m³"},
                {"indicador": "Variabilidad de consumo", "valor": round(np.random.uniform(0, 40), 1), "unidad": "%"},
                {"indicador": "Meses con consumo cero", "valor": np.random.randint(0, 4), "unidad": "meses"}
            ],
            "sad": [
                {"indicador": "Órdenes de servicio", "valor": np.random.randint(0, 6), "unidad": "órdenes"},
                {"indicador": "Tiempo promedio de atención", "valor": round(np.random.uniform(1, 7), 1), "unidad": "días"},
                {"indicador": "Satisfacción del cliente", "valor": round(np.random.uniform(70, 100), 1), "unidad": "%"}
            ]
        }
    else:  # Comercial
        indicadores = {
            "brilla": [
                {"indicador": "Número de compras corporativas", "valor": np.random.randint(0, 21), "unidad": "compras"},
                {"indicador": "Monto promedio de compra", "valor": round(np.random.uniform(500000, 5000000), -3), "unidad": "COP"},
                {"indicador": "Pagos a tiempo", "valor": round(np.random.uniform(50, 100), 1), "unidad": "%"}
            ],
            "consumo": [
                {"indicador": "Consumo mensual promedio", "valor": round(np.random.uniform(100, 1000), 1), "unidad": "m³"},
                {"indicador": "Variabilidad de consumo", "valor": round(np.random.uniform(10, 60), 1), "unidad": "%"},
                {"indicador": "Meses con consumo bajo", "valor": np.random.randint(0, 6), "unidad": "meses"}
            ],
            "efisoluciones": [
                {"indicador": "Proyectos ejecutados", "valor": np.random.randint(0, 10), "unidad": "proyectos"},
                {"indicador": "Duración promedio del proyecto", "valor": round(np.random.uniform(2, 10), 1), "unidad": "meses"},
                {"indicador": "Nivel de satisfacción", "valor": round(np.random.uniform(70, 100), 1), "unidad": "%"}
            ]
        }

    st.markdown("#### Indicadores detallados por área")

    for area in areas_seleccionadas:
        if area in indicadores:
            st.markdown(f"##### 🟢 {area.upper()}")
            cols = st.columns(3)
            for i, ind in enumerate(indicadores[area]):
                with cols[i]:
                    st.metric(ind["indicador"], f"{ind['valor']} {ind['unidad']}")
            st.markdown("")

    # Radar individual
    st.markdown("#### Dimensiones normalizadas del cliente")
    radar_df = cliente_data[["dimension_economica", "dimension_relacional", "dimension_cumplimiento", "dimension_potencial"]].to_frame().T
    categorias = radar_df.columns.tolist()
    valores = radar_df.iloc[0].tolist()

    fig_radar_cliente = go.Figure()
    fig_radar_cliente.add_trace(go.Scatterpolar(
        r=valores + [valores[0]],
        theta=categorias + [categorias[0]],
        fill='toself',
        name=f"Cliente {cliente_seleccionado}",
        line_color="#006699"
    ))
    fig_radar_cliente.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])), showlegend=False, template="plotly_white")
    st.plotly_chart(fig_radar_cliente, use_container_width=True)
