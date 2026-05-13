import pandas as pd
import numpy as np
import json
import sys
import json

# 1. Cargamos los datos que generamos en la Fase 1
df_clientes = pd.read_csv('../data/clientes.csv')
df_tickets = pd.read_csv('../data/tickets.csv')
df_tecnicos = pd.read_csv('../data/tecnicos.csv')

# 2. Es CRÍTICO convertir las columnas de texto a formato fecha (datetime) en Pandas
df_tickets['Fecha_Solicitud'] = pd.to_datetime(df_tickets['Fecha_Solicitud'])
df_tickets['Fecha_Resolucion'] = pd.to_datetime(df_tickets['Fecha_Resolucion'])

# 3. Feature Engineering: Calculamos métricas de negocio
# Tiempo de resolución en horas
df_tickets['Tiempo_Resolucion_Horas'] = (df_tickets['Fecha_Resolucion'] - df_tickets['Fecha_Solicitud']).dt.total_seconds() / 3600

# Costo Total = Repuestos + (Horas facturadas * Tarifa por hora del técnico)
TARIFA_HORA = 55.0 # Simulamos que cobramos $55 USD la hora
df_tickets['Ingreso_Total_USD'] = df_tickets['Costo_Repuestos_USD'] + (df_tickets['Horas_Facturadas'] * TARIFA_HORA)


# Unimos los tickets con la información del cliente
df_master = pd.merge(df_tickets, df_clientes, on='ID_Empresa', how='left')
# Unimos también al técnico responsable
df_master = pd.merge(df_master, df_tecnicos, on='ID_Tecnico', how='left')

# Definimos "hoy" como la fecha del último ticket registrado
fecha_actual = df_master['Fecha_Solicitud'].max()

# 4. Análisis RFM (Recency, Frequency, Monetary) para segmentar clientes
# Agrupamos por empresa para calcular el RFM
df_rfm = df_master.groupby('ID_Empresa').agg(
    Recency=('Fecha_Solicitud', lambda x: (fecha_actual - x.max()).days),
    Frequency=('ID_Ticket', 'count'),
    Monetary=('Ingreso_Total_USD', 'sum')
).reset_index()

# Le sumamos el tipo de contrato para tener contexto
df_rfm = pd.merge(df_rfm, df_clientes[['ID_Empresa', 'Tipo_Contrato', 'Tamano_Flota']], on='ID_Empresa', how='left')

# Comparamos el comportamiento según el tipo de contrato
analisis_contratos = df_master.groupby('Tipo_Contrato').agg(
    Ticket_Promedio_USD=('Ingreso_Total_USD', 'mean'),
    Tiempo_Resolucion_Promedio_Horas=('Tiempo_Resolucion_Horas', 'mean'),
    Porcentaje_Preventivos=('Tipo_Servicio', lambda x: (x == 'Preventivo').mean() * 100)
).round(2)

df_master.to_csv('../data/dataset_maestro_limpio.csv', index=False)
df_rfm.to_csv('../data/rfm_clientes.csv', index=False)

