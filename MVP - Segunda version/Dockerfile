# =============================================================================
# Dockerfile - Cliente Integral (Streamlit)
# =============================================================================

FROM python:3.12-slim-bookworm

# Evitar prompts interactivos
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root para seguridad
RUN useradd --create-home --shell /bin/bash appuser

# Directorio de trabajo
WORKDIR /app

# Copiar requirements primero (mejor cache de Docker)
COPY --chown=appuser:appuser requirements.txt ./

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY --chown=appuser:appuser app.py ./
COPY --chown=appuser:appuser databricks_connection.py ./
COPY --chown=appuser:appuser assets ./assets
COPY --chown=appuser:appuser components ./components
COPY --chown=appuser:appuser services ./services
COPY --chown=appuser:appuser utils ./utils
COPY --chown=appuser:appuser views ./views

# Crear directorio de configuración de Streamlit
RUN mkdir -p /app/.streamlit && chown -R appuser:appuser /app/.streamlit

# Cambiar a usuario no-root
USER appuser

# Variables de entorno por defecto
ENV PORT=3000
ENV STREAMLIT_SERVER_PORT=3000
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Puerto expuesto
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/_stcore/health || exit 1

# Comando de inicio
CMD ["sh", "-c", "streamlit run app.py --server.port=${PORT} --server.address=0.0.0.0 --server.headless=true"]
