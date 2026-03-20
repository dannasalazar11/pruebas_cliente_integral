import pandas as pd
import streamlit as st

from features.buscador_clientes.models import CustomerProfile, CustomerSearchRequest


UNIVERSOS = ("Residencial", "Comercial")
SERVICE_ICONS = {
    "Consumo": "🔥",
    "RTR": "🔁",
    "SAD": "🛠️",
    "Seguros": "🛡️",
    "Brilla": "💳",
    "Efisoluciones": "⚙️",
}


def load_styles() -> None:
    st.markdown(
        """
        <style>
        .search-page-title {
            font-size: 1.9rem;
            font-weight: 700;
            color: #153e75;
            margin-bottom: 0.2rem;
        }
        .search-page-copy {
            font-size: 1rem;
            color: #526173;
            margin-bottom: 1.2rem;
        }
        .search-shell {
            border: 1px solid #d8e7f5;
            border-radius: 24px;
            padding: 20px 22px 8px 22px;
            background:
                radial-gradient(circle at top right, rgba(11, 116, 200, 0.08), transparent 30%),
                linear-gradient(180deg, #ffffff 0%, #f7fbff 100%);
            margin-bottom: 1rem;
        }
        .search-summary-card {
            border: 1px solid #e7edf3;
            border-radius: 18px;
            padding: 18px 20px;
            background: linear-gradient(180deg, #ffffff 0%, #f8fbfe 100%);
            margin-bottom: 1rem;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
        }
        .search-panel {
            border: 1px solid #e7edf3;
            border-radius: 22px;
            padding: 18px 18px 10px 18px;
            background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%);
            box-shadow: 0 10px 28px rgba(15, 23, 42, 0.04);
            margin-bottom: 1rem;
            min-height: 100%;
        }
        .search-panel-title {
            font-size: 1.02rem;
            font-weight: 700;
            color: #23354d;
            margin-bottom: 0.15rem;
        }
        .search-panel-copy {
            font-size: 0.92rem;
            color: #6b7280;
            margin-bottom: 0.85rem;
        }
        .search-summary-label {
            font-size: 0.82rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: #7a869a;
            margin-bottom: 0.2rem;
        }
        .search-summary-value {
            font-size: 1.08rem;
            font-weight: 600;
            color: #1f2937;
        }
        .contract-meta {
            color: #5e6e82;
            font-size: 0.95rem;
        }
        .service-chip {
            display: inline-block;
            padding: 0.3rem 0.7rem;
            margin: 0 0.45rem 0.45rem 0;
            border-radius: 999px;
            background: #eaf4ff;
            color: #0b5fa5;
            font-weight: 600;
            font-size: 0.9rem;
            border: 1px solid #c9def3;
        }
        .service-chip-icon {
            margin-right: 0.3rem;
        }
        .service-chip-wrap {
            margin-top: 0.35rem;
        }
        .service-highlight {
            border: 1px solid #d7e7f7;
            border-radius: 18px;
            padding: 16px 18px;
            background: radial-gradient(circle at top right, rgba(11, 116, 200, 0.08), transparent 35%), #ffffff;
            margin-bottom: 0.9rem;
        }
        .service-highlight-value {
            font-size: 2rem;
            font-weight: 700;
            color: #0f172a;
            line-height: 1;
            margin-bottom: 0.25rem;
        }
        .service-highlight-copy {
            color: #64748b;
            font-size: 0.92rem;
        }
        .dimension-score-card {
            border: 1px solid #e5ecf3;
            border-radius: 18px;
            padding: 16px 18px;
            background: #ffffff;
            box-shadow: 0 4px 18px rgba(15, 23, 42, 0.04);
            margin-bottom: 0.8rem;
        }
        .dimension-score-title {
            font-size: 0.84rem;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.35rem;
        }
        .dimension-score-value {
            font-size: 1.35rem;
            font-weight: 700;
            color: #1f2937;
        }
        .metric-card {
            border: 1px solid #e6edf5;
            border-radius: 18px;
            padding: 15px 16px;
            background: #ffffff;
            box-shadow: 0 5px 14px rgba(15, 23, 42, 0.03);
            margin-bottom: 0.9rem;
            min-height: 132px;
        }
        .metric-label {
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #6b7280;
            margin-bottom: 0.45rem;
        }
        .metric-value {
            font-size: 1.18rem;
            font-weight: 700;
            color: #17212f;
            margin-bottom: 0.65rem;
            word-break: break-word;
        }
        .metric-subtle {
            font-size: 0.85rem;
            color: #7b8796;
        }
        .metric-track {
            width: 100%;
            height: 7px;
            border-radius: 999px;
            background: #edf2f7;
            overflow: hidden;
        }
        .metric-fill {
            height: 100%;
            border-radius: 999px;
            background: linear-gradient(90deg, #7aa7ff 0%, #2f6fed 100%);
        }
        .section-heading {
            font-size: 1.08rem;
            font-weight: 700;
            color: #20324b;
            margin: 0 0 0.85rem 0;
        }
        button[role="tab"] {
            border-radius: 12px !important;
            border: 1px solid #dbe6f1 !important;
            padding: 0.45rem 0.9rem !important;
            color: #4b5d73 !important;
            background: #f8fbfe !important;
        }
        button[role="tab"][aria-selected="true"] {
            background: #eaf4ff !important;
            color: #0b5fa5 !important;
            border-color: #b6d3f3 !important;
            font-weight: 700 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    st.markdown(
        """
        <div class="search-shell">
            <div class="search-page-title">Buscador de clientes</div>
            <div class="search-page-copy">Consulta un cliente puntual, su perfil integral, sus contratos y el detalle de cada servicio activo.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_search_form(
    tipo_identificacion_options: list[str],
    current_request: CustomerSearchRequest,
) -> CustomerSearchRequest | None:
    default_universo_index = UNIVERSOS.index(current_request.universo) if current_request.universo in UNIVERSOS else 0
    selected_tipo = (
        current_request.tipo_identificacion
        if current_request.tipo_identificacion in tipo_identificacion_options
        else (tipo_identificacion_options[0] if tipo_identificacion_options else "")
    )
    default_tipo_index = tipo_identificacion_options.index(selected_tipo) if selected_tipo in tipo_identificacion_options else 0

    with st.form("customer_search_form"):
        col1, col2, col3, col4 = st.columns([1, 1, 1.2, 0.7], gap="medium")

        with col1:
            universo = st.selectbox("Universo", UNIVERSOS, index=default_universo_index)
        with col2:
            tipo_identificacion = st.selectbox(
                "Tipo de identificación",
                tipo_identificacion_options,
                index=default_tipo_index if tipo_identificacion_options else None,
                placeholder="Selecciona un tipo",
            )
        with col3:
            identificacion = st.text_input("Número de identificación", value=current_request.identificacion)
        with col4:
            st.markdown("<div style='height: 1.7rem;'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Buscar", width="stretch")

    if not submitted:
        return None

    return CustomerSearchRequest(
        universo=universo,
        tipo_identificacion=(tipo_identificacion or "").strip(),
        identificacion=identificacion.strip(),
        searched=True,
    )


def render_customer_profile(profile: CustomerProfile) -> None:
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    values = [
        ("Nombre", profile.nombre),
        ("Apellido", profile.apellido),
        ("Tipo de identificación", profile.tipo_identificacion),
        ("Identificación", profile.identificacion),
    ]

    for col, (label, value) in zip((col1, col2, col3, col4), values):
        with col:
            st.markdown(
                f"""
                <div class="search-summary-card">
                    <div class="search-summary-label">{label}</div>
                    <div class="search-summary-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _render_panel_header(title: str, copy: str) -> None:
    st.markdown(
        f"""
        <div class="search-panel-title">{title}</div>
        <div class="search-panel-copy">{copy}</div>
        """,
        unsafe_allow_html=True,
    )


def render_contracts_section(df_contracts: pd.DataFrame) -> None:
    st.markdown("### Contratos")

    if df_contracts.empty:
        st.info("El cliente existe, pero no tiene contratos válidos para la categoría seleccionada.")
        return

    for _, row in df_contracts.iterrows():
        contrato = row.get("Contrato", "Sin contrato")
        estado = row.get("Estado", "Sin estado")
        with st.expander(f"Contrato {contrato} | Estado: {estado}", expanded=False):
            col1, col2 = st.columns(2, gap="large")

            with col1:
                st.markdown(f"**Contrato:** {contrato}")
                st.markdown(f"**Estado:** {estado}")
                st.markdown(f"**Categoría:** {row.get('Categoria', 'No disponible')}")
                st.markdown(f"**Subcategoría:** {row.get('Subcategoria', 'No disponible')}")
                st.markdown(f"**Dirección:** {row.get('Direccion', 'No disponible')}")

            with col2:
                st.markdown(f"**Barrio:** {row.get('Barrio', 'No disponible')}")
                st.markdown(f"**Localidad:** {row.get('Localidad', 'No disponible')}")
                st.markdown(f"**Departamento:** {row.get('Departamento', 'No disponible')}")
                st.markdown(f"**Mercado:** {row.get('Mercado', 'No disponible')}")


def _normalize_metric_value(value: object) -> object:
    if isinstance(value, pd.Series):
        cleaned = [item for item in value.tolist() if not pd.isna(item)]
        if not cleaned:
            return None
        if len(cleaned) == 1:
            return cleaned[0]
        return " | ".join(str(item) for item in cleaned)

    if hasattr(value, "tolist") and not isinstance(value, (str, bytes)):
        try:
            as_list = value.tolist()
        except Exception:
            as_list = value
        if isinstance(as_list, list):
            flattened = []
            for item in as_list:
                if isinstance(item, list):
                    flattened.extend(item)
                else:
                    flattened.append(item)
            cleaned = [item for item in flattened if not pd.isna(item)]
            if not cleaned:
                return None
            if len(cleaned) == 1:
                return cleaned[0]
            return " | ".join(str(item) for item in cleaned)

    return value


def _format_metric_value(value: object) -> str:
    normalized = _normalize_metric_value(value)
    if normalized is None:
        return "No disponible"

    try:
        is_missing = pd.isna(normalized)
    except (TypeError, ValueError):
        is_missing = False

    if isinstance(is_missing, (list, tuple)):
        is_missing = all(is_missing)
    elif hasattr(is_missing, "all") and not isinstance(is_missing, bool):
        try:
            is_missing = bool(is_missing.all())
        except Exception:
            is_missing = False

    if is_missing:
        return "No disponible"

    if isinstance(normalized, (int, float)) and not isinstance(normalized, bool):
        return f"{normalized:.2f}"

    return str(normalized)


def _score_progress_html(value: object) -> str:
    normalized = _normalize_metric_value(value)
    try:
        numeric = float(normalized)
    except (TypeError, ValueError):
        return ""

    if numeric < 0 or numeric > 1:
        return ""

    width = max(0.0, min(100.0, numeric * 100.0))
    return f'<div class="metric-track"><div class="metric-fill" style="width:{width:.1f}%"></div></div>'


def _render_metric_card(label: str, value: object) -> None:
    html = (
        f'<div class="metric-card">'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-value">{_format_metric_value(value)}</div>'
        f'{_score_progress_html(value)}'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def _normalize_metric_value(value: object) -> object:
    if isinstance(value, pd.Series):
        cleaned = [item for item in value.tolist() if not pd.isna(item)]
        if not cleaned:
            return None
        if len(cleaned) == 1:
            return cleaned[0]
        return " | ".join(str(item) for item in cleaned)

    if hasattr(value, "tolist") and not isinstance(value, (str, bytes)):
        try:
            as_list = value.tolist()
        except Exception:
            as_list = value
        if isinstance(as_list, list):
            flattened = []
            for item in as_list:
                if isinstance(item, list):
                    flattened.extend(item)
                else:
                    flattened.append(item)
            cleaned = [item for item in flattened if not pd.isna(item)]
            if not cleaned:
                return None
            if len(cleaned) == 1:
                return cleaned[0]
            return " | ".join(str(item) for item in cleaned)

    return value


def _format_metric_value(value: object) -> str:
    normalized = _normalize_metric_value(value)
    if normalized is None:
        return "No disponible"

    try:
        is_missing = pd.isna(normalized)
    except (TypeError, ValueError):
        is_missing = False

    if isinstance(is_missing, (list, tuple)):
        is_missing = all(is_missing)
    elif hasattr(is_missing, "all") and not isinstance(is_missing, bool):
        try:
            is_missing = bool(is_missing.all())
        except Exception:
            is_missing = False

    if is_missing:
        return "No disponible"

    if isinstance(normalized, (int, float)) and not isinstance(normalized, bool):
        return f"{normalized:.2f}"

    return str(normalized)


def _score_progress_html(value: object) -> str:
    normalized = _normalize_metric_value(value)
    try:
        numeric = float(normalized)
    except (TypeError, ValueError):
        return ""

    if numeric < 0 or numeric > 1:
        return ""

    width = max(0.0, min(100.0, numeric * 100.0))
    return f'<div class="metric-track"><div class="metric-fill" style="width:{width:.1f}%"></div></div>'


def _render_metric_card(label: str, value: object) -> None:
    html = (
        f'<div class="metric-card">'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-value">{_format_metric_value(value)}</div>'
        f'{_score_progress_html(value)}'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def _normalize_metric_value(value: object) -> object:
    if isinstance(value, pd.Series):
        cleaned = [item for item in value.tolist() if not pd.isna(item)]
        if not cleaned:
            return None
        if len(cleaned) == 1:
            return cleaned[0]
        return " | ".join(str(item) for item in cleaned)

    if hasattr(value, "tolist") and not isinstance(value, (str, bytes)):
        try:
            as_list = value.tolist()
        except Exception:
            as_list = value
        if isinstance(as_list, list):
            flattened = []
            for item in as_list:
                if isinstance(item, list):
                    flattened.extend(item)
                else:
                    flattened.append(item)
            cleaned = [item for item in flattened if not pd.isna(item)]
            if not cleaned:
                return None
            if len(cleaned) == 1:
                return cleaned[0]
            return " | ".join(str(item) for item in cleaned)

    return value


def _format_metric_value(value: object) -> str:
    normalized = _normalize_metric_value(value)
    if normalized is None:
        return "No disponible"

    try:
        is_missing = pd.isna(normalized)
    except (TypeError, ValueError):
        is_missing = False

    if isinstance(is_missing, (list, tuple)):
        is_missing = all(is_missing)
    elif hasattr(is_missing, "all") and not isinstance(is_missing, bool):
        try:
            is_missing = bool(is_missing.all())
        except Exception:
            is_missing = False

    if is_missing:
        return "No disponible"

    if isinstance(normalized, (int, float)) and not isinstance(normalized, bool):
        return f"{normalized:.2f}"

    return str(normalized)


def _score_progress_html(value: object) -> str:
    normalized = _normalize_metric_value(value)
    try:
        numeric = float(normalized)
    except (TypeError, ValueError):
        return ""

    if numeric < 0 or numeric > 1:
        return ""

    width = max(0.0, min(100.0, numeric * 100.0))
    return f'<div class="metric-track"><div class="metric-fill" style="width:{width:.1f}%"></div></div>'


def _render_metric_card(label: str, value: object) -> None:
    html = (
        f'<div class="metric-card">'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-value">{_format_metric_value(value)}</div>'
        f'{_score_progress_html(value)}'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def _normalize_metric_value(value: object) -> object:
    if isinstance(value, pd.Series):
        cleaned = [item for item in value.tolist() if not pd.isna(item)]
        if not cleaned:
            return None
        if len(cleaned) == 1:
            return cleaned[0]
        return " | ".join(str(item) for item in cleaned)

    if hasattr(value, "tolist") and not isinstance(value, (str, bytes)):
        try:
            as_list = value.tolist()
        except Exception:
            as_list = value
        if isinstance(as_list, list):
            flattened = []
            for item in as_list:
                if isinstance(item, list):
                    flattened.extend(item)
                else:
                    flattened.append(item)
            cleaned = [item for item in flattened if not pd.isna(item)]
            if not cleaned:
                return None
            if len(cleaned) == 1:
                return cleaned[0]
            return " | ".join(str(item) for item in cleaned)

    return value


def _format_metric_value(value: object) -> str:
    normalized = _normalize_metric_value(value)
    if normalized is None:
        return "No disponible"
    try:
        if pd.isna(normalized):
            return "No disponible"
    except (TypeError, ValueError):
        pass
    if isinstance(normalized, (int, float)) and not isinstance(normalized, bool):
        return f"{normalized:.2f}"
    return str(normalized)


def _normalize_metric_value(value: object) -> object:
    if isinstance(value, pd.Series):
        cleaned = [item for item in value.tolist() if not pd.isna(item)]
        if not cleaned:
            return None
        if len(cleaned) == 1:
            return cleaned[0]
        return " | ".join(str(item) for item in cleaned)

    if hasattr(value, "tolist") and not isinstance(value, (str, bytes)):
        try:
            as_list = value.tolist()
        except Exception:
            as_list = value
        if isinstance(as_list, list):
            flattened = []
            for item in as_list:
                if isinstance(item, list):
                    flattened.extend(item)
                else:
                    flattened.append(item)
            cleaned = [item for item in flattened if not pd.isna(item)]
            if not cleaned:
                return None
            if len(cleaned) == 1:
                return cleaned[0]
            return " | ".join(str(item) for item in cleaned)

    return value


def _format_metric_value(value: object) -> str:
    normalized = _normalize_metric_value(value)
    if normalized is None:
        return "No disponible"
    try:
        if pd.isna(normalized):
            return "No disponible"
    except (TypeError, ValueError):
        pass
    if isinstance(normalized, (int, float)) and not isinstance(normalized, bool):
        return f"{normalized:.2f}"
    return str(normalized)


def _score_progress_html(value: object) -> str:
    normalized = _normalize_metric_value(value)
    try:
        numeric = float(normalized)
    except (TypeError, ValueError):
        return ""

    if numeric < 0 or numeric > 1:
        return ""

    width = max(0.0, min(100.0, numeric * 100.0))
    return f'<div class="metric-track"><div class="metric-fill" style="width:{width:.1f}%"></div></div>'


def _render_metric_card(label: str, value: object) -> None:
    html = (
        f'<div class="metric-card">'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-value">{_format_metric_value(value)}</div>'
        f'{_score_progress_html(value)}'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def _normalize_metric_value(value: object) -> object:
    if isinstance(value, pd.Series):
        cleaned = [item for item in value.tolist() if not pd.isna(item)]
        if not cleaned:
            return None
        if len(cleaned) == 1:
            return cleaned[0]
        return " | ".join(str(item) for item in cleaned)

    if hasattr(value, "tolist") and not isinstance(value, (str, bytes)):
        try:
            as_list = value.tolist()
        except Exception:
            as_list = value
        if isinstance(as_list, list):
            flattened = []
            for item in as_list:
                if isinstance(item, list):
                    flattened.extend(item)
                else:
                    flattened.append(item)
            cleaned = [item for item in flattened if not pd.isna(item)]
            if not cleaned:
                return None
            if len(cleaned) == 1:
                return cleaned[0]
            return " | ".join(str(item) for item in cleaned)

    return value


def _format_metric_value(value: object) -> str:
    normalized = _normalize_metric_value(value)
    if normalized is None:
        return "No disponible"
    try:
        if pd.isna(normalized):
            return "No disponible"
    except (TypeError, ValueError):
        pass
    if isinstance(normalized, (int, float)) and not isinstance(normalized, bool):
        return f"{normalized:.2f}"
    return str(normalized)


def _normalize_metric_value(value: object) -> object:
    if isinstance(value, pd.Series):
        cleaned = [item for item in value.tolist() if not pd.isna(item)]
        if not cleaned:
            return None
        if len(cleaned) == 1:
            return cleaned[0]
        return " | ".join(str(item) for item in cleaned)

    if hasattr(value, "tolist") and not isinstance(value, (str, bytes)):
        try:
            as_list = value.tolist()
        except Exception:
            as_list = value
        if isinstance(as_list, list):
            flattened = []
            for item in as_list:
                if isinstance(item, list):
                    flattened.extend(item)
                else:
                    flattened.append(item)
            cleaned = [item for item in flattened if not pd.isna(item)]
            if not cleaned:
                return None
            if len(cleaned) == 1:
                return cleaned[0]
            return " | ".join(str(item) for item in cleaned)

    return value


def _format_metric_value(value: object) -> str:
    normalized = _normalize_metric_value(value)
    if normalized is None:
        return "No disponible"
    try:
        if pd.isna(normalized):
            return "No disponible"
    except (TypeError, ValueError):
        pass
    if isinstance(normalized, (int, float)) and not isinstance(normalized, bool):
        return f"{normalized:.2f}"
    return str(normalized)


def _score_progress_html(value: object) -> str:
    normalized = _normalize_metric_value(value)
    try:
        numeric = float(normalized)
    except (TypeError, ValueError):
        return ""

    if numeric < 0 or numeric > 1:
        return ""

    width = max(0.0, min(100.0, numeric * 100.0))
    return f'<div class="metric-track"><div class="metric-fill" style="width:{width:.1f}%"></div></div>'


def _style_detail_dataframe(df: pd.DataFrame):
    numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
    styled = df.style
    if numeric_columns:
        styled = styled.format("{:.2f}", subset=numeric_columns)
    return styled.set_properties(
        **{
            "border-color": "#e7edf3",
            "font-size": "0.92rem",
        }
    )


def render_dimension_scores(df_dimensiones: pd.DataFrame) -> None:
    st.markdown("### Perfil integral")

    if df_dimensiones.empty:
        st.info("No se encontró score integral para este cliente.")
        return

    row = df_dimensiones.iloc[0]
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    score_fields = [
        ("Economica", "Económica"),
        ("Relacional", "Relacional"),
        ("Cumplimiento", "Cumplimiento"),
        ("Potencial", "Potencial"),
    ]

    for col, (key, label) in zip((col1, col2, col3, col4), score_fields):
        value = row.get(key, "No disponible")
        display = f"{float(value):.2f}" if pd.notna(value) and value != "No disponible" else "No disponible"
        with col:
            st.markdown(
                f"""
                <div class="dimension-score-card">
                    <div class="dimension-score-title">{label}</div>
                    <div class="dimension-score-value">{display}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_active_services(servicios_activos: tuple[str, ...]) -> None:
    st.markdown("### Servicios activos")
    if not servicios_activos:
        st.info("El cliente no tiene servicios activos registrados en la tabla de dimensiones.")
        return

    chips = "".join([f'<span class="service-chip">{servicio}</span>' for servicio in servicios_activos])
    st.markdown(chips, unsafe_allow_html=True)


def render_service_details(detalle_servicios: dict[str, dict[str, pd.DataFrame]]) -> None:
    st.markdown("### Detalle por servicio")

    if not detalle_servicios:
        st.info("No hay detalle de servicios disponible para este cliente.")
        return

    service_tabs = st.tabs(list(detalle_servicios.keys()))
    detail_labels = {
        "dimensiones": "Dimensiones",
        "indicadores": "Indicadores",
        "variables": "Variables",
    }

    for service_tab, (service_name, detail_map) in zip(service_tabs, detalle_servicios.items()):
        with service_tab:
            inner_tabs = st.tabs([detail_labels[key] for key in detail_labels if key in detail_map])
            for inner_tab, detail_key in zip(inner_tabs, [key for key in detail_labels if key in detail_map]):
                with inner_tab:
                    df = detail_map[detail_key]
                    if df.empty:
                        st.info(f"No hay información de {detail_labels[detail_key].lower()} para {service_name}.")
                    else:
                        st.dataframe(_style_detail_dataframe(df), width="stretch", height=280)


def _score_progress_html(value: object) -> str:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return ""

    if numeric < 0 or numeric > 1:
        return ""

    width = max(0.0, min(100.0, numeric * 100.0))
    return f"""
    <div class="metric-track">
        <div class="metric-fill" style="width:{width:.1f}%"></div>
    </div>
    """


def _format_metric_value(value: object) -> str:
    if value is None or pd.isna(value):
        return "No disponible"
    if isinstance(value, (int, float)):
        return f"{value:.2f}"
    return str(value)


def _render_metric_card(label: str, value: object) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{_format_metric_value(value)}</div>
            {_score_progress_html(value)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_customer_integral_overview(
    df_dimensiones: pd.DataFrame,
    servicios_activos: tuple[str, ...],
) -> None:
    st.markdown('<div class="section-heading">Resumen integral</div>', unsafe_allow_html=True)
    left_col, right_col = st.columns([1.15, 0.85], gap="large")

    with left_col:
        with st.container(border=True):
            _render_panel_header("Perfil integral", "Score actual del cliente en las cuatro dimensiones principales.")
        if df_dimensiones.empty:
            st.info("No se encontró score integral para este cliente.")
        else:
            row = df_dimensiones.iloc[0]
            grid_a, grid_b = st.columns(2, gap="medium")
            grid_c, grid_d = st.columns(2, gap="medium")
            score_fields = [
                ("Economica", "Económica"),
                ("Relacional", "Relacional"),
                ("Cumplimiento", "Cumplimiento"),
                ("Potencial", "Potencial"),
            ]
            for col, (key, label) in zip((grid_a, grid_b, grid_c, grid_d), score_fields):
                with col:
                    _render_metric_card(label, row.get(key))

    with right_col:
        with st.container(border=True):
            _render_panel_header("Servicios activos", "Presencia actual del cliente dentro del modelo integral.")
        if not servicios_activos:
            st.info("El cliente no tiene servicios activos registrados en la tabla de dimensiones.")
        else:
            st.markdown(
                f"""
                <div class="service-highlight">
                    <div class="service-highlight-value">{len(servicios_activos)}</div>
                    <div class="service-highlight-copy">servicios activos encontrados para este cliente</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            chips = "".join(
                [
                    f'<span class="service-chip"><span class="service-chip-icon">{SERVICE_ICONS.get(servicio, "•")}</span>{servicio}</span>'
                    for servicio in servicios_activos
                ]
            )
            st.markdown(f'<div class="service-chip-wrap">{chips}</div>', unsafe_allow_html=True)


def render_service_details_dashboard(detalle_servicios: dict[str, dict[str, pd.DataFrame]]) -> None:
    st.markdown('<div class="section-heading">Detalle por servicio</div>', unsafe_allow_html=True)

    if not detalle_servicios:
        st.info("No hay detalle de servicios disponible para este cliente.")
        return

    service_tabs = st.tabs(list(detalle_servicios.keys()))
    detail_labels = {
        "dimensiones": "Dimensiones",
        "indicadores": "Indicadores",
        "variables": "Variables",
    }

    for service_tab, (service_name, detail_map) in zip(service_tabs, detalle_servicios.items()):
        with service_tab:
            detail_keys = [key for key in ("dimensiones", "indicadores", "variables") if key in detail_map]
            inner_tabs = st.tabs([detail_labels[key] for key in detail_keys])

            for inner_tab, detail_key in zip(inner_tabs, detail_keys):
                with inner_tab:
                    df = detail_map[detail_key]
                    if df.empty:
                        st.info(f"No hay información de {detail_labels[detail_key].lower()} para {service_name}.")
                        continue

                    row = df.iloc[0]
                    visible_columns = [
                        column
                        for column in df.columns
                        if str(column).strip().lower() not in {"tipoidentificacion", "identificacion"}
                    ]

                    for start in range(0, len(visible_columns), 4):
                        current_columns = visible_columns[start:start + 4]
                        cols = st.columns(4, gap="medium")
                        for col, column_name in zip(cols, current_columns):
                            with col:
                                _render_metric_card(str(column_name), row.get(column_name))


def render_customer_integral_overview(
    df_dimensiones: pd.DataFrame,
    servicios_activos: tuple[str, ...],
) -> None:
    st.markdown('<div class="section-heading">Resumen integral</div>', unsafe_allow_html=True)
    left_col, right_col = st.columns([1.15, 0.85], gap="large")

    with left_col:
        with st.container(border=True):
            _render_panel_header("Perfil integral", "Score actual del cliente en las cuatro dimensiones principales.")
            if df_dimensiones.empty:
                st.info("No se encontro score integral para este cliente.")
            else:
                row = df_dimensiones.iloc[0]
                grid_a, grid_b = st.columns(2, gap="medium")
                grid_c, grid_d = st.columns(2, gap="medium")
                score_fields = [
                    ("Economica", "Economica"),
                    ("Relacional", "Relacional"),
                    ("Cumplimiento", "Cumplimiento"),
                    ("Potencial", "Potencial"),
                ]
                for col, (key, label) in zip((grid_a, grid_b, grid_c, grid_d), score_fields):
                    with col:
                        _render_metric_card(label, row.get(key))

    with right_col:
        with st.container(border=True):
            _render_panel_header("Servicios activos", "Presencia actual del cliente dentro del modelo integral.")
            if not servicios_activos:
                st.info("El cliente no tiene servicios activos registrados en la tabla de dimensiones.")
            else:
                st.markdown(
                    f"""
                    <div class="service-highlight">
                        <div class="service-highlight-value">{len(servicios_activos)}</div>
                        <div class="service-highlight-copy">servicios activos encontrados para este cliente</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                chips = "".join(
                    [
                        f'<span class="service-chip"><span class="service-chip-icon">{SERVICE_ICONS.get(servicio, "-")}</span>{servicio}</span>'
                        for servicio in servicios_activos
                    ]
                )
                st.markdown(f'<div class="service-chip-wrap">{chips}</div>', unsafe_allow_html=True)


def _score_progress_html(value: object) -> str:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return ""

    if numeric < 0 or numeric > 1:
        return ""

    width = max(0.0, min(100.0, numeric * 100.0))
    return f'<div class="metric-track"><div class="metric-fill" style="width:{width:.1f}%"></div></div>'


def _render_metric_card(label: str, value: object) -> None:
    html = (
        f'<div class="metric-card">'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-value">{_format_metric_value(value)}</div>'
        f'{_score_progress_html(value)}'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_contracts_section(df_contracts: pd.DataFrame) -> None:
    if df_contracts.empty:
        st.info("Actualmente no es suscriptor de ningún contrato.")
        return

    st.markdown("### Contratos")

    for _, row in df_contracts.iterrows():
        contrato = row.get("Contrato", "Sin contrato")
        estado = row.get("Estado", "Sin estado")
        with st.expander(f"Contrato {contrato} | Estado: {estado}", expanded=False):
            col1, col2 = st.columns(2, gap="large")

            with col1:
                st.markdown(f"**Contrato:** {contrato}")
                st.markdown(f"**Estado:** {estado}")
                st.markdown(f"**Categoría:** {row.get('Categoria', 'No disponible')}")
                st.markdown(f"**Subcategoría:** {row.get('Subcategoria', 'No disponible')}")
                st.markdown(f"**Dirección:** {row.get('Direccion', 'No disponible')}")

            with col2:
                st.markdown(f"**Barrio:** {row.get('Barrio', 'No disponible')}")
                st.markdown(f"**Localidad:** {row.get('Localidad', 'No disponible')}")
                st.markdown(f"**Departamento:** {row.get('Departamento', 'No disponible')}")
                st.markdown(f"**Mercado:** {row.get('Mercado', 'No disponible')}")
