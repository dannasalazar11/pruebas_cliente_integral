import streamlit as st
import pandas as pd
import numpy as np
from utils.db import ejecutar_query_databricks
from services.variables_por_servicio import formatear_lista_fechas
from services.descripcion_variables import render_descripcion_variables


def potenciar():
    # --- ESTILOS CSS ÚNICOS (USANDO CLASES ESPECÍFICAS '-pot') ---
    st.markdown("""
        <style>
        /* 1. Título y cajas con nombres únicos para no chocar con Fidelizar */
        .title-text-pot { 
            font-size: 2.2rem; font-weight: 800; color: #064E3B !important; margin-bottom: 0.5rem; 
        }
        .info-box-pot { 
            background-color: #ECFDF5; 
            padding: 20px; 
            border-left: 5px solid #10B981; 
            border-radius: 5px;
            margin-bottom: 20px;
            color: #065F46;
        }
        .step-num-pot {
            background-color: #10B981;
            color: white;
            border-radius: 50%;
            padding: 2px 8px;
            font-weight: bold;
            margin-right: 5px;
        }

        /* 2. SELECTOR DE BOTÓN ULTRA-ESPECÍFICO */
        /* Solo aplica a botones cuyo texto contiene 'Potenciación' */
        div.stButton > button:has(p:contains("Potenciación")) {
            background-color: #10B981 !important;
            color: white !important;
            border-radius: 20px !important;
            height: 3em !important;
            font-weight: bold !important;
            border: none !important;
            width: 100%;
        }
        
        div.stButton > button:has(p:contains("Potenciación")):hover {
            background-color: #059669 !important;
            border: none !important;
        }

        /* 3. Evitar que el header por defecto de streamlit se pinte verde si no queremos */
        .st-emotion-cache-10trblm { color: inherit; } 
        </style>
    """, unsafe_allow_html=True)

