import streamlit as st


def render_placeholder_page(title: str) -> None:
    st.markdown(
        f"""
        <div class="placeholder-card">
            <div class="placeholder-title">{title}</div>
            <div class="placeholder-copy">
                Esta sección quedó registrada en la nueva navegación y está lista para
                implementarse siguiendo la misma estructura modular.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
