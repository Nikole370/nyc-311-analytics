# Reglas de métricas, segmentos y parámetros — Notebook 04

Este documento describe, fuera del código, qué calcula `notebooks/04-analitica-311.ipynb`: las fórmulas de cada métrica derivada, el segmento elegido y los parámetros/filtros que controlan el análisis. El notebook **implementa** estas reglas; este documento es la referencia para entenderlas o cuestionarlas sin leer Python.

**Input**: `outputs/week-04-311/` (modelo estrella del notebook 03) — `fact_311` + `dim_fecha`, `dim_geo`, `dim_agencia`, `dim_problema`.
**Output**: `outputs/week-05-311/` — segmento, métricas derivadas, parámetros aplicados y validaciones, listos para Tableau.

---

## 1. Parámetros y filtros

Los parámetros se definen una sola vez (sección 2 del notebook) y controlan todo lo que viene después. Cambiarlos re-calcula automáticamente el segmento y las métricas.

### P1 · Rango de años de análisis (`ANIO_INICIO = 2024`, `ANIO_FIN = 2025`)

**Qué hace**: `fact_periodo = fact[(year >= ANIO_INICIO) & (year <= ANIO_FIN) & Borough.notna()]`. Todo el segmento y las métricas derivadas se calculan sobre `fact_periodo`, no sobre `fact_311` completo.

**Por qué 2024-2025 y no 2023-2026 (todo el dataset)**:
- 2023 solo tiene datos desde agosto (~11,500 filas frente a ~35,000 de un año completo) — es un año parcial por construcción de la muestra.
- 2026 solo tiene datos hasta abril — también parcial.
- Incluirlos en una métrica de variación interanual produciría una conclusión falsa (un año con 4 meses de datos siempre "cae" frente a un año completo, sin que eso refleje una tendencia real).

**Impacto**: se retienen 71,064 de 94,500 filas (75.2%). Las 106 filas sin `Borough` (FK inválida hacia `dim_geo`) también se excluyen — mismo criterio que D6 en `decisiones-analiticas.md`.

**Cómo reusar**: para repetir el análisis con otro rango (p. ej. si se descarga una versión más reciente del dataset con 2027 completo), basta con cambiar `ANIO_INICIO`/`ANIO_FIN` en la sección 2.1 del notebook y re-ejecutar.

### P2 · Umbrales de cumplimiento de resolución (`UMBRALES_SLA_HORAS = [24, 72]`)

**Qué hace**: para cada familia de problema, calcula el % de solicitudes resueltas (`resolution_hours` no nulo) con tiempo de resolución ≤ 24h y ≤ 72h.

**Por qué estos dos valores**:
- **24h (1 día)**: estándar exigente, razonable para problemas que afectan la vía pública de forma inmediata (tráfico, ruido).
- **72h (3 días)**: estándar más realista para procesos administrativos (inspecciones, permisos, infraestructura).

Reportar ambos evita elegir un único umbral arbitrario que favorezca o penalice ciertas familias según su naturaleza operativa.

**Alternativa descartada**: usar la media de `resolution_hours` por familia como umbral dinámico. Se descartó por la misma razón que D3 (`decisiones-analiticas.md`): la distribución está fuertemente sesgada a la derecha y la media no representa el caso típico.

### P3 · Referencia externa: población por borough (Censo EE. UU. 2020)

**Qué hace**: diccionario fijo `POBLACION_BOROUGH` (Bronx, Brooklyn, Manhattan, Queens, Staten Island) usado para normalizar el volumen de solicitudes por habitante.

**Por qué un valor externo y no calculado del dataset**: la población no es una variable observable en 311. Se documenta como constante con fuente (Censo 2020) para que la normalización sea auditable — si la fuente cambia (p. ej. estimaciones intercensales más recientes), se actualiza un único diccionario y se re-exportan los CSVs.

| Borough | Población (Censo 2020) |
|---|---|
| Bronx | 1,472,654 |
| Brooklyn | 2,736,074 |
| Manhattan | 1,694,251 |
| Queens | 2,405,464 |
| Staten Island | 495,747 |

---

## 2. Segmento: familia de problema × borough

**Definición**: cruce entre `problem_family` (11 familias temáticas definidas en el notebook 03, D7) y `Borough` (5 boroughs de `dim_geo`). Una fila por combinación presente en `fact_periodo`.

**Por qué este segmento y no otro**: responde la pregunta central de un dashboard de servicio ciudadano — *¿qué tipo de problema predomina en cada zona de la ciudad?*. Permite priorizar recursos por zona y por tipo de problema simultáneamente.

**Alternativas descartadas**:
- *Canal de reporte × agencia*: describe *cómo* se reporta, no *qué* ni *dónde* — menos relevante para priorización.
- *Hora del día × familia*: ya cubierto parcialmente por `agg_hora.csv` (notebook 03); cruzarlo con familia añade granularidad sin una pregunta de negocio clara que lo justifique en esta entrega.

**Archivo**: `seg_familia_borough.csv` — columnas `Borough`, `problem_family`, `n_solicitudes`, `pct_share_borough`, `tasa_por_10k_hab`.

