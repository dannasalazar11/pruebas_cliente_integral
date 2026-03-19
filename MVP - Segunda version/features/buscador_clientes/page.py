import streamlit as st

from features.buscador_clientes.data import load_tipo_identificacion_options, search_customer
from features.buscador_clientes.sections import (
    render_customer_integral_overview,
    load_styles,
    render_contracts_section,
    render_customer_profile,
    render_header,
    render_search_form,
    render_service_details_dashboard,
)
from features.buscador_clientes.state import get_request, initialize_state, update_request


def render() -> None:
    initialize_state()
    load_styles()
    render_header()

    current_request = get_request()
    tipo_identificacion_options = load_tipo_identificacion_options()
    if not tipo_identificacion_options:
        st.warning("No fue posible cargar el catálogo de tipos de identificación.")
        return

    updated_request = render_search_form(tipo_identificacion_options, current_request)

    if updated_request is not None:
        if not updated_request.tipo_identificacion or not updated_request.identificacion:
            st.warning("Selecciona el tipo de identificación y escribe un número de identificación para buscar.")
            return
        update_request(updated_request)
        current_request = updated_request

    if not current_request.searched:
        st.info("Selecciona el universo, el tipo de identificación y busca un cliente para ver su información.")
        return

    result = search_customer(current_request)

    if result.profile is None:
        st.warning("No se encontró un cliente con el tipo y número de identificación ingresados.")
        return

    render_customer_profile(result.profile)
    render_customer_integral_overview(result.dimensiones, result.servicios_activos)
    render_service_details_dashboard(result.detalle_servicios)
    render_contracts_section(result.contratos)
