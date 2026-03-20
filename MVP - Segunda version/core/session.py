from collections.abc import MutableMapping

import streamlit as st


NAVIGATION_KEY = "seccion_activa"
PAGE_STATE_PREFIXES = ("dashboard_", "info_", "buscador_", "decisiones_")


def clear_state_mapping(
    session_mapping: MutableMapping[str, object],
    preserve_keys: set[str] | None = None,
    prefixes: tuple[str, ...] = PAGE_STATE_PREFIXES,
) -> None:
    keys_to_keep = preserve_keys or set()

    for key in list(session_mapping.keys()):
        if key in keys_to_keep:
            continue
        if key.startswith(prefixes):
            del session_mapping[key]


def reset_app_state(preserve_keys: set[str] | None = None) -> None:
    clear_state_mapping(st.session_state, preserve_keys=preserve_keys)
    st.cache_data.clear()
