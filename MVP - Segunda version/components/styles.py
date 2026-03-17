import streamlit as st


def load_base_css() -> None:
    css = """
    <style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0;
    }

    div.stButton > button {
        border-radius: 10px;
        font-weight: 600;
        height: 3.5rem;
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
    }

    .app-shell-header-copy h1 {
        margin: 0;
        color: #1e3a8a;
        font-size: 2.6rem;
        font-weight: 800;
        line-height: 1.2;
    }

    .app-shell-header-copy p {
        margin: 0;
        color: #64748b;
        font-size: 1.15rem;
        font-weight: 400;
    }

    .app-shell-status {
        text-align: right;
        color: #94a3b8;
        font-size: 0.9rem;
    }

    .app-shell-footer {
        text-align: center;
        color: #94a3b8;
        font-size: 0.8rem;
        border-top: 1px solid #e2e8f0;
        padding-top: 20px;
    }

    .placeholder-card {
        border: 1px solid #e7edf3;
        border-radius: 16px;
        padding: 24px;
        background: #ffffff;
    }

    .placeholder-title {
        color: #1f3c88;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 0.4rem;
    }

    .placeholder-copy {
        color: #5e6e82;
        font-size: 1rem;
    }

    .service-detail-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
        border: 1px solid #e5e7eb;
        margin-top: 1.5rem;
    }

    .service-detail-header {
        background: #0077cc;
        margin: -1.5rem -1.5rem 1.2rem -1.5rem;
        padding: 1.5rem;
        color: white;
        display: flex;
        align-items: center;
        border-radius: 12px 12px 0 0;
    }

    .service-detail-icon {
        font-size: 2rem;
        margin-right: 1rem;
    }

    .service-detail-header-text-main {
        font-size: 1.4rem;
        font-weight: 600;
        margin-bottom: 0.2rem;
    }

    .service-detail-header-text-sub {
        font-size: 0.9rem;
        opacity: 0.9;
    }

    .chip-group {
        margin-top: 0.8rem;
    }

    .chip {
        display: inline-block;
        padding: 4px 12px;
        background: #eef6ff;
        color: #0077cc;
        border-radius: 12px;
        margin-right: 6px;
        font-size: 0.8rem;
        font-weight: 500;
    }

    .section-box {
        background: #f5f9ff;
        border-left: 4px solid #0077cc;
        padding: 1rem;
        border-radius: 6px;
        margin-bottom: 1rem;
    }

    .section-title {
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.2rem;
    }

    .section-subtitle {
        font-size: 0.9rem;
        opacity: 0.85;
        margin-bottom: 0.5rem;
    }

    .bullet-title {
        font-weight: 600;
        margin-top: 1rem;
        margin-bottom: 0.1rem;
    }

    .bullet-sub {
        font-size: 0.9rem;
        opacity: 0.9;
        margin-bottom: 0.4rem;
    }

    ul.custom-list {
        margin-top: 0.3rem;
        margin-bottom: 0.8rem;
    }

    ul.custom-list li {
        margin-bottom: 0.3rem;
        font-size: 0.9rem;
    }

    .divider {
        height: 1px;
        background: #e5e7eb;
        margin: 1.5rem 0;
    }

    .info-box {
        padding: 1.2rem 1.5rem;
        background: #f5f9ff;
        border-left: 4px solid #0077cc;
        border-radius: 8px;
        margin-bottom: 1.8rem;
    }

    .service-card-subtitle {
        text-align: center;
        margin-top: 5px;
        font-size: 0.85rem;
        color: #6b7280;
    }

    .hint-text {
        text-align: center;
        margin-top: 1rem;
        font-size: 0.85rem;
        color: #6b7280;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
