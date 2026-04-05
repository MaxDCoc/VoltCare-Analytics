import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta

# Inicializamos Faker y fijamos una semilla para que el dataset sea reproducible
fake = Faker('es_AR') # Nombres de empresas y ciudades en formato local
Faker.seed(42)
np.random.seed(42)
random.seed(42)

def generar_clientes(num_clientes=500):
    clientes = []
    for _ in range(num_clientes):
        clientes.append({
            'ID_Empresa': fake.unique.random_int(min=1000, max=9999),
            'Nombre_Empresa': fake.company(),
            # Flotas pequeñas son más comunes que las gigantes
            'Tamano_Flota': int(np.random.choice([10, 25, 50, 100, 200], p=[0.4, 0.3, 0.15, 0.1, 0.05])),
            # 60% paga suscripción mensual, 40% paga por incidente
            'Tipo_Contrato': np.random.choice(['Suscripcion', 'Pay-per-use'], p=[0.6, 0.4]),
            'Fecha_Alta': fake.date_between(start_date='-3y', end_date='today')
        })
    return pd.DataFrame(clientes)

df_clientes = generar_clientes()
print("Clientes generados:", len(df_clientes))

def generar_tecnicos(num_tecnicos=50):
    tecnicos = []
    for _ in range(num_tecnicos):
        tecnicos.append({
            'ID_Tecnico': fake.unique.random_int(min=100, max=999),
            'Nombre_Tecnico': fake.name(),
            # Especialidades requeridas para vehículos eléctricos
            'Especialidad': np.random.choice(['Alta Tension', 'Software', 'Mecanica General'], p=[0.3, 0.3, 0.4]),
            'Seniority': np.random.choice(['Junior', 'Semi-Senior', 'Senior'], p=[0.4, 0.4, 0.2])
        })
    return pd.DataFrame(tecnicos)

df_tecnicos = generar_tecnicos()
print("Técnicos generados:", len(df_tecnicos))

def generar_tickets(df_clientes, df_tecnicos, num_tickets=50000):
    tickets = []
    
    # Extraemos listas para iterar rápido
    empresas_ids = df_clientes['ID_Empresa'].tolist()
    tecnicos_ids = df_tecnicos['ID_Tecnico'].tolist()
    
    # Fechas límite para el historial (últimos 2 años)
    fecha_fin = datetime.now()
    fecha_inicio = fecha_fin - timedelta(days=730)
    
    for i in range(num_tickets):
        fecha_solicitud = fake.date_time_between(start_date=fecha_inicio, end_date=fecha_fin)
        
        # Simulamos que los tickets correctivos tardan más en resolverse que los preventivos
        tipo_servicio = np.random.choice(['Preventivo', 'Correctivo Mecanico', 'Correctivo Software'], p=[0.5, 0.3, 0.2])
        
        if tipo_servicio == 'Preventivo':
            horas = round(random.uniform(1.0, 3.0), 1)
            costo = round(random.uniform(50, 150), 2)
            dias_resolucion = random.randint(0, 1) # Se resuelve rápido
        else:
            horas = round(random.uniform(2.5, 12.0), 1)
            costo = round(random.uniform(200, 1500), 2)
            dias_resolucion = random.randint(1, 5) # Tarda más
            
        fecha_resolucion = fecha_solicitud + timedelta(days=dias_resolucion, hours=random.randint(1,8))
        
        tickets.append({
            'ID_Ticket': f"TK-{100000 + i}",
            'ID_Empresa': random.choice(empresas_ids),
            'ID_Tecnico': random.choice(tecnicos_ids),
            'Fecha_Solicitud': fecha_solicitud,
            'Fecha_Resolucion': fecha_resolucion,
            'Tipo_Servicio': tipo_servicio,
            'Horas_Facturadas': horas,
            'Costo_Repuestos_USD': costo
        })
        
    return pd.DataFrame(tickets)

df_tickets = generar_tickets(df_clientes, df_tecnicos)
print("Tickets generados:", len(df_tickets))

# Guardamos los archivos en la carpeta correspondiente
df_clientes.to_csv('../data/clientes.csv', index=False)
df_tecnicos.to_csv('../data/tecnicos.csv', index=False)
df_tickets.to_csv('../data/tickets.csv', index=False)

print("¡Archivos exportados con éxito!")