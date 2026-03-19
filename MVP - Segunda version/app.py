from dotenv import load_dotenv
import streamlit as st

from components.layout import render_footer, render_header
from components.styles import load_base_css
from core.navigation import PageDefinition, render_navigation
from core.session import NAVIGATION_KEY, reset_app_state
from views.buscador_clientes import render as render_buscador_clientes
from views.informacion_general import render as render_informacion_general
from views.valoracion_integral import render as render_valoracion_integral

load_dotenv()

st.set_page_config(
    page_title="Cliente Integral | Efigas",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def build_pages() -> list[PageDefinition]:
    return [
        PageDefinition(
            page_id="informacion_general",
            nav_label="ℹ️ Información General",
            title="Información General de los Servicios",
            render=render_informacion_general,
        ),
        PageDefinition(
            page_id="valoracion_integral",
            nav_label="💎 Valoración Integral",
            title="Valoración Integral del Cliente",
            render=render_valoracion_integral,
        ),
        PageDefinition(
            page_id="buscador_clientes",
            nav_label="🔎 Buscador de clientes",
            title="Buscador de clientes",
            render=render_buscador_clientes,
        ),
    ]


def main() -> None:
    load_base_css()
    pages = build_pages()

    render_header()
    active_page = render_navigation(pages, session_key=NAVIGATION_KEY)

    previous_page = st.session_state.get("_previous_active_page")
    if previous_page and previous_page != active_page.page_id:
        reset_app_state(preserve_keys={NAVIGATION_KEY, "_previous_active_page"})
    st.session_state["_previous_active_page"] = active_page.page_id

    st.markdown("---")

    with st.container():
        active_page.render()

    render_footer()


if __name__ == "__main__":
    main()