def run_analysis():
    df_clientes = pd.read_csv('../data/clientes.csv')
    df_tickets = pd.read_csv('../data/tickets.csv')
    df_tecnicos = pd.read_csv('../data/tecnicos.csv')

    df_tickets['Fecha_Solicitud'] = pd.to_datetime(df_tickets['Fecha_Solicitud'])
    df_tickets['Fecha_Resolucion'] = pd.to_datetime(df_tickets['Fecha_Resolucion'])

    df_tickets['Tiempo_Resolucion_Horas'] = (
        df_tickets['Fecha_Resolucion'] - df_tickets['Fecha_Solicitud']
    ).dt.total_seconds() / 3600

    TARIFA_HORA = 55.0
    df_tickets['Ingreso_Total_USD'] = (
        df_tickets['Costo_Repuestos_USD'] +
        (df_tickets['Horas_Facturadas'] * TARIFA_HORA)
    )

    contract_type = None
    service_type = None
    seniority = None
    if len(sys.argv) > 1:
        contract_type = sys.argv[1]
    if len(sys.argv) > 2:
        service_type = sys.argv[2]
    if len(sys.argv) > 3:
        seniority = sys.argv[3]

    df_master = pd.merge(df_tickets, df_clientes, on='ID_Empresa', how='left')
    df_master = pd.merge(df_master, df_tecnicos, on='ID_Tecnico', how='left')

    if contract_type:
        df_master = df_master[
            df_master['Tipo_Contrato'] == contract_type
        ]
    if service_type:
        df_master = df_master[
            df_master['Tipo_Servicio'] == service_type
        ]
    if seniority:
        df_master = df_master[
            df_master['Seniority'] == seniority
        ]

    mttr = df_master['Tiempo_Resolucion_Horas'].mean()

    contratos = df_master.groupby('Tipo_Contrato').agg(
        tiempo=('Tiempo_Resolucion_Horas', 'mean'),
        ingreso=('Ingreso_Total_USD', 'mean')
    ).to_dict()

    # =========================================
    # BUSINESS INSIGHTS RULES ENGINE
    # =========================================

    insights = []

    # =========================================
    # 1. MTTR EXCESIVAMENTE ALTO
    # =========================================
    # El MTTR (Mean Time To Resolution) representa el tiempo
    # promedio necesario para resolver un ticket de servicio.
    #
    # En operaciones B2B de última milla, un MTTR elevado
    # implica que los vehículos permanecen fuera de servicio
    # durante períodos prolongados, afectando:
    #
    # - la disponibilidad operativa de la flota
    # - el cumplimiento de SLA
    # - la satisfacción del cliente
    #
    # Un valor superior a 55 horas se considera un indicador
    # de posibles ineficiencias operativas o sobrecarga técnica.
    #
    if mttr > 55:
        insights.append(
            "MTTR is significantly above operational target, indicating potential operational inefficiencies."
        )


    # =========================================
    # 2. MTTR ANORMALMENTE BAJO
    # =========================================
    # Aunque un MTTR bajo suele ser positivo, valores
    # extremadamente bajos pueden indicar comportamientos
    # operativos no deseados, como:
    #
    # - cierres prematuros de tickets
    # - diagnósticos superficiales
    # - subregistro de tiempos reales
    #
    # Esta validación ayuda a detectar posibles inconsistencias
    # en la calidad del proceso de soporte técnico.
    #
    if mttr < 15:
        insights.append(
            "MTTR is unusually low, which may indicate superficial diagnostics or premature ticket closures."
        )


    # =========================================
    # 3. TÉCNICOS JUNIOR EN CORRECTIVOS DE SOFTWARE
    # =========================================
    # Los incidentes de software suelen requerir diagnósticos
    # complejos y experiencia técnica avanzada.
    #
    # Cuando este tipo de tareas es asignado a perfiles Junior,
    # existe un mayor riesgo de:
    #
    # - escalaciones frecuentes
    # - tiempos de resolución elevados
    # - retrabajo operativo
    #
    # Este escenario fue identificado previamente como uno de
    # los principales cuellos de botella del negocio.
    #
    if (
        seniority == "Junior"
        and service_type == "Correctivo Software"
    ):
        insights.append(
            "Junior technicians handling software corrective tasks may create operational bottlenecks and increase MTTR."
        )


    # =========================================
    # 4. CLIENTES PAY-PER-USE
    # =========================================
    # Los clientes bajo modalidad Pay-per-use suelen solicitar
    # servicio únicamente ante fallas críticas o urgentes.
    #
    # Esto provoca una demanda menos predecible y dificulta:
    #
    # - la planificación operativa
    # - la asignación eficiente de técnicos
    # - la estabilidad de la carga de trabajo
    #
    # Además, este tipo de clientes suele presentar tickets
    # de mayor complejidad y costo promedio.
    #
    if contract_type == "Pay-per-use":
        insights.append(
            "Pay-per-use contracts may generate unpredictable operational demand spikes and reduce workshop planning efficiency."
        )


    # =========================================
    # 5. BAJA PROPORCIÓN DE MANTENIMIENTO PREVENTIVO
    # =========================================
    # Una baja proporción de mantenimientos preventivos indica
    # que la operación está reaccionando a fallas en lugar de
    # anticiparse a ellas.
    #
    # Esto suele generar:
    #
    # - mayores costos correctivos
    # - incremento de fallas críticas
    # - menor disponibilidad de flota
    #
    # Mantener un porcentaje saludable de preventivos es clave
    # para estabilizar la operación y reducir el downtime.
    #
    preventive_ratio = (
        len(
            df_master[
                df_master["Tipo_Servicio"] == "Preventivo"
            ]
        )
        / len(df_master)
    ) * 100

    if preventive_ratio < 40:
        insights.append(
            "Preventive maintenance ratio is low, indicating a reactive maintenance strategy that may increase long-term operational costs."
        )


    # =========================================
    # 6. SOBRECARGA OPERACIONAL
    # =========================================
    # Un volumen excesivo de tickets puede indicar que la
    # capacidad operativa actual no es suficiente para absorber
    # la demanda de servicio.
    #
    # Este escenario puede provocar:
    #
    # - demoras acumuladas
    # - aumento del MTTR
    # - saturación del personal técnico
    #
    # También puede sugerir crecimiento operativo sin expansión
    # proporcional del equipo de soporte.
    #
    if len(df_master) > 15000:
        insights.append(
            "High ticket volume detected, suggesting potential operational overload or insufficient technical capacity."
        )


    # =========================================
    # 7. MUESTRA ESTADÍSTICAMENTE PEQUEÑA
    # =========================================
    # Cuando la cantidad de registros analizados es demasiado
    # baja, las métricas obtenidas pueden no representar el
    # comportamiento real de la operación.
    #
    # Este control ayuda a advertir posibles problemas de
    # confiabilidad estadística en el análisis.
    #
    if len(df_master) < 100:
        insights.append(
            "Low sample size detected. Analytical reliability may be limited."
        )


    # =========================================
    # 8. TICKET PROMEDIO EXCESIVAMENTE ALTO
    # =========================================
    # Un ingreso promedio muy elevado por ticket puede estar
    # asociado a:
    #
    # - fallas catastróficas
    # - mantenimiento tardío
    # - reemplazo de componentes críticos
    #
    # Este comportamiento suele indicar una operación reactiva
    # y potencialmente costosa para el cliente.
    #
    avg_income = df_master["Ingreso_Total_USD"].mean()

    if avg_income > 1200:
        insights.append(
            "Average ticket value is unusually high, potentially indicating catastrophic failures or delayed maintenance cycles."
        )


    # =========================================
    # 9. EXCESO DE MANTENIMIENTO CORRECTIVO
    # =========================================
    # Cuando predominan los servicios correctivos sobre los
    # preventivos, la operación depende excesivamente de la
    # resolución de fallas una vez ocurridas.
    #
    # Esto reduce:
    #
    # - la previsibilidad operativa
    # - la estabilidad de la flota
    # - la eficiencia del taller
    #
    # Además, suele incrementar costos y tiempos de inactividad.
    #
    corrective_ratio = (
        len(
            df_master[
                df_master["Tipo_Servicio"].str.contains(
                    "Correctivo",
                    na=False
                )
            ]
        )
        / len(df_master)
    ) * 100

    if corrective_ratio > 65:
        insights.append(
            "Corrective maintenance dominates the operation, suggesting insufficient preventive maintenance planning."
        )


    # =========================================
    # 10. RIESGO OPERATIVO EN SEGMENTOS JUNIOR
    # =========================================
    # Si un segmento compuesto exclusivamente por técnicos
    # Junior presenta además un MTTR elevado, existe un riesgo
    # operativo claro relacionado con:
    #
    # - falta de experiencia
    # - necesidad de mentoring
    # - dependencia excesiva de escalaciones
    #
    # Este escenario suele justificar programas de shadowing
    # o soporte senior durante horarios críticos.
    #
    if seniority == "Junior" and mttr > 50:
        insights.append(
            "Junior-only operational segments are showing elevated MTTR, suggesting mentoring or escalation improvements may be required."
        )


    # =========================================
    # 11. CLIENTES DE FLOTA GRANDE CON MTTR ALTO
    # =========================================
    # Las empresas con flotas grandes suelen representar
    # contratos estratégicos y de alto valor comercial.
    #
    # Un MTTR elevado en este segmento aumenta el riesgo de:
    #
    # - incumplimiento de SLA
    # - pérdida de confianza del cliente
    # - churn empresarial
    #
    # El impacto económico de cada hora de downtime suele ser
    # significativamente mayor en este tipo de clientes.
    #
    if (
        "Tamano_Flota" in df_master.columns
        and df_master["Tamano_Flota"].mean() > 40
        and mttr > 50
    ):
        insights.append(
            "Large fleet customers are experiencing elevated MTTR, increasing the risk of SLA violations and customer churn."
        )


    # =========================================
    # 12. OPERACIÓN SIN ANOMALÍAS SIGNIFICATIVAS
    # =========================================
    # Si ninguna regla anterior se activa, se asume que no
    # existen indicadores relevantes de riesgo operativo para
    # los filtros analizados.
    #
    # Esta validación evita devolver listas vacías y permite
    # mantener una respuesta consistente en la API.
    #
    if len(insights) == 0:
        insights.append(
            "No significant operational anomalies detected for the selected filters."
        )

    return {
        "filters": {
            "contract_type": contract_type,
            "service_type": service_type,
            "seniority": seniority
        },
        "records_analyzed": len(df_master),
        "mttr": mttr,
        "contratos": contratos,
        "insights": insights
    }

if __name__ == "__main__":
    result = run_analysis()
    print(json.dumps(result))