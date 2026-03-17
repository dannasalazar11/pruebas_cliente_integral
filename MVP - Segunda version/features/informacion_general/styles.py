import streamlit as st


def load_page_styles() -> None:
    st.markdown(
        """
        <style>
        .concept-card {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }

        .method-title {
            color: #1E3A8A;
            font-size: 1.8rem;
            font-weight: 800;
            margin-bottom: 20px;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 10px;
        }

        .dim-box {
            padding: 20px;
            border-radius: 12px;
            height: 220px;
            border-top: 6px solid;
            background-color: white;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .dim-box:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 15px rgba(0,0,0,0.1);
        }

        .dim-econ { border-top-color: #F28E2B; }
        .dim-cump { border-top-color: #59A14F; }
        .dim-rel { border-top-color: #4E79A7; }
        .dim-pot { border-top-color: #B6992D; }

        .service-selector-title {
            font-size: 1.6rem;
            font-weight: 700;
            color: #1e293b;
            margin-top: 40px;
            margin-bottom: 20px;
            text-align: center;
        }

        .apply-badge {
            font-size: 0.85rem;
            color: #64748b;
            text-align: center;
            margin-top: 8px;
            font-style: italic;
        }

        .service-header {
            background: linear-gradient(90deg, #1E3A8A 0%, #3B82F6 100%);
            padding: 30px;
            border-radius: 15px;
            color: white;
            margin-bottom: 20px;
        }

        .service-header h2 {
            margin: 0;
            font-size: 2.2rem;
            font-weight: 800;
            color: white !important;
        }

        .service-header p {
            margin: 5px 0 0;
            font-size: 1.1rem;
            opacity: 0.9;
        }

        .badge-container {
            display: flex;
            gap: 10px;
            margin: 15px 0;
        }

        .badge-res {
            background: #DBEAFE;
            color: #1E40AF;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }

        .formula-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-left: 5px solid;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }

        .f-econ { border-left-color: #F28E2B; }
        .f-cump { border-left-color: #59A14F; }
        .f-rel { border-left-color: #4E79A7; }
        .f-pot { border-left-color: #B6992D; }

        .math-box {
            background: #F8FAFC;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            font-family: 'Cambria Math', 'Times New Roman', serif;
            margin: 15px 0;
            font-size: 1.1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
