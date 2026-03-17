import streamlit as st

from features.informacion_general.content import DIMENSIONS, METHODOLOGY_HTML, SERVICES
from features.informacion_general.renderers import render_service
from features.informacion_general.state import (
    get_selected_service,
    initialize_state,
    set_selected_service,
)
from features.informacion_general.styles import load_page_styles


def render_methodology() -> None:
    st.markdown(METHODOLOGY_HTML, unsafe_allow_html=True)


def render_dimensions() -> None:
    st.markdown("<h3 style='text-align: center; color: #1E3A8A;'>Dimensiones</h3>", unsafe_allow_html=True)
    columns = st.columns(len(DIMENSIONS))

    for column, dimension in zip(columns, DIMENSIONS):
        with column:
            st.markdown(
                f"""
                <div class="dim-box {dimension['class_name']}">
                    <h4 style='color:{dimension['title_color']}; margin-top:0;'>{dimension['title']}</h4>
                    <p style='font-size: 0.9rem; color: #475569;'>{dimension['description']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_service_selector() -> str:
    selected_service = get_selected_service()
    st.markdown(
        '<p class="service-selector-title">Explorar Detalle Técnico por Servicio</p>',
        unsafe_allow_html=True,
    )

    columns = st.columns(len(SERVICES))
    for (service_name, service_config), column in zip(SERVICES.items(), columns):
        with column:
            is_active = selected_service == service_name
            if st.button(
                service_name,
                width="stretch",
                type="primary" if is_active else "secondary",
                key=f"btn_mdl_{service_name}",
            ):
                set_selected_service(service_name)
                st.rerun()
            st.markdown(f"<p class='apply-badge'>{service_config['aplica']}</p>", unsafe_allow_html=True)

    return get_selected_service()


def render() -> None:
    initialize_state()
    load_page_styles()
    render_methodology()
    st.divider()
    render_dimensions()
    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()
    selected_service = render_service_selector()
    st.markdown("<br>", unsafe_allow_html=True)
    render_service(selected_service)
