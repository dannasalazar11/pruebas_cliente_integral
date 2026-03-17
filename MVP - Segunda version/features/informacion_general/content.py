METHODOLOGY_HTML = """
<div class="concept-card">
    <div class="method-title">Metodología de Análisis</div>
    <p style="color: #475569; font-size: 1.1rem; line-height: 1.6;">
        El <b>Modelo Cliente Integral</b> transforma información operativa en criterios
        accionables para la toma de decisiones estratégicas, mediante una jerarquía analítica
        claramente definida.
    </p>
    <div style="color: #334155; line-height: 1.7;">
        <p><b>1. Variables:</b> Hechos operativos del cliente en cada servicio.</p>
        <p><b>2. Indicadores:</b> Señales analíticas normalizadas que incorporan reglas de negocio.</p>
        <p><b>3. Dimensiones:</b> Ejes estratégicos comunes para consolidar valor, riesgo y relación.</p>
    </div>
</div>
"""

DIMENSIONS = [
    {"class_name": "dim-econ", "title": "💰 Económica", "description": "Mide la contribución monetaria en términos de utilidad asociada a los servicios utilizados.", "title_color": "#F28E2B"},
    {"class_name": "dim-cump", "title": "✅ Cumplimiento", "description": "Evalúa el riesgo y el respeto a las obligaciones contractuales, financieras y normativas vigentes.", "title_color": "#59A14F"},
    {"class_name": "dim-rel", "title": "🤝 Relacional", "description": "Mide la intensidad, recurrencia y estabilidad del vínculo del cliente con el servicio a través del tiempo.", "title_color": "#4E79A7"},
    {"class_name": "dim-pot", "title": "🚀 Potencial", "description": "Estima la capacidad de crecimiento, adopción de nuevas soluciones o profundización de los servicios actuales.", "title_color": "#B6992D"},
]

