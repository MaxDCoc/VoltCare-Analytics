# ⚡ VoltCare Analytics

**Optimización B2B de mantenimiento de flotas EV** — datos, API y BI en un solo flujo.

[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Go](https://img.shields.io/badge/Go-00ADD8?style=flat&logo=go&logoColor=white)](https://go.dev/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![Power BI](https://img.shields.io/badge/Power_BI-F2C811?style=flat&logo=powerbi&logoColor=black)](https://powerbi.microsoft.com/)

<img width="1530" height="856" alt="Dashboard VoltCare" src="https://github.com/user-attachments/assets/3cca0d3a-e429-4e81-81a0-0e28e5b855a5" />

---

## Resumen ejecutivo (TL;DR)

**VoltCare Analytics** es una solución **end-to-end** para un proveedor B2B de mantenimiento de vehículos eléctricos de última milla: genera un entorno de datos sintético pero coherente (clientes, técnicos y **+50.000 tickets** de servicio), enriquece métricas operativas y expone análisis vía **API REST** para integrarlo con herramientas de **inteligencia de negocio** (por ejemplo **Power BI**).

El valor para el negocio está en **medir y priorizar** lo que impacta disponibilidad de flota y márgenes: **MTTR** (tiempo medio hasta resolución), comparación por tipo de contrato, balance **preventivo vs correctivo** y **segmentación RFM** — con reglas explícitas que traducen números en alertas accionables para operaciones y revenue.

---

## Arquitectura y stack

- **Python** (`pandas`, `numpy`, `Faker`): motor de **generación de datasets** y **análisis** (`notebooks/`), incluyendo feature engineering, exports CSV y un **motor de insights** basado en reglas.
- **Go** (`voltcare-api`): **API HTTP** que orquesta los scripts Python (`exec` + JSON en stdout) y devuelve respuestas JSON a clientes o dashboards.
- **Docker** + **docker-compose**: imagen única con **Go** y **Python** + `requirements.txt`; despliegue local en el puerto **8080**.
- **Power BI**: modelo e informes sobre los CSV generados; archivo de ejemplo sugerido: `dashboards/bi_doc.pbix` (suele vivir en local por tamaño — no versionado por defecto).

```mermaid
flowchart LR
  client[Cliente_HTTP] --> api[API_Go]
  api --> py[Scripts_Python]
  py --> api
  api --> client
```

---

## Estructura del repositorio

Coloca tu informe de **Power BI** en `dashboards/bi_doc.pbix` cuando lo tengas listo.

```text
.
├── docker-compose.yml
├── requirements.txt
├── notebooks/
│   ├── data_generator.py   # genera CSV en data/
│   └── data_analysis.py    # análisis, RFM, insights, API /analyze
├── voltcare-api/
│   ├── cmd/main.go
│   ├── config/
│   ├── handlers/
│   ├── services/
│   ├── Dockerfile
│   └── go.mod
├── dashboards/             # opcional: bi_doc.pbix
└── data/                   # generado (gitignored): clientes, tickets, maestro, RFM…
```

> **Nota:** la carpeta **`data/`** y los **`.csv`** no se suben al repositorio por diseño. Tras clonar, genera datos con **`POST /generate`** (Docker) o ejecutando `python notebooks/data_generator.py` desde tu entorno local.

---

## Insights y valor de negocio

A partir de la exploración del dashboard interactivo, se identificaron tres áreas críticas de mejora para las operaciones de la compañía:

### 1. El Costo Oculto del modelo "Pay-per-use"
* **Hallazgo:** El análisis RFM segmentado por tipo de contrato reveló que, si bien los clientes *Pay-per-use* generan ingresos puntuales altos debido a fallas catastróficas, su MTTR (Tiempo Medio de Reparación) es drásticamente superior al de los clientes con *Suscripción*. Esto genera cuellos de botella impredecibles en el taller y un alto riesgo de fuga de clientes (*churn*).
* **Acción Recomendada:** Diseñar una campaña de *upselling* dirigida a las empresas del cuadrante "Alta Frecuencia" del modelo Pay-per-use, ofreciendo incentivos para migrar al modelo de Suscripción. Esto estabilizará la curva de demanda operativa.

### 2. Cuello de Botella Operativo en "Correctivos de Software"
* **Hallazgo:** La Matriz de Calor de rendimiento demostró que los servicios clasificados como "Correctivo de Software" asignados a técnicos de nivel *Junior* concentran el mayor porcentaje de horas de demora, elevando el MTTR global.
* **Acción Recomendada:** Implementar un esquema de *Shadowing* obligatorio. Emparejar a técnicos Junior con perfiles Senior exclusivamente para diagnósticos de software durante los picos de demanda (ej. lunes por la mañana) para reducir el tiempo de resolución en un 35% proyectado.

### 3. El Valor Predictivo de la Recencia (Recency)
* **Hallazgo:** El cruce de datos indica una correlación directa entre flotas que posponen sus mantenimientos preventivos y la aparición de fallos mecánicos costosos meses después.
* **Acción Recomendada:** Configurar alertas automatizadas en el CRM. Si una flota con contrato activo supera los 45 días sin registrar un servicio preventivo, el equipo de soporte debe emitir un ticket proactivo de contacto.

---

## Cómo ejecutar este proyecto (Quick Start)

### 1. Clonar

```bash
git clone https://github.com/MaxDCoc/VoltCare-Analytics.git
cd VoltCare-Analytics
```

### 2. Variables de entorno (obligatorio para la API)

Crea el archivo **`voltcare-api/.env`** (el `WORKDIR` del contenedor es `voltcare-api`; `godotenv` lo espera ahí):

```env
PORT=8080
```

### 3. Levantar con Docker

```bash
docker compose up --build
```

> Si tu instalación es antigua, prueba: `docker-compose up --build`

Servicio: **`voltcare-api`** → [http://localhost:8080](http://localhost:8080)

### 4. Probar la API

En **PowerShell** de Windows, usa **`curl.exe`** (el alias `curl` puede apuntar a `Invoke-WebRequest` y fallar).

**Healthcheck**

```bash
curl http://localhost:8080/health
```

**Generar dataset** (escribe CSV bajo `data/` dentro del contenedor)

```bash
curl -X POST http://localhost:8080/generate
```

**Analizar** (cuerpo JSON; los tres campos son opcionales, pero si los envías deben ser valores válidos)

Valores permitidos:

- **contract_type:** `Suscripcion`, `Pay-per-use`
- **service_type:** `Preventivo`, `Correctivo Mecanico`, `Correctivo Software`
- **seniority:** `Junior`, `Semi-Senior`, `Senior`

Ejemplo:

```bash
curl -X POST http://localhost:8080/analyze ^
  -H "Content-Type: application/json" ^
  -d "{\"contract_type\":\"Pay-per-use\",\"service_type\":\"Correctivo Software\",\"seniority\":\"Junior\"}"
```

En **macOS/Linux** usa `\` en lugar de `^` para partir líneas, o una sola línea:

```bash
curl -X POST http://localhost:8080/analyze -H "Content-Type: application/json" -d "{\"contract_type\":\"Suscripcion\",\"service_type\":\"Preventivo\",\"seniority\":\"Senior\"}"
```

### 5. Power BI

Abre **`dashboards/bi_doc.pbix`** en **Power BI Desktop** y conecta las fuentes a los CSV generados (por ejemplo `dataset_maestro_limpio.csv`, `rfm_clientes.csv`) según tu modelo.

---

**Stack clave:** **Python** · **Go** · **Docker** · **Power BI** · **MTTR** · **RFM**
