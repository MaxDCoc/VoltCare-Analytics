# ⚡ VoltCare Analytics: Optimización B2B de Mantenimiento de Flotas EV

<img width="1530" height="856" alt="Adobe Express - Grabación de pantalla 2026-04-25 213013" src="https://github.com/user-attachments/assets/3cca0d3a-e429-4e81-81a0-0e28e5b855a5" />

## 📌 Resumen Ejecutivo
**VoltCare Analytics** es un proyecto de análisis de datos *end-to-end* diseñado para optimizar las operaciones de mantenimiento de un proveedor B2B de vehículos eléctricos (EVs) de última milla. 

El objetivo principal fue procesar y analizar un volumen de **+50,000 tickets de servicio simulados** para identificar cuellos de botella operativos (medidos a través del MTTR) y maximizar el *Customer Lifetime Value* (CLV) mediante técnicas de segmentación de clientes, proporcionando recomendaciones accionables para la reasignación de técnicos y estrategias comerciales.

## 🛠️ Stack Tecnológico y Arquitectura
* **Ingeniería de Datos (Python):** Uso de `Pandas`, `NumPy` y `Faker` para la generación de un entorno de datos sintético pero lógicamente coherente, inyectando estacionalidad y reglas de negocio complejas.
* **Análisis Cuantitativo:** Feature Engineering, cálculo de métricas de tiempo y segmentación **RFM** (Recency, Frequency, Monetary) aplicada a entornos B2B.
* **Inteligencia de Negocios (Power BI):** Modelado de datos en esquema de estrella, creación de métricas financieras dinámicas con **DAX**, y visualización interactiva utilizando herramientas de IA integradas (Árboles de Descomposición).

---

## 📊 Insights y Recomendaciones de Negocio

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

## 🚀 Reproducción del Proyecto Localmente

Si deseas explorar el código y la lógica de generación de datos:

1. **Clona el repositorio:**
   ```bash
   git clone "https://github.com/MaxDCoc/VoltCare-Analytics.git"
   ```

2. **Instala las dependencias necesarias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Genera el Dataset:** Ejecuta el motor de datos para crear los archivos CSV.
   ```bash
   python notebooks/data_generator.py
   ```

4. **Explora el Análisis RFM:** Abre el notebook interactivo.
   ```bash
   jupyter notebook notebooks/fase2_analisis.ipynb
   ```

5. **Visualiza el Dashboard:** Abre el archivo `dashboards/VoltCare_Report.pbix` utilizando Power BI Desktop.
