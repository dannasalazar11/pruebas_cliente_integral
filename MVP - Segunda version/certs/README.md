# Certificados SSL

Esta carpeta contiene los certificados SSL para los diferentes ambientes.

## Estructura

```
certs/
├── qa/
│   ├── servidor.crt    # Certificado SSL para QA
│   └── servidor.key    # Llave privada para QA
└── prod/
    ├── servidor.crt    # Certificado SSL para Producción
    └── servidor.key    # Llave privada para Producción
```

## Generar certificados autofirmados (solo para desarrollo/QA)

```bash
# QA
openssl req -x509 -newkey rsa:4096 \
  -keyout certs/qa/servidor.key \
  -out certs/qa/servidor.crt \
  -days 365 -nodes \
  -subj "/CN=cliente-integral-qa.efigas.com.co"

# Producción (usar certificados reales de una CA)
# Copiar certificados proporcionados por el equipo de seguridad
```

## Importante

- **NUNCA** subir las llaves privadas (.key) a repositorios públicos
- Los certificados de producción deben ser emitidos por una CA confiable
- Renovar certificados antes de su expiración
