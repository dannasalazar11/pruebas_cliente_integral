import base64
from pathlib import Path

import streamlit as st


def _load_logo_data_uri() -> str | None:
    logo_path = Path("assets/logo-efigas-positivo.png")
    if not logo_path.exists():
        return None

    encoded = base64.b64encode(logo_path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def render_header() -> None:
    logo_data_uri = _load_logo_data_uri()
    logo_html = (
        f'<img src="{logo_data_uri}" alt="Efigas" class="app-shell-logo" />'
        if logo_data_uri
        else '<div class="app-shell-logo-fallback">Efigas</div>'
    )

    st.markdown(
        f"""
        <div class="app-shell-hero">
            <div class="app-shell-brand">
                <div class="app-shell-logo-wrap">
                    {logo_html}
                </div>
                <div class="app-shell-header-copy">
                    <h1>Plataforma Cliente Integral</h1>
                    <p>
                        Análisis avanzado de comportamiento del cliente a través de todos sus
                        servicios con Efigas
                    </p>
                </div>
            </div>
            <div class="app-shell-status-wrap">
                <div class="app-shell-status-label">Estado de plataforma</div>
                <div class="app-shell-status-badge">V 2.0 | Conectado</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer() -> None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="app-shell-footer">
            © 2025 Efigas S.A. E.S.P. - BI y Analítica
        </div>
        """,
        unsafe_allow_html=True,
    )