---

## 3. Métricas derivadas

### M1 · Participación porcentual (`pct_share_borough`)

**Fórmula**: `n_solicitudes / total_solicitudes_del_borough * 100`, redondeado a 2 decimales. Por construcción, suma 100% dentro de cada borough (verificado en la sección 5 del notebook).

**Qué pregunta responde**: dentro de un borough, ¿qué proporción de las solicitudes corresponde a cada familia de problema? Permite comparar la *composición* de problemas entre boroughs de tamaños muy distintos (p. ej. Staten Island vs Brooklyn).

### M2 · Tasa por 10,000 habitantes (`tasa_por_10k_hab`)

**Fórmula**: `n_solicitudes / poblacion_borough * 10,000`, redondeado a 2 decimales, usando `POBLACION_BOROUGH` (P3).

**Qué pregunta responde**: ¿qué borough tiene más solicitudes de una familia dada *en relación a su población*, no en términos absolutos? Sin esta normalización, Brooklyn y Queens siempre parecerían tener "más problemas" simplemente por tener más habitantes.

### M3 · Familia dominante por borough (`metric_familia_dominante.csv`)

**Fórmula**: para cada borough, la familia con mayor `pct_share_borough`, **excluyendo `'Otros'`**.

**Por qué excluir `'Otros'`**: `'Otros'` agrupa 138 de los 187 tipos de `Problem` (la categoría residual de D7 en `decisiones-analiticas.md`) y suele ser la más numerosa en casi todos los boroughs. Reportarla como "familia dominante" no es informativo — es la suma de "todo lo demás", no un tipo de problema accionable. El notebook calcula ambas vistas (con y sin `'Otros'`) pero solo exporta la segunda como métrica, dejando la primera como evidencia de por qué se excluye.

**Resultado** (periodo 2024-2025): Ruido domina en Bronx y Manhattan; Tráfico / Estacionamiento domina en Brooklyn, Queens y Staten Island.

### M4 · Cumplimiento de resolución por familia (`metric_sla_resolucion.csv`)

**Fórmula**: para cada familia de problema, sobre el subconjunto con `resolution_hours` no nulo:
- `pct_dentro_24h = mean(resolution_hours <= 24) * 100`
- `pct_dentro_72h = mean(resolution_hours <= 72) * 100`

**Qué pregunta responde**: ¿qué tipos de problema se resuelven rápido y cuáles se acumulan? Complementa `agg_resolucion_agencia.csv` (notebook 03, que agrupa por *quién* resuelve) con una vista por *qué tipo de problema* se reporta — más cercana a la experiencia del ciudadano, que reporta un `Problem`, no una `Agency`.

**Resultado** (periodo 2024-2025): Tráfico / Estacionamiento y Ruido se resuelven en ≤24h en >90% de los casos (atendidos por NYPD, ver D-NYPD en `agg_resolucion_agencia.csv`); Graffiti, Árboles/Parques e Infraestructura vial quedan por debajo del 30% — consistente con procesos de inspección más largos.

### M5 · Variación interanual del volumen (`metric_variacion_anual.csv`)

**Fórmula**: por borough, `variacion_pct = (n_solicitudes_2025 - n_solicitudes_2024) / n_solicitudes_2024 * 100`, redondeado a 1 decimal.

**Qué pregunta responde**: ¿la demanda de servicios 311 está creciendo, cayendo o estable en cada zona? Es la transformación de `agg_borough_year.csv` (notebook 03, volumen absoluto por año) en una tasa de cambio — la cifra que efectivamente se visualiza como tendencia.

**Por qué solo 2024→2025**: es la única comparación entre dos años completos disponible (ver P1). Si en una ejecución futura hay 3+ años completos, esta métrica puede extenderse a una serie de variaciones año a año sin cambiar la fórmula.

**Resultado**: los 5 boroughs crecieron de 2024 a 2025; Staten Island (+21.4%) y Bronx (+12.6%) muestran el mayor crecimiento relativo, Manhattan el menor (+0.4%).

---

## 4. Archivos exportados (`outputs/week-05-311/`)

| Archivo | Contenido | Fila = |
|---|---|---|
| `seg_familia_borough.csv` | Segmento + M1 + M2 | combinación borough × familia |
| `metric_familia_dominante.csv` | M3 | borough |
| `metric_sla_resolucion.csv` | M4 | familia de problema |
| `metric_variacion_anual.csv` | M5 | borough |
| `parametros_aplicados.csv` | P1, P2, P3 con su justificación | parámetro |
| `validation_checks.csv` | checks de integridad (sección 5 del notebook) | check |
| `heatmap_segmento_familia_borough.png` | visualización de M1 | — |
| `sla_resolucion_familia.png` | visualización de M4 | — |
| `variacion_anual_borough.png` | visualización de M5 | — |

Conexión en Tableau: `seg_familia_borough.csv`, `metric_sla_resolucion.csv` y `metric_variacion_anual.csv` se agregan como fuentes independientes junto al modelo estrella de `outputs/week-04-311/` (ver sección 7 de `03-modelado-311.ipynb` y sección 7 de `04-analitica-311.ipynb`).
