import streamlit as st

from features.informacion_general.content import SERVICES


def render_service(service_name: str) -> None:
    service = SERVICES[service_name]
    badges_html = "".join([f'<span class="badge-res">{badge}</span>' for badge in service["badges"]])

    st.markdown(
        f"""
        <div class="service-header">
            <h2>{service["title"]}</h2>
            <p>{service["subtitle"]}</p>
        </div>
        <div class="badge-container">{badges_html}</div>
        """,
        unsafe_allow_html=True,
    )

    for section in service["sections"]:
        with st.expander(section["label"], expanded=False):
            for card in section["cards"]:
                st.markdown(
                    f'<div class="formula-card {card["class_name"]}">{card["html"]}</div>',
                    unsafe_allow_html=True,
                )


def render_servicio_consumo() -> None:
    render_service("Consumo")


def render_servicio_rtr() -> None:
    render_service("RTR")


def render_servicio_sad() -> None:
    render_service("SAD")


def render_servicio_efisoluciones() -> None:
    render_service("Efisoluciones")
