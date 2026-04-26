import pandas as pd
import numpy as np

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

print(df_tickets[['ID_Ticket', 'Tiempo_Resolucion_Horas', 'Ingreso_Total_USD']].head())

# Unimos los tickets con la información del cliente
df_master = pd.merge(df_tickets, df_clientes, on='ID_Empresa', how='left')
# Unimos también al técnico responsable
df_master = pd.merge(df_master, df_tecnicos, on='ID_Tecnico', how='left')

# Verificamos nuestra "Gran Tabla"
print("Columnas del dataset maestro:")
print(df_master.columns.tolist())

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

print("Muestra del Análisis RFM:")
print(df_rfm.head())

# Comparamos el comportamiento según el tipo de contrato
analisis_contratos = df_master.groupby('Tipo_Contrato').agg(
    Ticket_Promedio_USD=('Ingreso_Total_USD', 'mean'),
    Tiempo_Resolucion_Promedio_Horas=('Tiempo_Resolucion_Horas', 'mean'),
    Porcentaje_Preventivos=('Tipo_Servicio', lambda x: (x == 'Preventivo').mean() * 100)
).round(2)

print("\n--- Comportamiento por Tipo de Contrato ---")
print(analisis_contratos)

df_master.to_csv('../data/dataset_maestro_limpio.csv', index=False)
df_rfm.to_csv('../data/rfm_clientes.csv', index=False)