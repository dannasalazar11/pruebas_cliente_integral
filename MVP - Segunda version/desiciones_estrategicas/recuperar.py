import streamlit as st
from utils.db import ejecutar_query_databricks
import pandas as pd
from services.variables_por_servicio import formatear_lista_fechas
import numpy as np
from services.descripcion_variables import render_descripcion_variables



def recuperar():
    # --- ESTILOS CSS EXCLUSIVOS (Identidad Roja/Recuperación) ---
    st.markdown("""
        <style>
        /* Título con clase única */
        .title-rec { 
            font-size: 3.5rem !important; 
            font-weight: 900 !important; 
            color: #991B1B !important; 
            margin-bottom: 0px !important;
            line-height: 1.1 !important;
        }
        /* Caja de información roja */
        .info-box-rec { 
            background-color: #FEF2F2; 
            padding: 20px; 
            border-left: 5px solid #991B1B; 
            border-radius: 5px;
            margin-bottom: 20px;
            color: #991B1B;
        }
        /* Círculos numéricos rojos */
        .step-number-rec {
            background-color: #991B1B;
            color: white;
            border-radius: 50%;
            padding: 2px 8px;
            font-weight: bold;
            margin-right: 5px;
        }
        
        /* SELECTOR DE BOTÓN ESPECÍFICO PARA RECUPERAR */
        /* Solo afecta al botón que contiene la palabra "Urgentes" */
        div.stButton > button:has(p:contains("Urgentes")) {
            background-color: #991B1B !important;
            color: white !important;
            border-radius: 20px !important;
            height: 3em !important;
            font-weight: bold !important;
            border: none !important;
            width: 100%;
        }
        
        div.stButton > button:has(p:contains("Urgentes")):hover {
            background-color: #7F1D1D !important;
            border: none !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- ENCABEZADO ---
    st.markdown('<p class="title-rec">Estrategia de Recuperación</p>', unsafe_allow_html=True)
    
    # --- SECCIÓN DE AYUDA (Tabs) ---
    tab_guia, tab_pasos, tab_orden = st.tabs([
        "💡 ¿Para qué sirve?", 
        "🛠️ ¿Cómo funciona?", 
        "📉 Interpretación"
    ])

    with tab_guia:
        st.markdown("""
        <div class="info-box-rec">
            Esta funcionalidad identifica clientes que muestran un <b>deterioro</b> en su relación con la empresa. 
            Prioriza a aquellos que <b>fueron valiosos</b> y que todavía presentan una <b>viabilidad de recuperación</b> 
            basada en su potencial y comportamiento histórico.
        </div>
        """, unsafe_allow_html=True)

    with tab_pasos:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("<span class='step-number-rec'>1</span> Define la <b>categoría</b> de cliente.", unsafe_allow_html=True)
            st.markdown("<span class='step-number-rec'>2</span> Selecciona el <b>servicio</b> donde quieres identificar el riesgo.", unsafe_allow_html=True)
        with col_b:
            st.markdown("<span class='step-number-rec'>3</span> Ajusta la <b>cantidad</b> de clientes a extraer.", unsafe_allow_html=True)
            st.markdown("<span class='step-number-rec'>4</span> Ejecuta para obtener el <b>listado prioritario</b> de clientes a recuperar.", unsafe_allow_html=True)

    with tab_orden:
        st.info("""
        El **Score_REC** se calcula ponderando tres factores críticos:
        1. **Deterioro (55%):** Caída en cumplimiento y relación con la empresa.
        2. **Valor Histórico (30%):** Importancia económica del cliente.
        3. **Viabilidad (15%):** Probabilidad de éxito si se contacta (basado en potencial).
        """)

    st.divider()

    # =========================
    # 1. PARÁMETROS
    # =========================
    with st.container():
        st.subheader("⚙️ Configuración de la Recuperación")
        c1, c2, c3 = st.columns([1.5, 1.5, 1])
        
        with c1:
            tipo_cliente = st.selectbox("👤 Tipo de cliente", ["Residencial", "Comercial"], key="rec_tipo_cli")
        
        servicios_posibles = ["Consumo", "RTR", "SAD"] if tipo_cliente == "Residencial" else ["Consumo", "RTR", "Efisoluciones"]

        with c2:
            servicio = st.selectbox("🚩 Servicio en Riesgo", servicios_posibles, key="rec_serv_riesgo")
        
        with c3:
            top_n = st.number_input("🔝 Cantidad", min_value=1, max_value=10000, value=100, key="rec_top_n")

    st.markdown("<br>", unsafe_allow_html=True)

    # El nombre debe contener "Urgentes" para el CSS
    ejecutar = st.button("🔍 Identificar Clientes")

    if ejecutar:
        with st.spinner("Analizando patrones de abandono..."):
            tipo_cliente_sql = tipo_cliente.lower()
            pref = servicio.lower()
            tabla_dim = f"analiticaefg.clienteintegral.{pref}_{tipo_cliente_sql}_consolidado_dimensiones"
            tabla_var = f"analiticaefg.clienteintegral.{pref}_{tipo_cliente_sql}_consolidado_variables"
            tabla_contratos = f"analiticaefg.clienteintegral.modelo_contratos{tipo_cliente}"


            def _get_columns(full_name):
                parts = full_name.split(".")
                q = f"SELECT column_name FROM system.information_schema.columns WHERE table_catalog='{parts[0]}' AND table_schema='{parts[1]}' AND table_name='{parts[2]}'"
                df_cols = ejecutar_query_databricks(q)
                if df_cols is not None and not df_cols.empty:
                    cols = df_cols["column_name"].tolist()
                    return [c for c in cols if c.lower() not in ("idcliente", "tipoidentificacion", "identificacion")]
                return []

            cols_vars = _get_columns(tabla_var)
            select_vars = ",\n                ".join([f"v.`{c}` AS `{pref}_{c}`" for c in cols_vars])
            if select_vars.strip():
                select_vars = ",\n                " + select_vars

            query = f"""
            WITH base AS (
                SELECT
                    d.IdCliente, d.TipoIdentificacion, d.Identificacion,
                    (0.55 * (1 - d.Cumplimiento) + 0.45 * (1 - d.Relacional)) AS Deterioro,
                    d.Economica AS Valor,
                    (0.65 * d.Potencial + 0.35 * d.Relacional) AS Viabilidad
                FROM {tabla_dim} d
            ),
            scored AS (
                SELECT *,
                    (0.55 * Deterioro + 0.30 * Valor + 0.15 * Viabilidad) AS Score_REC
                FROM base
            )
            SELECT
                s.IdCliente,
                s.TipoIdentificacion,
                s.Identificacion,
                s.Score_REC,
                c.Contratos, c.ContratosActivos
                {select_vars}
            FROM scored s
            LEFT JOIN {tabla_contratos} c ON s.IdCliente = c.IdCliente
            LEFT JOIN {tabla_var} v ON s.IdCliente = v.IdCliente
            ORDER BY s.Score_REC DESC LIMIT {top_n}
            """

            df_resultado = ejecutar_query_databricks(query)

        if df_resultado is not None and not df_resultado.empty:
            st.success(f"✅ Se han detectado {len(df_resultado)} clientes con necesidad de intervención.")
            
            # --- KPIs ---
            m1, m2, m3, m4 = st.columns(4)
            df_resultado['Score_REC'] = pd.to_numeric(df_resultado['Score_REC'], errors='coerce')
            m1.metric("Score Máximo", f"{df_resultado['Score_REC'].max():.2f}")
            m2.metric("Score Mínimo", f"{df_resultado["Score_REC"].min():.2f}")
            m3.metric("Score Promedio", f"{df_resultado['Score_REC'].mean():.2f}")

            def count_contracts(x):
                if isinstance(x, (list, np.ndarray)):
                    return len(x)
                if isinstance(x, str):
                    return len(x.split(','))
                return 1 if pd.notnull(x) and str(x).strip() != "" else 0

            total_c = (
                df_resultado['Contratos'].apply(count_contracts).sum()
                if 'Contratos' in df_resultado.columns else 0
            )

            m4.metric("Total Contratos", int(total_c))


            st.download_button(
                label="📥 Descargar Plan de Acción (CSV)",
                data=df_resultado.to_csv(index=False).encode('utf-8'),
                file_name=f'recuperacion_{pref}_{tipo_cliente}.csv',
                mime='text/csv',
                key="rec_dl_btn"
            )

            if df_resultado is not None and not df_resultado.empty:
                if "rtr_fechas_proximas_rtr" in df_resultado.columns:
                    df_resultado["rtr_fechas_proximas_rtr"] = df_resultado["rtr_fechas_proximas_rtr"].apply(formatear_lista_fechas)

            # Estilo con gradiente rojo
            st.dataframe(
                df_resultado.style.background_gradient(subset=['Score_REC'], cmap='Reds'),
                width='stretch',
                hide_index=True
            )

            render_descripcion_variables(servicio)
        else:
            st.warning("No se encontraron clientes que cumplan los criterios de recuperación.")