import pandas as pd
import streamlit as st

from features.decisiones_estrategicas.data import count_contract_items, load_service_options
from features.decisiones_estrategicas.models import (
    ConsolidarRequest,
    FidelizarRequest,
    PotenciarRequest,
    RecuperarRequest,
)


def load_styles() -> None:
    st.markdown(
        """
        <style>
        .de-title {
            font-size: 2.7rem;
            font-weight: 800;
            color: #0f172a;
            margin-bottom: 0.35rem;
        }
        .de-subtitle {
            font-size: 1.05rem;
            color: #64748b;
            margin-bottom: 1.4rem;
        }
        .de-hero {
            background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 100%);
            border: 1px solid #dbeafe;
            border-radius: 18px;
            padding: 1.25rem 1.35rem;
            margin-bottom: 1rem;
        }
        .de-card-title {
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: #64748b;
            margin-bottom: 0.25rem;
        }
        .de-card-value {
            font-size: 1.8rem;
            font-weight: 800;
            color: #0f172a;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    st.markdown(
        """
        <div class="de-hero">
            <div class="de-title">Decisiones estratégicas</div>
            <div class="de-subtitle">
                Acciones priorizadas para consolidar, recuperar, fidelizar y potenciar clientes
                con base en su perfil integral por servicio.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_consolidar_intro() -> None:
    tab_guia, tab_pasos, tab_orden = st.tabs(
        ["¿Para qué sirve?", "¿Cómo funciona?", "Interpretación"]
    )

    with tab_guia:
        st.info(
            "Identifica clientes estables, confiables y valiosos. La idea es proteger esa relación "
            "y priorizar acciones de consolidación donde el cliente ya muestra fortaleza."
        )
    with tab_pasos:
        col_1, col_2 = st.columns(2)
        with col_1:
            st.markdown("1. Selecciona la categoría.")
            st.markdown("2. Escoge los servicios donde quieres medir estabilidad.")
        with col_2:
            st.markdown("3. Define cuántos clientes quieres extraer.")
            st.markdown("4. Ejecuta el análisis y descarga el listado priorizado.")
    with tab_orden:
        st.caption(
            "El Score_CON pondera fidelidad relacional, valor económico recurrente y madurez, "
            "quedándose con el score más restrictivo cuando se evalúan varios servicios."
        )


def render_consolidar_form(current_request: ConsolidarRequest) -> ConsolidarRequest | None:
    with st.container(border=True):
        st.subheader("Consolidar")
        render_consolidar_intro()
        c1, c2, c3 = st.columns([1.2, 2.2, 1])

        with c1:
            categoria = st.selectbox(
                "Categoría",
                ["Residencial", "Comercial"],
                index=0 if current_request.categoria == "Residencial" else 1,
                key="decisiones_con_categoria",
            )

        service_options = load_service_options(categoria)
        default_services = [service for service in current_request.servicios if service in service_options]

        with c2:
            servicios = st.multiselect(
                "Servicios a evaluar",
                service_options,
                default=default_services,
                key="decisiones_con_servicios",
            )

        with c3:
            top_n = st.number_input(
                "Cantidad",
                min_value=1,
                max_value=10000,
                value=int(current_request.top_n),
                step=1,
                key="decisiones_con_top_n",
            )

        ejecutar = st.button("Identificar clientes a consolidar", type="primary", key="decisiones_con_btn")

    if not ejecutar:
        return None

    if not servicios:
        st.info("Selecciona al menos un servicio para ejecutar la estrategia de consolidación.")
        return None

    return ConsolidarRequest(
        categoria=categoria,
        servicios=tuple(servicios),
        top_n=int(top_n),
        searched=True,
    )


def _render_result_cards(df_resultado: pd.DataFrame) -> None:
    df_metrics = df_resultado.copy()
    df_metrics["Score_CON"] = pd.to_numeric(df_metrics["Score_CON"], errors="coerce")

    total_contracts = 0
    if "Contratos" in df_metrics.columns:
        total_contracts = int(df_metrics["Contratos"].apply(count_contract_items).sum())

    cards = st.columns(4)
    metrics = [
        ("Clientes priorizados", f"{len(df_metrics):,}".replace(",", ".")),
        ("Score máximo", f"{df_metrics['Score_CON'].max():.2f}"),
        ("Score promedio", f"{df_metrics['Score_CON'].mean():.2f}"),
        ("Total contratos", f"{total_contracts:,}".replace(",", ".")),
    ]
    for column, (title, value) in zip(cards, metrics):
        with column:
            st.markdown(
                f"""
                <div style="border:1px solid #e2e8f0;border-radius:16px;padding:1rem 1.1rem;background:white;">
                    <div class="de-card-title">{title}</div>
                    <div class="de-card-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_consolidar_results(df_resultado: pd.DataFrame, request: ConsolidarRequest) -> None:
    if df_resultado.empty:
        st.warning("No se encontraron clientes que cumplan los criterios seleccionados.")
        return

    st.success(f"Se encontraron {len(df_resultado)} clientes para la estrategia de consolidación.")
    _render_result_cards(df_resultado)

    csv_data = df_resultado.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Descargar listado (CSV)",
        data=csv_data,
        file_name=f"consolidacion_{request.categoria.lower()}.csv",
        mime="text/csv",
        key="decisiones_con_download",
    )

    st.dataframe(
        df_resultado.style.background_gradient(subset=["Score_CON"], cmap="Oranges"),
        use_container_width=True,
        hide_index=True,
    )


def render_recuperar_intro() -> None:
    tab_guia, tab_pasos, tab_orden = st.tabs(
        ["¿Para qué sirve?", "¿Cómo funciona?", "Interpretación"]
    )

    with tab_guia:
        st.info(
            "Identifica clientes con señales de deterioro en la relación con la empresa y los prioriza "
            "según su valor histórico y la viabilidad de una recuperación."
        )
    with tab_pasos:
        col_1, col_2 = st.columns(2)
        with col_1:
            st.markdown("1. Elige la categoría del cliente.")
            st.markdown("2. Selecciona el servicio en riesgo.")
        with col_2:
            st.markdown("3. Define cuántos clientes quieres priorizar.")
            st.markdown("4. Ejecuta el análisis para obtener el listado de recuperación.")
    with tab_orden:
        st.caption(
            "El Score_REC pondera deterioro, valor histórico y viabilidad, priorizando clientes "
            "que vale la pena recuperar antes de que la relación siga cayendo."
        )


def render_recuperar_form(current_request: RecuperarRequest) -> RecuperarRequest | None:
    with st.container(border=True):
        st.subheader("Recuperar")
        render_recuperar_intro()
        c1, c2, c3 = st.columns([1.2, 2.2, 1])

        with c1:
            categoria = st.selectbox(
                "Categoría",
                ["Residencial", "Comercial"],
                index=0 if current_request.categoria == "Residencial" else 1,
                key="decisiones_rec_categoria",
            )

        service_options = load_service_options(categoria)
        current_service = current_request.servicio if current_request.servicio in service_options else None
        service_index = service_options.index(current_service) if current_service in service_options else 0

        with c2:
            servicio = st.selectbox(
                "Servicio en riesgo",
                service_options,
                index=service_index if service_options else None,
                key="decisiones_rec_servicio",
            )

        with c3:
            top_n = st.number_input(
                "Cantidad",
                min_value=1,
                max_value=10000,
                value=int(current_request.top_n),
                step=1,
                key="decisiones_rec_top_n",
            )

        ejecutar = st.button("Identificar clientes a recuperar", type="primary", key="decisiones_rec_btn")

    if not ejecutar:
        return None

    return RecuperarRequest(
        categoria=categoria,
        servicio=str(servicio),
        top_n=int(top_n),
        searched=True,
    )


def render_recuperar_results(df_resultado: pd.DataFrame, request: RecuperarRequest) -> None:
    if df_resultado.empty:
        st.warning("No se encontraron clientes que cumplan los criterios seleccionados.")
        return

    st.success(f"Se encontraron {len(df_resultado)} clientes para la estrategia de recuperación.")

    df_metrics = df_resultado.copy()
    df_metrics["Score_REC"] = pd.to_numeric(df_metrics["Score_REC"], errors="coerce")
    total_contracts = 0
    if "Contratos" in df_metrics.columns:
        total_contracts = int(df_metrics["Contratos"].apply(count_contract_items).sum())

    cards = st.columns(4)
    metrics = [
        ("Clientes priorizados", f"{len(df_metrics):,}".replace(",", ".")),
        ("Score máximo", f"{df_metrics['Score_REC'].max():.2f}"),
        ("Score promedio", f"{df_metrics['Score_REC'].mean():.2f}"),
        ("Total contratos", f"{total_contracts:,}".replace(",", ".")),
    ]
    for column, (title, value) in zip(cards, metrics):
        with column:
            st.markdown(
                f"""
                <div style="border:1px solid #e2e8f0;border-radius:16px;padding:1rem 1.1rem;background:white;">
                    <div class="de-card-title">{title}</div>
                    <div class="de-card-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    csv_data = df_resultado.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Descargar plan de acción (CSV)",
        data=csv_data,
        file_name=f"recuperacion_{request.servicio.lower()}_{request.categoria.lower()}.csv",
        mime="text/csv",
        key="decisiones_rec_download",
    )

    st.dataframe(
        df_resultado.style.background_gradient(subset=["Score_REC"], cmap="Reds"),
        use_container_width=True,
        hide_index=True,
    )


def render_fidelizar_intro() -> None:
    tab_guia, tab_pasos, tab_orden = st.tabs(
        ["¿Para qué sirve?", "¿Cómo funciona?", "Interpretación"]
    )

    with tab_guia:
        st.info(
            "Identifica clientes que conviene fidelizar usando un servicio ancla fuerte y un servicio objetivo "
            "donde todavía existe una oportunidad clara de crecimiento."
        )
    with tab_pasos:
        col_1, col_2 = st.columns(2)
        with col_1:
            st.markdown("1. Elige la categoría del cliente.")
            st.markdown("2. Selecciona el servicio ancla.")
        with col_2:
            st.markdown("3. Escoge el servicio objetivo a potenciar.")
            st.markdown("4. Ejecuta el análisis para obtener el listado priorizado.")
    with tab_orden:
        st.caption(
            "El Score_FID combina la fortaleza del servicio ancla, la oportunidad del servicio objetivo "
            "y la estabilidad general del cliente."
        )


def render_fidelizar_form(current_request: FidelizarRequest) -> FidelizarRequest | None:
    with st.container(border=True):
        st.subheader("Fidelizar")
        render_fidelizar_intro()
        c1, c2, c3 = st.columns([1.2, 1.8, 1.8])

        with c1:
            categoria = st.selectbox(
                "Categoría",
                ["Residencial", "Comercial"],
                index=0 if current_request.categoria == "Residencial" else 1,
                key="decisiones_fid_categoria",
            )

        service_options = load_service_options(categoria)
        current_ancla = current_request.servicio_ancla if current_request.servicio_ancla in service_options else None
        current_ancla_index = service_options.index(current_ancla) if current_ancla in service_options else 0

        with c2:
            servicio_ancla = st.selectbox(
                "Servicio ancla",
                service_options,
                index=current_ancla_index if service_options else None,
                key="decisiones_fid_ancla",
            )

        objetivo_options = [service for service in service_options if service != servicio_ancla]
        current_objetivo = (
            current_request.servicio_objetivo if current_request.servicio_objetivo in objetivo_options else None
        )
        objetivo_index = objetivo_options.index(current_objetivo) if current_objetivo in objetivo_options else 0

        with c3:
            servicio_objetivo = st.selectbox(
                "Servicio objetivo",
                objetivo_options,
                index=objetivo_index if objetivo_options else None,
                key="decisiones_fid_objetivo",
            )

        c4, _ = st.columns([1.2, 2.8])
        with c4:
            top_n = st.number_input(
                "Cantidad",
                min_value=1,
                max_value=10000,
                value=int(current_request.top_n),
                step=1,
                key="decisiones_fid_top_n",
            )

        ejecutar = st.button("Identificar clientes a fidelizar", type="primary", key="decisiones_fid_btn")

    if not ejecutar:
        return None

    return FidelizarRequest(
        categoria=categoria,
        servicio_ancla=str(servicio_ancla),
        servicio_objetivo=str(servicio_objetivo),
        top_n=int(top_n),
        searched=True,
    )


def render_fidelizar_results(df_resultado: pd.DataFrame, request: FidelizarRequest) -> None:
    if df_resultado.empty:
        st.warning("No se encontraron clientes que cumplan los criterios seleccionados.")
        return

    st.success(f"Se encontraron {len(df_resultado)} clientes para la estrategia de fidelización.")

    df_metrics = df_resultado.copy()
    df_metrics["Score_FID"] = pd.to_numeric(df_metrics["Score_FID"], errors="coerce")
    total_contracts = 0
    if "Contratos" in df_metrics.columns:
        total_contracts = int(df_metrics["Contratos"].apply(count_contract_items).sum())

    cards = st.columns(4)
    metrics = [
        ("Clientes priorizados", f"{len(df_metrics):,}".replace(",", ".")),
        ("Score máximo", f"{df_metrics['Score_FID'].max():.2f}"),
        ("Score promedio", f"{df_metrics['Score_FID'].mean():.2f}"),
        ("Total contratos", f"{total_contracts:,}".replace(",", ".")),
    ]
    for column, (title, value) in zip(cards, metrics):
        with column:
            st.markdown(
                f"""
                <div style="border:1px solid #e2e8f0;border-radius:16px;padding:1rem 1.1rem;background:white;">
                    <div class="de-card-title">{title}</div>
                    <div class="de-card-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    csv_data = df_resultado.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Descargar listado (CSV)",
        data=csv_data,
        file_name=f"fidelizacion_{request.categoria.lower()}.csv",
        mime="text/csv",
        key="decisiones_fid_download",
    )

    st.dataframe(
        df_resultado.style.background_gradient(subset=["Score_FID"], cmap="Blues"),
        use_container_width=True,
        hide_index=True,
    )


def render_potenciar_intro() -> None:
    tab_guia, tab_pasos, tab_orden = st.tabs(
        ["¿Para qué sirve?", "¿Cómo funciona?", "Interpretación"]
    )

    with tab_guia:
        st.info(
            "Identifica clientes con alto potencial de crecimiento en uno o varios servicios para enfocar "
            "acciones comerciales donde la probabilidad de expansión es mayor."
        )
    with tab_pasos:
        col_1, col_2 = st.columns(2)
        with col_1:
            st.markdown("1. Selecciona la categoría del cliente.")
            st.markdown("2. Escoge los servicios objetivo a potenciar.")
        with col_2:
            st.markdown("3. Define cuántos clientes quieres priorizar.")
            st.markdown("4. Ejecuta el análisis para obtener el listado comercial.")
    with tab_orden:
        st.caption(
            "El Score_POT refleja el potencial de crecimiento promedio entre los servicios elegidos, "
            "ponderando potencial, valor económico, relación y cumplimiento."
        )


def render_potenciar_form(current_request: PotenciarRequest) -> PotenciarRequest | None:
    with st.container(border=True):
        st.subheader("Potenciar")
        render_potenciar_intro()
        c1, c2, c3 = st.columns([1.2, 2.2, 1])

        with c1:
            categoria = st.selectbox(
                "Categoría",
                ["Residencial", "Comercial"],
                index=0 if current_request.categoria == "Residencial" else 1,
                key="decisiones_pot_categoria",
            )

        service_options = load_service_options(categoria)
        default_services = [service for service in current_request.servicios if service in service_options]

        with c2:
            servicios = st.multiselect(
                "Servicios objetivo",
                service_options,
                default=default_services,
                key="decisiones_pot_servicios",
            )

        with c3:
            top_n = st.number_input(
                "Cantidad",
                min_value=1,
                max_value=10000,
                value=int(current_request.top_n),
                step=1,
                key="decisiones_pot_top_n",
            )

        ejecutar = st.button("Identificar clientes a potenciar", type="primary", key="decisiones_pot_btn")

    if not ejecutar:
        return None

    if not servicios:
        st.info("Selecciona al menos un servicio para ejecutar la estrategia de potenciación.")
        return None

    return PotenciarRequest(
        categoria=categoria,
        servicios=tuple(servicios),
        top_n=int(top_n),
        searched=True,
    )


def render_potenciar_results(df_resultado: pd.DataFrame, request: PotenciarRequest) -> None:
    if df_resultado.empty:
        st.warning("No se encontraron clientes que cumplan los criterios seleccionados.")
        return

    st.success(f"Se encontraron {len(df_resultado)} clientes para la estrategia de potenciación.")

    df_metrics = df_resultado.copy()
    df_metrics["Score_POT"] = pd.to_numeric(df_metrics["Score_POT"], errors="coerce")
    total_contracts = 0
    if "Contratos" in df_metrics.columns:
        total_contracts = int(df_metrics["Contratos"].apply(count_contract_items).sum())

    cards = st.columns(4)
    metrics = [
        ("Clientes priorizados", f"{len(df_metrics):,}".replace(",", ".")),
        ("Score máximo", f"{df_metrics['Score_POT'].max():.2f}"),
        ("Score promedio", f"{df_metrics['Score_POT'].mean():.2f}"),
        ("Total contratos", f"{total_contracts:,}".replace(",", ".")),
    ]
    for column, (title, value) in zip(cards, metrics):
        with column:
            st.markdown(
                f"""
                <div style="border:1px solid #e2e8f0;border-radius:16px;padding:1rem 1.1rem;background:white;">
                    <div class="de-card-title">{title}</div>
                    <div class="de-card-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    csv_data = df_resultado.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Descargar resultados (CSV)",
        data=csv_data,
        file_name=f"potenciacion_{request.categoria.lower()}.csv",
        mime="text/csv",
        key="decisiones_pot_download",
    )

    st.dataframe(
        df_resultado.style.background_gradient(subset=["Score_POT"], cmap="YlGn"),
        use_container_width=True,
        hide_index=True,
    )


def render_placeholder_strategy(title: str, description: str) -> None:
    with st.container(border=True):
        st.subheader(title)
        st.info(description)