# --- ESTILOS CSS ÚNICOS ---
    st.markdown("""
        <style>
        .title-pot { 
            font-size: 3.5rem !important; /* Aumentado de 2.2 a 3.5 */
            font-weight: 900 !important; 
            color: #064E3B !important; 
            margin-bottom: 0px !important;
            line-height: 1.1 !important;
        }
        .subtitle-pot {
            font-size: 1.2rem;
            color: #64748b;
            margin-bottom: 2rem;
        }
        /* ... el resto de tu CSS (info-box-pot, etc.) ... */
        </style>
    """, unsafe_allow_html=True)

    # --- ENCABEZADO ---
    st.markdown('<p class="title-pot">Estrategia de Potenciación</p>', unsafe_allow_html=True)

    # --- SECCIÓN DE AYUDA (Tabs) ---
    tab_guia, tab_pasos, tab_orden = st.tabs([
        "💡 ¿Para qué sirve?", 
        "🛠️ ¿Cómo funciona?", 
        "📊 Interpretación"
    ])

    with tab_guia:
        st.markdown("""
        <div class="info-box-pot">
            Esta funcionalidad identifica clientes con <b>alta capacidad de crecimiento</b>. 
            Permite enfocar esfuerzos comerciales en clientes que ya tienen una relación y presentan el mayor 
            <b>potencial de crecimiento</b>.
        </div>
        """, unsafe_allow_html=True)

    with tab_pasos:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("<span class='step-num-pot'>1</span> Define la <b>categoría</b> del cliente.", unsafe_allow_html=True)
            st.markdown("<span class='step-num-pot'>2</span> Selecciona los <b>servicios</b> a potenciar.", unsafe_allow_html=True)
        with col_b:
            st.markdown("<span class='step-num-pot'>3</span> Elige la <b>cantidad</b> de clientes quieres determinar.", unsafe_allow_html=True)
            st.markdown("<span class='step-num-pot'>4</span> Ejecuta para obtener el <b>listado prioritario</b> de clientes a potenciar.", unsafe_allow_html=True)

    with tab_orden:
        st.info("El **Score_POT** refleja la probabilidad de éxito de una acción comercial basada en el potencial acumulado.")

    st.divider()

    # =========================
    # 1. SELECCIÓN DE PARÁMETROS
    # =========================
    with st.container():
        st.subheader("⚙️ Configuración del Análisis")
        c1, c2, c3 = st.columns([1, 2, 1])

        with c1:
            tipo_cliente = st.selectbox("👤 Tipo de cliente", ["Residencial", "Comercial"], key="pot_tipo_cli")
        
        servicios_posibles = ["Consumo", "RTR", "SAD"] if tipo_cliente == "Residencial" else ["Consumo", "RTR", "Efisoluciones"]

        with c2:
            servicios_sel = st.multiselect("🎯 Servicios objetivo", servicios_posibles, key="pot_serv_sel")

        with c3:
            top_n = st.number_input("🔝 Cantidad", min_value=1, max_value=10000, value=100, step=1, key="pot_top_n")

    if not servicios_sel:
        st.info("Por favor, selecciona al menos un servicio.")
        return

    st.markdown("<br>", unsafe_allow_html=True)

    # =========================
    # 2. BOTÓN ÚNICO
    # =========================
    # El nombre del botón DEBE contener la palabra "Potenciación" para que el CSS funcione
    ejecutar = st.button("🔍 Identificar Clientes")

    if ejecutar:
        with st.spinner("Analizando potencial de crecimiento..."):
            tipo_cliente_sql = tipo_cliente.lower()

            # --- Construcción dinámica (Lógica de Databricks) ---
            tablas_dim = [f"analiticaefg.clienteintegral.{s.lower()}_{tipo_cliente_sql}_consolidado_dimensiones" for s in servicios_sel]
            tablas_var = {s: f"analiticaefg.clienteintegral.{s.lower()}_{tipo_cliente_sql}_consolidado_variables" for s in servicios_sel}
            tabla_contratos = f"analiticaefg.clienteintegral.modelo_contratos{tipo_cliente_sql}"

            def _get_columns(full_name):
                parts = full_name.split(".")
                q = f"SELECT column_name FROM system.information_schema.columns WHERE table_catalog='{parts[0]}' AND table_schema='{parts[1]}' AND table_name='{parts[2]}'"
                df_cols = ejecutar_query_databricks(q)
                if df_cols is not None and not df_cols.empty:
                    cols = df_cols["column_name"].tolist()
                    return [c for c in cols if c.lower() not in ("idcliente", "tipoidentificacion", "identificacion")]
                return []

            selects_score = []
            joins_dim = []
            for i, s in enumerate(servicios_sel):
                alias = f"t{i}"
                if i > 0:
                    joins_dim.append(f"INNER JOIN {tablas_dim[i]} {alias} ON t0.IdCliente = {alias}.IdCliente")
                selects_score.append(f"(0.45 * {alias}.Potencial + 0.30 * {alias}.Economica + 0.15 * {alias}.Relacional + 0.10 * {alias}.Cumplimiento) AS score_{s.lower()}")

            score_avg_formula = " + ".join([f"score_{s.lower()}" for s in servicios_sel])

            selects_vars = []
            joins_vars = []
            for s in servicios_sel:
                pref = s.lower()
                alias = f"v_{pref}"
                cols = _get_columns(tablas_var[s])
                joins_vars.append(f"LEFT JOIN {tablas_var[s]} {alias} ON b.IdCliente = {alias}.IdCliente")
                for c in cols:
                    selects_vars.append(f"{alias}.`{c}` AS `{pref}_{c}`")

            query = f"""
            WITH base AS (
                SELECT t0.IdCliente, t0.TipoIdentificacion, t0.Identificacion, {",".join(selects_score)}
                FROM {tablas_dim[0]} t0 {" ".join(joins_dim)}
            ),
            scored AS (
                SELECT *, ({score_avg_formula}) / {len(servicios_sel)} AS Score_POT
                FROM base
            )
            SELECT b.IdCliente, b.TipoIdentificacion, b.Identificacion, b.Score_POT, c.Contratos, c.ContratosActivos, {",".join(selects_vars)}
            FROM scored b
            LEFT JOIN {tabla_contratos} c ON b.IdCliente = c.IdCliente
            {" ".join(joins_vars)}
            ORDER BY b.Score_POT DESC LIMIT {top_n}
            """

            df = ejecutar_query_databricks(query)

        # =========================
        # 3. RESULTADOS
        # =========================
        if df is not None and not df.empty:
            st.success(f"✅ Se han identificado {len(df)} clientes con alto potencial.")

            # Métricas
            m1, m2, m3, m4 = st.columns(4)
            df['Score_POT'] = pd.to_numeric(df['Score_POT'], errors='coerce')
            m1.metric("Score Máximo", f"{df['Score_POT'].max():.2f}")
            m2.metric("Score Mínimo", f"{df['Score_POT'].min():.2f}")
            m3.metric("Score Promedio", f"{df['Score_POT'].mean():.2f}")
            
            # Conteo de contratos robusto
            def count_contracts(x):
                if isinstance(x, (list, np.ndarray)): return len(x)
                if isinstance(x, str): return len(x.split(','))
                return 1 if pd.notnull(x) and str(x).strip() != "" else 0

            total_c = df['Contratos'].apply(count_contracts).sum() if 'Contratos' in df.columns else 0
            m4.metric("Total Contratos", int(total_c))

            st.download_button(
                "📥 Descargar Resultados (CSV)",
                df.to_csv(index=False).encode('utf-8'),
                f"potenciacion_{tipo_cliente}.csv",
                "text/csv",
                key="dl_btn_pot"
            )

            if df is not None and not df.empty:
                if "rtr_fechas_proximas_rtr" in df.columns:
                    df["rtr_fechas_proximas_rtr"] = df["rtr_fechas_proximas_rtr"].apply(formatear_lista_fechas)
            

            # Tabla estilizada (Verde)
            st.dataframe(
                df.style.background_gradient(subset=['Score_POT'], cmap='YlGn'),
                width='stretch',
                hide_index=True
            )

            for servicio in servicios_sel:
                render_descripcion_variables(servicio)
        else:
            st.warning("No se encontraron resultados para los parámetros seleccionados.")