SERVICES = {
    "Consumo": {
        "aplica": "Residencial y Comercial",
        "title": "Consumo de Gas Natural",
        "subtitle": "Suministro energético principal para clientes finales.",
        "badges": ["🏠 Residencial", "🏢 Comercial"],
        "sections": [
            {"label": "💰 Económica", "cards": [{"class_name": "f-econ", "html": "<h4 style='color:#F28E2B; margin:0;'>Ganancias por Consumo</h4><p style='font-size:0.95rem; color:#475569; margin-top:10px;'>Ingreso obtenido basado en el tipo de cliente y el periodo de consumo. Se calcula sumando el cargo fijo y el margen de distribución por cada periodo.</p>"}]},
            {"label": "✅ Cumplimiento", "cards": [{"class_name": "f-cump", "html": "<h4 style='color:#59A14F; margin:0;'>Indicador de Cumplimiento de Pagos</h4><p style='font-size:0.9rem; color:#64748b;'>Pondera el comportamiento histórico del pago del recibo de gas.</p><div class='math-box'>Score = ((1.0 × Periodos al día) + (0.1 × Periodos en mora)) / Total periodos</div>"}, {"class_name": "f-cump", "html": "<h4 style='color:#59A14F; margin:0;'>Indicador de Productos Activos</h4><p style='font-size:0.9rem; color:#64748b;'>Identifica el porcentaje de productos de gas que se encuentran activos.</p><div class='math-box'>Score = Productos de Gas Activos / Total de Productos de Gas</div>"}]},
            {"label": "🤝 Relacional", "cards": [{"class_name": "f-rel", "html": "<h4 style='color:#4E79A7; margin:0;'>Indicador de Continuidad</h4><p style='font-size:0.9rem; color:#64748b;'>Mide la estabilidad de la relación del cliente con el servicio a partir de su comportamiento de uso reciente.</p><div class='math-box'>Continuidad = Meses con Consumo &gt; 0 / 12</div>"}, {"class_name": "f-rel", "html": "<h4 style='color:#4E79A7; margin:0;'>Indicador de Antigüedad</h4><p style='font-size:0.9rem; color:#64748b;'>Mide la duración del vínculo del cliente con el servicio de consumo.</p><div class='math-box'>(Ranking relativo de antigüedad)<sup>0.5</sup></div>"}]},
            {"label": "🚀 Potencial", "cards": [{"class_name": "f-pot", "html": "<h4 style='color:#B6992D; margin:0;'>Aprovechamiento de Consumo (IAC)</h4><p style='font-size:0.9rem; color:#64748b;'>Identifica clientes cuyo consumo está por debajo del nivel esperado para su entorno.</p><div class='math-box'>IAC = 1 / (1 + e^(5*(Consumo cliente / Consumo referencia - 1))) + 0.405</div>"}]},
        ],
    },
    "RTR": {
        "aplica": "Residencial y Comercial",
        "title": "Revisión Técnico-Reglamentaria (RTR)",
        "subtitle": "Inspección obligatoria de seguridad para empezar o continuar con el uso de gas. Se realiza cada 5 años.",
        "badges": ["🏠 Residencial", "🏢 Comercial"],
        "sections": [
            {"label": "💰 Económica", "cards": [{"class_name": "f-econ", "html": "<h4 style='color:#F28E2B; margin:0;'>Ingresos por RTR</h4><p style='font-size:0.9rem; color:#475569;'>Calcula el aporte económico histórico del cliente a partir de las revisiones técnicas realizadas.</p><div class='math-box'>IngresosRTR = 0.20 × (Valor Base × Revisiones Realizadas)</div>"}]},
            {"label": "✅ Cumplimiento", "cards": [{"class_name": "f-cump", "html": "<h4 style='color:#59A14F; margin:0;'>Proporción de Revisiones Realizadas</h4><div class='math-box'>RTR Realizadas / RTR Exigidas</div>"}, {"class_name": "f-cump", "html": "<h4 style='color:#59A14F; margin:0;'>Cumplimiento de Plazos</h4><div class='math-box'>RTR Realizadas a Tiempo / RTR Exigidas</div>"}, {"class_name": "f-cump", "html": "<h4 style='color:#59A14F; margin:0;'>Premiación por No Mora</h4><div class='math-box'>e<sup>-(Dias Atraso/60)</sup></div>"}]},
            {"label": "🤝 Relacional", "cards": [{"class_name": "f-rel", "html": "<h4 style='color:#4E79A7; margin:0;'>Indicador de Antigüedad</h4><div class='math-box'>(RankingRelativoDeAntigüedad)<sup>0.5</sup></div>"}, {"class_name": "f-rel", "html": "<h4 style='color:#4E79A7; margin:0;'>Indicador de Fidelidad</h4><div class='math-box'>RTR con EFIGAS / RTR realizadas</div>"}]},
            {"label": "🚀 Potencial", "cards": [{"class_name": "f-pot", "html": "<h4 style='color:#B6992D; margin:0;'>Próxima Revisión RTR</h4><div class='math-box'>((Fecha Última RTR − Fecha Actual) / 5 Años)<sup>2.5</sup></div>"}]},
        ],
    },
    "SAD": {
        "aplica": "Solo Residencial",
        "title": "SAD",
        "subtitle": "Servicios Adicionales Domiciliarios.",
        "badges": ["🏠 Residencial"],
        "sections": [
            {"label": "💰 Económica", "cards": [{"class_name": "f-econ", "html": "<h4 style='color:#F28E2B; margin:0;'>Ganancia Económica por SAD</h4><div class='math-box'>0.20 × ΣValorTrabajosSAD</div>"}]},
            {"label": "✅ Cumplimiento", "cards": [{"class_name": "f-cump", "html": "<h4 style='color:#59A14F; margin:0;'>Ejecución de Órdenes</h4><div class='math-box'>1 − (OrdenesAnuladas / (OrdenesEjecutadas + OrdenesAnuladas))</div>"}]},
            {"label": "🤝 Relacional", "cards": [{"class_name": "f-rel", "html": "<h4 style='color:#4E79A7; margin:0;'>Vínculo por Antigüedad</h4><div class='math-box'>(RankingRelativoDeAntigüedad)<sup>0.5</sup></div>"}, {"class_name": "f-rel", "html": "<h4 style='color:#4E79A7; margin:0;'>Intensidad de la Relación</h4><div class='math-box'>(RankingRelativoDeTrabajosRealizados)<sup>0.7</sup></div>"}]},
            {"label": "🚀 Potencial", "cards": [{"class_name": "f-pot", "html": "<h4 style='color:#B6992D; margin:0;'>Potencialidad General de Servicios</h4><div class='math-box'>CapacidadDisponible × BajaAdopcionDeServicios</div>"}, {"class_name": "f-pot", "html": "<h4 style='color:#B6992D; margin:0;'>Potencial de Venta de Calentador</h4><div class='math-box'>EspacioParaVender × ExperienciaPrevia × TamañoDelCliente</div>"}]},
        ],
    },
    "Efisoluciones": {
        "aplica": "Solo Comercial",
        "title": "Efisoluciones",
        "subtitle": "Servicios Adicionales dirigidos a clientes comerciales.",
        "badges": ["🏢 Comercial"],
        "sections": [
            {"label": "💰 Económica", "cards": [{"class_name": "f-econ", "html": "<h4 style='color:#F28E2B; margin:0;'>Ganancia Económica por Efisoluciones</h4><div class='math-box'>0.20 × ΣValorTrabajosEfisoluciones</div>"}]},
            {"label": "✅ Cumplimiento", "cards": [{"class_name": "f-cump", "html": "<h4 style='color:#59A14F; margin:0;'>Ejecución de Órdenes</h4><div class='math-box'>1 − (OrdenesAnuladas / (OrdenesEjecutadas + OrdenesAnuladas))</div>"}]},
            {"label": "🤝 Relacional", "cards": [{"class_name": "f-rel", "html": "<h4 style='color:#4E79A7; margin:0;'>Vínculo por Antigüedad</h4><div class='math-box'>(RankingRelativoDeAntigüedad)<sup>0.5</sup></div>"}, {"class_name": "f-rel", "html": "<h4 style='color:#4E79A7; margin:0;'>Intensidad de la Relación</h4><div class='math-box'>(RankingRelativoDeTrabajosRealizados)<sup>0.7</sup></div>"}]},
            {"label": "🚀 Potencial", "cards": [{"class_name": "f-pot", "html": "<h4 style='color:#B6992D; margin:0;'>Potencialidad General de Servicios</h4><div class='math-box'>CapacidadDisponible × BajaAdopcionDeServicios</div>"}, {"class_name": "f-pot", "html": "<h4 style='color:#B6992D; margin:0;'>Potencial de Venta de Calentador</h4><div class='math-box'>EspacioParaVender × ExperienciaPrevia × TamañoDelCliente</div>"}]},
        ],
    },
}
