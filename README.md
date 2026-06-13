# NYC 311 Service Requests — Data Visualization Project

Análisis exploratorio y visual de ~20.8 millones de solicitudes de servicio ciudadano en Nueva York (2020–2026), usando Python para la cadena de datos y Tableau para las visualizaciones finales.

**Dataset**: [311 Service Requests from 2010 to Present](https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9) — NYC Open Data  
**Descarga**: 2026-04-18 · 44 columnas · 20,855,981 filas

---

## Estado del proyecto

| Etapa | Estado | Notebook |
|---|---|---|
| 01 · Perfilado y granularidad | ✅ Completo | `notebooks/01-perfilado-311.ipynb` |
| 02 · Limpieza de datos | ✅ Completo | `notebooks/02-limpieza-311.ipynb` |
| 03 · Modelado de fuentes | ✅ Completo | `notebooks/03-modelado-311.ipynb` |
| 04 · Visualizaciones Tableau | ⏳ Pendiente | — |

---

## Preguntas analíticas

El perfilado del dataset identificó **6 preguntas viables** y **4 descartadas** según disponibilidad y completitud de variables. Ver criterios completos en [`docs/decisiones-analiticas.md`](docs/decisiones-analiticas.md).

**Viables:**
- ¿Cuántas solicitudes hay por Borough y año?
- ¿Qué tipos de problema (Problem) son más frecuentes?
- ¿Cuál es el tiempo mediano de resolución por agencia?
- ¿Qué canal de reporte genera más solicitudes?
- ¿Cómo se distribuyen espacialmente los incidentes en NYC?
- ¿El volumen de solicitudes ha crecido desde 2020?

**Descartadas** (variable no observada o dataset incorrecto):
- Satisfacción ciudadana — no existe la variable
- Correlación puentes/pobreza — 90%+ nulos en Bridge cols + sin variable socioeconómica
- Tipos de crimen por precinto — el 311 no registra crímenes
- Patrones TLC por borough — 90%+ nulos en Vehicle Type / Taxi Borough

---

## Decisiones técnicas clave

### Por qué 15 columnas y no las 44
De las 44 columnas originales, 12 son campos geográficos de detalle redundantes con Latitude/Longitude, y 8 son campos sparse con >70% de nulos (Bridge, TLC, Vehicle Type) que solo aplican a subconjuntos específicos de agencias. Se seleccionaron las 15 columnas que cubren directamente las 6 preguntas analíticas viables.

### Por qué carga por chunks y no `pd.read_csv` directo
El CSV completo produce un DataFrame de ~4+ GB en RAM. La carga por chunks de 50,000 filas con `usecols` restringido reduce el footprint a 16,252 MB — manejable en entornos locales sin Spark ni cloud.

### Por qué mediana y no media para tiempo de resolución
La media de `resolution_hours` es 211.6 h pero la mediana es 7.1 h — diferencia de 30x causada por una distribución fuertemente sesgada a la derecha. Usar la media en Tableau produciría una interpretación errónea del desempeño real de las agencias.

Ver justificaciones completas → [`docs/decisiones-analiticas.md`](docs/decisiones-analiticas.md)

---

## Estructura del repositorio

```
NYC-311-ANALYTICS/
├── data/                          ← dataset crudo (excluido del repo, ver .gitignore)
│   └── 311_Service_Requests_from_2020_to_Present_20260418.csv
├── docs/
│   └── decisiones-analiticas.md  ← justificaciones metodológicas detalladas
├── notebooks/
│   ├── 01-perfilado-311.ipynb     ← perfilado, granularidad y viabilidad de preguntas
│   ├── 02-limpieza-311.ipynb      ← limpieza y bitácora de transformaciones
│   ├── 03-modelado-311.ipynb      ← modelo estrella y fuentes para Tableau
│   └── _shared.py                 ← utilidades compartidas (rutas, perfilado, exportación)
├── outputs/
│   ├── week-02-311/               ← perfilado: profile_table_311.csv, clean_sample_tableau.csv, question_matrix.csv
│   ├── week-03-311/                ← limpieza: 311_clean.csv, cleaning_log.csv, cleaning_comparison.csv
│   └── week-04-311/                ← modelado: fact_311.csv + dimensiones + agregaciones para Tableau
├── tableau/                        ← workbook (E5/E6)
├── .gitignore
└── README.md
```

Todas las rutas de salida (`OUTPUT_DIR`, `ensure_output_dir`/`save_for_tableau` en `_shared.py`) se resuelven respecto a la raíz del proyecto, no al directorio `notebooks/`, para que los CSVs queden siempre en `outputs/week-XX-311/` listos para conectar en Tableau.

---

## Reproducibilidad

```bash
# Dependencias
pip install pandas numpy matplotlib seaborn

# El CSV va en data/ (no incluido en el repo por tamaño)
# Descargar desde: https://data.cityofnewyork.us/api/views/erm2-nwe9/rows.csv

# Ejecutar en orden
jupyter notebook notebooks/01-perfilado-311.ipynb
```

> **Nota**: El dataset descargado en abril 2026 tiene 20,855,981 filas. Los resultados pueden variar si se descarga en una fecha posterior — NYC Open Data actualiza el archivo diariamente.

---

## Herramientas

- **Python 3.11** — pandas, numpy, matplotlib, seaborn
- **Tableau Desktop** — visualizaciones finales (en progreso)
- **Jupyter Notebooks** — cadena de análisis documentada y reproducible