import os
import pandas as pd
from databricks import sql
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    host = os.getenv("DATABRICKS_HOST")
    http_path = os.getenv("DATABRICKS_HTTP_PATH")
    token = os.getenv("DATABRICKS_TOKEN")

    missing = []
    if not host:
        missing.append("DATABRICKS_HOST")
    if not http_path:
        missing.append("DATABRICKS_HTTP_PATH")
    if not token:
        missing.append("DATABRICKS_TOKEN")

    if missing:
        raise ValueError(
            f"Faltan variables de entorno de Databricks: {', '.join(missing)}"
        )

    return sql.connect(
        server_hostname=host,
        http_path=http_path,
        access_token=token,
    )


def run_query(query: str) -> pd.DataFrame:
    conn = get_connection()
    try:
        return pd.read_sql(query, conn)
    finally:
        conn.close()