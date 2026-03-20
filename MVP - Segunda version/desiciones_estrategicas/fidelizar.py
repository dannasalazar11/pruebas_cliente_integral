import streamlit as st
import pandas as pd
import numpy as np
from utils.db import ejecutar_query_databricks
from services.variables_por_servicio import formatear_lista_fechas
from services.descripcion_variables import render_descripcion_variables

def fidelizar():
    # --- ESTILOS CSS EXCLUSIVOS (Identidad Azul) ---
    st.markdown("""
        <style>
        /* Título con clase única */
        .title-fid { 
            font-size: 2.2rem; font-weight: 800; color: #1E3A8A !important; margin-bottom: 0.5rem; 
        }
        /* Caja de información azul */
        .info-box-fid { 
            background-color: #F0F4F8; 
            padding: 20px; 
            border-left: 5px solid #1E3A8A; 
            border-radius: 5px;
            margin-bottom: 20px;
            color: #1E3A8A;
        }
        /* Círculos numéricos azules */
        .step-number-fid {
            background-color: #1E3A8A;
            color: white;
            border-radius: 50%;
            padding: 2px 8px;
            font-weight: bold;
            margin-right: 5px;
        }
        
        /* SELECTOR DE BOTÓN ESPECÍFICO PARA FIDELIZAR */
        /* Solo afecta al botón que contiene la palabra "Prioritarios" */
        div.stButton > button:has(p:contains("Prioritarios")) {
            background-color: #1E3A8A !important;
            color: white !important;
            border-radius: 20px !important;
            height: 3em !important;
            font-weight: bold !important;
            border: none !important;
            width: 100%;
        }
        
        div.stButton > button:has(p:contains("Prioritarios")):hover {
            background-color: #172554 !important;
            border: none !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <style>
        .title-fid { 
            font-size: 3.5rem !important; /* Aumentado de 2.2 a 3.5 */
            font-weight: 900 !important;   /* Más grueso */
            color: #1E3A8A !important; 
            margin-bottom: 0px !important;
            line-height: 1.1 !important;  /* Ajuste de espacio */
        }
        .subtitle-fid {
            font-size: 1.2rem;
            color: #64748b;
            margin-bottom: 2rem;
        }
        /* ... el resto de tu CSS (info-box-fid, etc.) ... */
        </style>
    """, unsafe_allow_html=True)

    # --- ENCABEZADO ---
    st.markdown('<p class="title-fid">Estrategia de Fidelización</p>', unsafe_allow_html=True)
    
    # --- SECCIÓN DE AYUDA (Tabs) ---
    tab_guia, tab_pasos, tab_orden = st.tabs([
        "💡 ¿Para qué sirve?", 
        "🛠️ ¿Cómo funciona?", 
        "📉 Interpretación"
    ])

    with tab_guia:
        st.markdown("""
        <div class="info-box-fid">
            Esta funcionalidad ayuda a <b>identificar qué clientes conviene fidelizar primero</b>. 
            Utilizamos un <b>servicio ancla</b> (donde el cliente ya es estable) como punto de apoyo 
            para potenciar un <b>servicio objetivo</b> con oportunidad de crecimiento.
        </div>
        """, unsafe_allow_html=True)

    with tab_pasos:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("<span class='step-number-fid'>1</span> Define la <b>categoría</b> del cliente.", unsafe_allow_html=True)
            st.markdown("<span class='step-number-fid'>2</span> Selecciona el <b>servicio ancla</b> (actual).", unsafe_allow_html=True)
            st.markdown("<span class='step-number-fid'>3</span> Elige el <b>servicio a potenciar</b>.", unsafe_allow_html=True)
        with col_b:
            st.markdown("<span class='step-number-fid'>4</span> Define la <b>cantidad</b> de clientes que quieres determinar.", unsafe_allow_html=True)
            st.markdown("<span class='step-number-fid'>5</span> Ejecuta para obtener el <b>listado prioritario</b> de clientes a fidelizar.", unsafe_allow_html=True)

    with tab_orden:
        st.info("""
        Los clientes aparecen ordenados según su **conveniencia estratégica**:
        1. **Fortaleza del ancla:** Lealtad en el servicio.
        2. **Oportunidad en objetivo:** Potencial en el servicio.
        3. **Estabilidad general:** Bajo riesgo de pérdida..
        """)

    st.divider()

    # =========================
    # 1. PARÁMETROS (Keys añadidas)
    # =========================
    with st.container():
        st.subheader("⚙️ Parámetros de la Estrategia")
        c1, c2, c3 = st.columns([1.5, 1.5, 1])
        
        with c1:
            tipo_cliente = st.selectbox("👤 Tipo de cliente", ["Residencial", "Comercial"], key="fid_tipo_cli")
        
        servicios_posibles = ["Consumo", "RTR", "SAD"] if tipo_cliente == "Residencial" else ["Consumo", "RTR", "Efisoluciones"]

        with c2:
            servicio_ancla = st.selectbox("⚓ Servicio ancla", servicios_posibles, key="fid_serv_ancla")
        
        with c3:
            servicio_objetivo = st.selectbox(
            "🚀 Servicio a potenciar",
            [s for s in servicios_posibles if s != servicio_ancla],
            key="fid_serv_obj"
            )

        c4, _ = st.columns([1.5, 2.5])
        with c4:
            top_n = st.number_input("🔝 Cantidad", min_value=1, max_value=10000, value=100, key="fid_top_n")


    st.markdown("<br>", unsafe_allow_html=True)


    # El nombre debe contener "Prioritarios" para el CSS
    ejecutar = st.button("🔍 Identificar Clientes")

    if ejecutar:
        with st.spinner("Analizando comportamiento..."):
            # (Toda tu lógica SQL intacta)
            tipo_cliente_sql = tipo_cliente.lower()
            tabla_dim_ancla = f"analiticaefg.clienteintegral.{servicio_ancla.lower()}_{tipo_cliente_sql}_consolidado_dimensiones"
            tabla_dim_obj = f"analiticaefg.clienteintegral.{servicio_objetivo.lower()}_{tipo_cliente_sql}_consolidado_dimensiones"
            tabla_var_ancla = f"analiticaefg.clienteintegral.{servicio_ancla.lower()}_{tipo_cliente_sql}_consolidado_variables"
            tabla_var_obj = f"analiticaefg.clienteintegral.{servicio_objetivo.lower()}_{tipo_cliente_sql}_consolidado_variables"
            tabla_contratos = f"analiticaefg.clienteintegral.modelo_contratos{tipo_cliente}"

            def _get_table_columns(full_name: str):
                parts = full_name.split(".")
                q = f"SELECT column_name FROM system.information_schema.columns WHERE table_catalog='{parts[0]}' AND table_schema='{parts[1]}' AND table_name='{parts[2]}'"
                df_cols = ejecutar_query_databricks(q)
                if df_cols is not None and not df_cols.empty:
                    cols = df_cols["column_name"].tolist()
                    return [c for c in cols if c.lower() not in ("idcliente", "tipoidentificacion", "identificacion")]
                return []

            cols_ancla = _get_table_columns(tabla_var_ancla)
            cols_obj = _get_table_columns(tabla_var_obj)

            select_vars_ancla = ",\n                ".join([f"va.`{c}` AS `{servicio_ancla.lower()}_{c}`" for c in cols_ancla])
            select_vars_obj = ",\n                ".join([f"vo.`{c}` AS `{servicio_objetivo.lower()}_{c}`" for c in cols_obj])
            extra_sql = ",\n                " + ",\n                ".join(filter(None, [select_vars_ancla, select_vars_obj])) if (select_vars_ancla or select_vars_obj) else ""

            query = f"""
            WITH base AS (
                SELECT a.IdCliente, a.TipoIdentificacion, a.Identificacion,
                       a.Economica AS econ_ancla, a.Cumplimiento AS cump_ancla, a.Relacional AS rel_ancla,
                       o.Economica AS econ_obj, o.Relacional AS rel_obj, o.Potencial AS pot_obj
                FROM {tabla_dim_ancla} a
                INNER JOIN {tabla_dim_obj} o ON a.IdCliente = o.IdCliente
            ),
            scores AS (
                SELECT *,
                       (0.4 * cump_ancla + 0.35 * rel_ancla + 0.25 * econ_ancla) AS F_ancla,
                       (0.5 * pot_obj + 0.3 * (1 - rel_obj) + 0.2 * (1 - econ_obj)) AS B_objetivo,
                       (0.6 * cump_ancla + 0.4 * rel_ancla) AS S_cliente
                FROM base
            ),
            final_scores AS (
                SELECT IdCliente, TipoIdentificacion, Identificacion,
                       (0.5 * B_objetivo + 0.3 * F_ancla + 0.2 * S_cliente) AS Score_FID
                FROM scores
            )
            SELECT s.IdCliente, s.TipoIdentificacion, s.Identificacion, s.Score_FID, c.Contratos, c.ContratosActivos {extra_sql}
            FROM final_scores s
            LEFT JOIN {tabla_contratos} c ON s.IdCliente = c.IdCliente
            LEFT JOIN {tabla_var_ancla} va ON s.IdCliente = va.IdCliente
            LEFT JOIN {tabla_var_obj} vo ON s.IdCliente = vo.IdCliente
            ORDER BY s.Score_FID DESC LIMIT {top_n}
            """

            df_resultado = ejecutar_query_databricks(query)

        if df_resultado is not None and not df_resultado.empty:
            if "rtr_fechas_proximas_rtr" in df_resultado.columns:
                df_resultado["rtr_fechas_proximas_rtr"] = df_resultado["rtr_fechas_proximas_rtr"].apply(formatear_lista_fechas)

            st.success(f"✅ Se han encontrado los {len(df_resultado)} clientes a fidelizar.")
            
            # --- KPIs ---
            m1, m2, m3, m4 = st.columns(4)
            df_resultado['Score_FID'] = pd.to_numeric(df_resultado['Score_FID'], errors='coerce')
            m1.metric("Score Máximo", f"{df_resultado['Score_FID'].max():.2f}")
            m2.metric("Score Mínimo", f"{df_resultado["Score_FID"].min():.2f}")
            m3.metric("Score Promedio", f"{df_resultado['Score_FID'].mean():.2f}")
            
            def count_contracts(x):
                if isinstance(x, (list, np.ndarray)): return len(x)
                if isinstance(x, str): return len(x.split(','))
                return 1 if pd.notnull(x) and str(x).strip() != "" else 0

            total_c = df_resultado['Contratos'].apply(count_contracts).sum() if 'Contratos' in df_resultado.columns else 0
            m4.metric("Total Contratos", int(total_c))

            st.download_button(
                label="📥 Descargar Listado (CSV)",
                data=df_resultado.to_csv(index=False).encode('utf-8'),
                file_name=f'fidelizacion_{tipo_cliente}.csv',
                mime='text/csv',
                key="fid_dl_btn"
            )

            st.dataframe(
                df_resultado.style.background_gradient(subset=['Score_FID'], cmap='Blues'),
                width='stretch',
                hide_index=True
            )

            render_descripcion_variables(servicio_ancla)

            render_descripcion_variables(servicio_objetivo)
        else:
            st.warning("No se encontraron clientes para estos criterios.")

