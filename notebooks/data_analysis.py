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

    return {
        "filters": {
            "contract_type": contract_type,
            "service_type": service_type,
            "seniority": seniority
        },
        "records_analyzed": len(df_master),
        "mttr": mttr,
        "contratos": contratos
    }

if __name__ == "__main__":
    result = run_analysis()
    print(json.dumps(result))