from pathlib import Path

import streamlit as st


def render_header() -> None:
    with st.container():
        c1, c2, c3 = st.columns([1, 4, 1.5], vertical_alignment="center")

        with c1:
            logo_path = Path("assets/logo-efigas-positivo.png")
            if logo_path.exists():
                st.image(str(logo_path), width=160)
            else:
                st.title("Efigas")

        with c2:
            st.markdown(
                """
                <div class="app-shell-header-copy">
                    <h1>Plataforma Cliente Integral</h1>
                    <p>
                        Análisis avanzado de comportamiento del cliente a través de todos sus
                        servicios con Efigas
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with c3:
            st.markdown(
                """
                <div class="app-shell-status">
                    V 2.0 | Conectado
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)


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
