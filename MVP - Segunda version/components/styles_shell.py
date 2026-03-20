import streamlit as st


def load_base_css() -> None:
    css = """
    <style>
    .block-container {
        padding-top: 0.5rem;
        padding-bottom: 0;
    }

    div.stButton > button {
        border-radius: 16px;
        font-weight: 600;
        height: 3.55rem;
        border: 1px solid #d9e4f1;
        transition: all 0.24s ease;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
    }

    div.stButton > button[kind="secondary"] {
        background: #ffffff;
        color: #24364d;
        border-color: #d9e4f1;
    }

    div.stButton > button[kind="secondary"]:hover {
        background: #f8fbff;
        color: #0f3d75;
        border-color: #bfd5ee;
        transform: translateY(-1px);
    }

    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #0f3d75 0%, #1d4f91 100%);
        color: #ffffff;
        border-color: #0f3d75;
        box-shadow: 0 8px 18px rgba(15, 61, 117, 0.14);
    }

    div.stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #0d3565 0%, #184781 100%);
        color: #ffffff;
        border-color: #0d3565;
        transform: translateY(-1px);
    }

    .app-shell-hero {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        gap: 1.2rem;
        padding: 1.1rem 1.3rem;
        margin-bottom: 0.85rem;
        border: 1px solid #dbeafe;
        border-radius: 22px;
        background: linear-gradient(135deg, #f8fbff 0%, #eef5ff 100%);
    }

    .app-shell-brand {
        display: flex;
        align-items: center;
        gap: 1.15rem;
        min-width: 0;
    }

    .app-shell-logo-wrap {
        flex: 0 0 auto;
        width: 150px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .app-shell-logo {
        width: 100%;
        max-width: 150px;
        height: auto;
        object-fit: contain;
    }

    .app-shell-logo-fallback {
        font-size: 1.4rem;
        font-weight: 800;
        color: #0f3d75;
    }

    .app-shell-header-copy {
        min-width: 0;
    }

    .app-shell-header-copy h1 {
        margin: 0;
        color: #0f3d75;
        font-size: 2.75rem;
        font-weight: 800;
        line-height: 1.08;
        letter-spacing: -0.03em;
    }

    .app-shell-header-copy p {
        margin: 0.45rem 0 0 0;
        color: #64748b;
        font-size: 1.08rem;
        font-weight: 400;
        max-width: 960px;
        line-height: 1.5;
    }

    .app-shell-nav-panel {
        padding: 0.1rem 0 0.15rem 0;
        margin-bottom: 0.3rem;
    }

    .app-shell-nav-head {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        margin-bottom: 0.65rem;
    }

    .app-shell-nav-copy {
        display: flex;
        flex-direction: column;
        gap: 0.2rem;
    }

    .app-shell-nav-title {
        color: #0f3d75;
        font-size: 1rem;
        font-weight: 700;
    }

    .app-shell-nav-subtitle {
        color: #64748b;
        font-size: 0.92rem;
    }

    .app-shell-nav-rule {
        height: 1px;
        background: linear-gradient(90deg, #dbe5f0 0%, #e8eef5 100%);
        margin: 0.9rem 0 0.7rem 0;
    }

    .app-shell-content-divider {
        height: 1px;
        background: linear-gradient(90deg, #dbe5f0 0%, #e8eef5 100%);
        margin: 0 0 1.15rem 0;
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

    @media (max-width: 1100px) {
        .app-shell-hero {
            flex-direction: column;
            align-items: flex-start;
        }

        .app-shell-logo-wrap {
            width: 120px;
        }

        .app-shell-header-copy h1 {
            font-size: 2.2rem;
        }
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
