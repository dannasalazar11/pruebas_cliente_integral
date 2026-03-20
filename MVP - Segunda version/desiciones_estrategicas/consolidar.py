import streamlit as st
from utils.db import ejecutar_query_databricks
import pandas as pd
from services.variables_por_servicio import formatear_lista_fechas
import numpy as np
from services.descripcion_variables import render_descripcion_variables


def consolidar():
    # --- ESTILOS CSS EXCLUSIVOS (Identidad Naranja/Consolidación) ---
    st.markdown("""
        <style>
        /* Título con clase única */
        .title-con { 
            font-size: 3.5rem !important; 
            font-weight: 900 !important; 
            color: #C2410C !important; /* Naranja oscuro */
            margin-bottom: 0px !important;
            line-height: 1.1 !important;
        }
        /* Caja de información naranja */
        .info-box-con { 
            background-color: #FFF7ED; 
            padding: 20px; 
            border-left: 5px solid #F97316; 
            border-radius: 5px;
            margin-bottom: 20px;
            color: #9A3412;
        }
        /* Círculos numéricos naranjas */
        .step-number-con {
            background-color: #F97316;
            color: white;
            border-radius: 50%;
            padding: 2px 8px;
            font-weight: bold;
            margin-right: 5px;
        }
        
        /* SELECTOR DE BOTÓN ESPECÍFICO PARA CONSOLIDAR */
        /* Solo afecta al botón que contiene la palabra "Consolidados" */
        div.stButton > button:has(p:contains("Consolidados")) {
            background-color: #F97316 !important;
            color: white !important;
            border-radius: 20px !important;
            height: 3em !important;
            font-weight: bold !important;
            border: none !important;
            width: 100%;
        }
        
        div.stButton > button:has(p:contains("Consolidados")):hover {
            background-color: #EA580C !important;
            border: none !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- ENCABEZADO ---
    st.markdown('<p class="title-con">Estrategia de Consolidación</p>', unsafe_allow_html=True)
    
    # --- SECCIÓN DE AYUDA (Tabs) ---
    tab_guia, tab_pasos, tab_orden = st.tabs([
        "💡 ¿Para qué sirve?", 
        "🛠️ ¿Cómo funciona?", 
        "📉 Interpretación"
    ])

    with tab_guia:
        st.markdown("""
        <div class="info-box-con">
            Esta funcionalidad identifica clientes <b>estables, confiables y valiosos</b>. 
            Son el motor del negocio; la estrategia recomendada es <b>mantener la excelencia operativa</b> 
            sin saturarlos con ofertas, asegurando que su fidelidad natural no se vea interrumpida.
        </div>
        """, unsafe_allow_html=True)

    with tab_pasos:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("<span class='step-number-con'>1</span> Selecciona la <b>categoría</b> a analizar.", unsafe_allow_html=True)
            st.markdown("<span class='step-number-con'>2</span> Elige los <b>servicios</b> en donde buscar estabilidad.", unsafe_allow_html=True)
        with col_b:
            st.markdown("<span class='step-number-con'>3</span>Ajusta la <b>cantidad</b> de clientes a extraer.", unsafe_allow_html=True)
            st.markdown("<span class='step-number-con'>4</span> Ejecuta para obtener el <b>listado prioritario</b> de clientes a consolidar.", unsafe_allow_html=True)

    with tab_orden:
        st.info("""
        El **Score_CON** mide la robustez de la relación:
        1. **Fidelidad Relacional (55%):** Basado en cumplimiento y tiempo de permanencia.
        2. **Valor Recurrente (30%):** Aporte económico constante.
        3. **Madurez (15%):** Identifica clientes que ya están consolidados en su uso del servicio.
        """)

    st.divider()

    # =========================
    # 1. PARÁMETROS
    # =========================
    with st.container():
        st.subheader("⚙️ Configuración del Análisis")
        c1, c2, c3 = st.columns([1.5, 2, 1])
        
        with c1:
            tipo_cliente = st.selectbox("👤 Tipo de cliente", ["Residencial", "Comercial"], key="con_tipo_cli")
        
        servicios_posibles = ["Consumo", "RTR", "SAD"] if tipo_cliente == "Residencial" else ["Consumo", "RTR", "Efisoluciones"]

        with c2:
            servicios_sel = st.multiselect("📚 Servicios a evaluar", servicios_posibles, key="con_serv_sel")
        
        with c3:
            top_n = st.number_input("🔝 Cantidad", min_value=1, max_value=10000, value=100, key="con_top_n")

    if not servicios_sel:
        st.info("⚠️ Por favor, selecciona al menos un servicio para realizar el análisis de consolidación.")
        return

    st.markdown("<br>", unsafe_allow_html=True)

    # El nombre contiene "Consolidados" para activar el CSS naranja
    ejecutar = st.button("🔍 Identificar Clientes")

    if ejecutar:
        with st.spinner("Analizando clientes a consolidar..."):
            tipo_cliente_sql = tipo_cliente.lower()

            # Tablas por servicio
            tablas_dim = {s: f"analiticaefg.clienteintegral.{s.lower()}_{tipo_cliente_sql}_consolidado_dimensiones" for s in servicios_sel}
            tablas_var = {s: f"analiticaefg.clienteintegral.{s.lower()}_{tipo_cliente_sql}_consolidado_variables" for s in servicios_sel}
            tabla_contratos = f"analiticaefg.clienteintegral.modelo_contratos{tipo_cliente}"


            def _get_columns(full_name):
                parts = full_name.split(".")
                q = f"SELECT column_name FROM system.information_schema.columns WHERE table_catalog='{parts[0]}' AND table_schema='{parts[1]}' AND table_name='{parts[2]}'"
                df_cols = ejecutar_query_databricks(q)
                if df_cols is not None and not df_cols.empty:
                    cols = df_cols["column_name"].tolist()
                    return [c for c in cols if c.lower() not in ("idcliente", "tipoidentificacion", "identificacion")]
                return []

            # Construcción dinámica de la Query
            selects_scores = []
            joins_dim = []
            for i, s in enumerate(servicios_sel):
                alias = f"d{i}"
                if i == 0: from_clause = f"{tablas_dim[s]} {alias}"
                else: joins_dim.append(f"INNER JOIN {tablas_dim[s]} {alias} ON d0.IdCliente = {alias}.IdCliente")
                
                selects_scores.append(f"(0.55 * (0.55 * {alias}.Relacional + 0.45 * {alias}.Cumplimiento) + 0.30 * {alias}.Economica + 0.15 * (1 - {alias}.Potencial)) AS score_{s.lower()}")

            score_cols = [f"score_{s.lower()}" for s in servicios_sel]
            score_final_expr = score_cols[0] if len(score_cols) == 1 else f"least({', '.join(score_cols)})"

            joins_vars = []
            selects_vars = []
            for s in servicios_sel:
                pref = s.lower()
                alias = f"v_{pref}"
                cols = _get_columns(tablas_var[s])
                joins_vars.append(f"LEFT JOIN {tablas_var[s]} {alias} ON b.IdCliente = {alias}.IdCliente")
                for c in cols: selects_vars.append(f"{alias}.`{c}` AS `{pref}_{c}`")

            select_vars_sql = ",\n                " + ",\n                ".join(selects_vars) if selects_vars else ""

            query = f"""
            WITH base AS (
                SELECT d0.IdCliente, d0.TipoIdentificacion, d0.Identificacion, {",".join(selects_scores)}
                FROM {from_clause} {" ".join(joins_dim)}
            ),
            scored AS (
                SELECT *, {score_final_expr} AS Score_CON FROM base
            )
            SELECT 
                b.IdCliente,
                b.TipoIdentificacion,
                b.Identificacion,
                b.Score_CON,
                c.Contratos, c.ContratosActivos
                {select_vars_sql}
            FROM scored b
            LEFT JOIN {tabla_contratos} c 
                ON b.IdCliente = c.IdCliente
            {" ".join(joins_vars)}
            ORDER BY b.Score_CON DESC LIMIT {top_n}
            """

            df_resultado = ejecutar_query_databricks(query)

        if df_resultado is not None and not df_resultado.empty:
            st.success(f"✅ Se han encontrado {len(df_resultado)} clientes valiosos.")
            
            # --- KPIs ---
            m1, m2, m3, m4 = st.columns(4)
            df_resultado['Score_CON'] = pd.to_numeric(df_resultado['Score_CON'], errors='coerce')
            m1.metric("Score Máximo", f"{df_resultado['Score_CON'].max():.2f}")
            m2.metric("Score Mínimo", f"{df_resultado["Score_CON"].min():.2f}")
            m3.metric("Score Promedio", f"{df_resultado['Score_CON'].mean():.2f}")
            
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
                label="📥 Descargar Listado (CSV)",
                data=df_resultado.to_csv(index=False).encode('utf-8'),
                file_name=f'consolidacion_{tipo_cliente}.csv',
                mime='text/csv',
                key="con_dl_btn"
            )

            if df_resultado is not None and not df_resultado.empty:
                if "rtr_fechas_proximas_rtr" in df_resultado.columns:
                    df_resultado["rtr_fechas_proximas_rtr"] = df_resultado["rtr_fechas_proximas_rtr"].apply(formatear_lista_fechas)

            # Estilo con gradiente naranja
            st.dataframe(
                df_resultado.style.background_gradient(subset=['Score_CON'], cmap='Oranges'),
                width='stretch',
                hide_index=True
            )

            for servicio in servicios_sel:
                render_descripcion_variables(servicio)
        else:
            st.warning("No se encontraron clientes que coincidan con los criterios de consolidación en los servicios seleccionados.")

