from dataclasses import dataclass
from typing import Callable

import streamlit as st


@dataclass(frozen=True)
class PageDefinition:
    page_id: str
    nav_label: str
    title: str
    render: Callable[[], None]


def render_navigation(
    pages: list[PageDefinition],
    session_key: str,
) -> PageDefinition:
    if session_key not in st.session_state:
        st.session_state[session_key] = pages[0].page_id

    st.markdown(
        """
        <div class="app-shell-nav-panel">
            <div class="app-shell-nav-head">
                <div class="app-shell-nav-copy">
                    <div class="app-shell-nav-title">Explora la plataforma</div>
                    <div class="app-shell-nav-subtitle">Selecciona el módulo de trabajo que quieres consultar.</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(len(pages))
    active_page_id = st.session_state[session_key]

    for index, page in enumerate(pages):
        is_active = active_page_id == page.page_id
        if cols[index].button(
            page.nav_label,
            width="stretch",
            type="primary" if is_active else "secondary",
            key=f"btn_nav_{page.page_id}",
        ):
            if st.session_state[session_key] != page.page_id:
                st.session_state[session_key] = page.page_id
                st.rerun()

    return next(page for page in pages if page.page_id == st.session_state[session_key])
