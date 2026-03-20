import streamlit as st

from features.decisiones_estrategicas.data import (
    load_consolidar_result,
    load_fidelizar_result,
    load_potenciar_result,
    load_recuperar_result,
)
from features.decisiones_estrategicas.sections import (
    load_styles,
    render_consolidar_form,
    render_consolidar_results,
    render_fidelizar_form,
    render_fidelizar_results,
    render_header,
    render_potenciar_form,
    render_potenciar_results,
    render_recuperar_form,
    render_recuperar_results,
)
from features.decisiones_estrategicas.state import (
    get_consolidar_request,
    get_fidelizar_request,
    get_potenciar_request,
    get_recuperar_request,
    initialize_state,
    update_consolidar_request,
    update_fidelizar_request,
    update_potenciar_request,
    update_recuperar_request,
)


def render() -> None:
    initialize_state()
    load_styles()
    render_header()

    current_consolidar_request = get_consolidar_request()
    current_recuperar_request = get_recuperar_request()
    current_fidelizar_request = get_fidelizar_request()
    current_potenciar_request = get_potenciar_request()

    tab_consolidar, tab_recuperar, tab_fidelizar, tab_potenciar = st.tabs(
        ["Consolidar", "Recuperar", "Fidelizar", "Potenciar"]
    )

    with tab_consolidar:
        updated_request = render_consolidar_form(current_consolidar_request)
        if updated_request is not None:
            update_consolidar_request(updated_request)
            current_consolidar_request = updated_request

        if current_consolidar_request.searched and current_consolidar_request.servicios:
            with st.spinner("Analizando clientes a consolidar..."):
                df_resultado = load_consolidar_result(current_consolidar_request)
            render_consolidar_results(df_resultado, current_consolidar_request)

    with tab_recuperar:
        updated_request = render_recuperar_form(current_recuperar_request)
        if updated_request is not None:
            update_recuperar_request(updated_request)
            current_recuperar_request = updated_request

        if current_recuperar_request.searched and current_recuperar_request.servicio:
            with st.spinner("Analizando clientes a recuperar..."):
                df_resultado = load_recuperar_result(current_recuperar_request)
            render_recuperar_results(df_resultado, current_recuperar_request)

    with tab_fidelizar:
        updated_request = render_fidelizar_form(current_fidelizar_request)
        if updated_request is not None:
            update_fidelizar_request(updated_request)
            current_fidelizar_request = updated_request

        if (
            current_fidelizar_request.searched
            and current_fidelizar_request.servicio_ancla
            and current_fidelizar_request.servicio_objetivo
        ):
            with st.spinner("Analizando clientes a fidelizar..."):
                df_resultado = load_fidelizar_result(current_fidelizar_request)
            render_fidelizar_results(df_resultado, current_fidelizar_request)

    with tab_potenciar:
        updated_request = render_potenciar_form(current_potenciar_request)
        if updated_request is not None:
            update_potenciar_request(updated_request)
            current_potenciar_request = updated_request

        if current_potenciar_request.searched and current_potenciar_request.servicios:
            with st.spinner("Analizando clientes a potenciar..."):
                df_resultado = load_potenciar_result(current_potenciar_request)
            render_potenciar_results(df_resultado, current_potenciar_request)
