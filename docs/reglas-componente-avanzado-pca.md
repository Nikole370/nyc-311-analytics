# Reglas del componente avanzado — PCA sobre perfiles de agencia (Notebook 05)

Este documento describe, fuera del código, qué calcula `notebooks/05-pca-agencias.ipynb`: por qué se eligió PCA y no t-SNE, cómo se construyó el perfil de agencia, qué significa cada componente y qué limitaciones tiene el resultado. El notebook **implementa** estas reglas; este documento es la referencia para entenderlas o cuestionarlas sin leer Python.

**Input**: `outputs/tableau/fact_311.csv` — fact_311 completo (20,855,981 filas). No se recalcula nada de los notebooks 01-04; este notebook agrega `fact_311` a nivel de agencia.
**Output**: `outputs/week-06-311/` — perfil por agencia con PCA y cluster, loadings, varianza explicada, parámetros aplicados y validaciones, listos para Tableau.

---

## 1. Por qué PCA y no t-SNE

**Decisión**: aplicar PCA sobre un perfil agregado por agencia, no t-SNE sobre `fact_311` a nivel de registro.

**Por qué**:
- `fact_311.csv` es transaccional (un registro por queja individual) y no tiene 8+ variables numéricas por fila que justifiquen aplicar una técnica de reducción de dimensionalidad directamente sobre el dato crudo.
- La alternativa correcta, prevista en el enunciado del curso ("PCA sobre variables derivadas"), es construir un **perfil agregado** — en este caso, una fila por agencia con variables numéricas derivadas — y aplicar la técnica sobre ese perfil.
- Esa agregación deja **20 agencias** (una fila por agencia, tras el filtro de la sección 3). t-SNE está pensado para revelar estructura no lineal en conjuntos de cientos o miles de puntos; con 20 puntos su resultado es inestable, sensible a la semilla y difícil de defender como reproducible.
- PCA da ejes lineales interpretables — se puede leer literalmente, a partir de los *loadings*, qué variables originales pesan en cada componente (sección 4) — lo cual es más defendible que una proyección no lineal de caja negra cuando la muestra es tan chica.

**Alternativa descartada**: t-SNE sobre el perfil de agencias. Se descartó por el tamaño de muestra (20 puntos) — no por limitación técnica de implementación, sino porque el resultado no sería confiable ni interpretable con tan pocos datos.

---

## 2. Perfil numérico por agencia

**Unidad de análisis**: una fila por agencia (21 agencias en `dim_agencia.csv`, 20 tras el filtro de la sección 3).

### 2.1 Variables incluidas (9)

| Variable | Qué mide | Fórmula |
|---|---|---|
| `volumen_total` | Tamaño de la agencia | `COUNT(Unique Key)` por agencia |
| `horas_promedio` | Velocidad de resolución (promedio) | `AVG(resolution_hours)` sobre quejas resueltas |
| `horas_mediana` | Velocidad de resolución (típica) | `MEDIAN(resolution_hours)` sobre quejas resueltas |
| `pct_horario_nocturno` | Patrón horario | % de quejas abiertas entre 20:00 y 06:59 |
| `pct_top_familia` | Especialización | % de sus quejas que caen en su `problem_family` más frecuente |
| `pct_menos_24h` | SLA — resolución same-day | % resuelto en ≤ 24h |
| `pct_1_3d` | SLA — resolución 1-3 días | % resuelto en (24h, 72h] |
| `pct_3_7d` | SLA — resolución 3-7 días | % resuelto en (72h, 168h] |
| `pct_mas_7d` | SLA — rezago crítico | % resuelto en > 168h |

**Por qué mediana y promedio a la vez**: mismo criterio que el notebook 01 (D-mediana en `decisiones-analiticas.md`) — la distribución de `resolution_hours` está muy sesgada, así que la mediana es la cifra "típica" y el promedio queda como referencia de cuánto lo distorsionan los outliers (ver por ejemplo EDC: mediana 1,439.9h vs promedio 7,836.3h).

### 2.2 Variable evaluada y descartada: `n_boroughs_activos`

Se calculó `n_boroughs_activos` (cantidad de boroughs donde opera cada agencia) como candidata inicial. Resultado: **todas las agencias operan en los 5 boroughs** — la variable tiene varianza cero y no aporta nada a un PCA (un *loading* de 0.000 en ambos componentes). Se documenta el descarte aquí, con el dato real que lo motivó, en vez de eliminarla silenciosamente del código.

### 2.3 Filtro — `MIN_RESUELTOS = 500`

**Qué hace**: excluye agencias con menos de 500 quejas resueltas antes de calcular el perfil.

**Por qué**: con pocos casos, los porcentajes (`pct_menos_24h`, etc.) no son estadísticamente estables — un solo caso puede mover el porcentaje varios puntos. El caso extremo es `3-1-1` (una categoría dentro de `Agency`, no el sistema 311 en general), con **1 sola fila** en todo el dataset de 20.8M — su `pct_horario_nocturno` sería 0% o 100% dependiendo de esa única fila, sin significado real.

**Impacto**: se retienen 20 de 21 agencias (`3-1-1` es la única excluida).

---

## 3. Preprocesamiento — estandarización

**Decisión**: `StandardScaler` (media 0, desviación estándar 1) sobre las 9 variables, antes de PCA.

**Por qué es obligatorio aquí**: `volumen_total` va de cientos a millones (NYPD: 9,067,475) mientras que los `pct_*` van de 0 a 100. Sin estandarizar, PCA quedaría dominado por `volumen_total` únicamente por su magnitud numérica, no porque sea la variable más informativa del perfil operativo.

---

## 4. Resultado del PCA

### 4.1 Varianza explicada

| Componente | % varianza | % acumulado |
|---|---|---|
| PC1 | 43.9% | 43.9% |
| PC2 | 30.2% | 74.0% |
| PC3 | 10.8% | 84.8% |

**Decisión**: usar 2 componentes para la visualización — explican en conjunto **74.0%** de la varianza de las 9 variables originales, suficiente para una proyección 2D razonablemente fiel, y es el máximo graficable en un scatter simple para Tableau.

### 4.2 Interpretación de los componentes (loadings)

| Variable | PC1 | PC2 |
|---|---|---|
| `pct_mas_7d` | **+0.471** | -0.077 |
| `horas_mediana` | **+0.426** | -0.207 |
| `pct_menos_24h` | **-0.397** | -0.265 |
| `pct_top_familia` | +0.327 | 0.182 |
| `volumen_total` | -0.326 | -0.301 |
| `horas_promedio` | +0.318 | -0.202 |
| `pct_3_7d` | -0.160 | **+0.508** |
| `pct_1_3d` | -0.214 | **+0.479** |
| `pct_horario_nocturno` | -0.229 | **-0.479** |

**PC1 — eje de eficiencia de resolución.** Dominado por `pct_mas_7d` y `horas_mediana` (positivos) frente a `pct_menos_24h` y `volumen_total` (negativos). Agencias con PC1 muy negativo combinan alto volumen y resolución rápida (caso extremo: **NYPD**, PC1 = -4.48). Agencias con PC1 muy positivo combinan bajo cumplimiento same-day, alto rezago crítico y alta especialización (`pct_top_familia` cercano a 100%) — caso extremo: **EDC**, PC1 = +4.54.

**PC2 — eje de forma de la distribución y patrón horario.** Dominado por `pct_3_7d` y `pct_1_3d` (positivos) frente a `pct_horario_nocturno` y `volumen_total` (negativos). Separa agencias cuya resolución se concentra en los rangos intermedios (1-7 días, ej. **DSNY** PC2 = +2.47) de agencias con patrón horario nocturno más marcado o tiempos más extremos y menos "término medio" (ej. **NYPD** PC2 = -4.84, **EDC** PC2 = -2.13).

**Conexión con el dashboard alpha**: el insight ya existente ("EDC tarda 27x más que el promedio del sistema") se confirma y se extiende aquí — PC1 muestra que la lentitud de EDC no es un artefacto de una sola métrica, sino un patrón consistente a través de 5 de las 9 variables del perfil (bajo `pct_menos_24h`, alto `pct_mas_7d`, alta `horas_mediana`, alta especialización, bajo volumen relativo).

---

## 5. Clustering complementario (K-Means)

**Decisión**: `k = 3`, elegido comparando `silhouette_score` para k = 2 a 5 (valores obtenidos en la ejecución del notebook, sección 5) y priorizando interpretabilidad — con solo 20 agencias, un *k* mayor fragmenta el conjunto en grupos de 1-2 agencias sin narrativa clara, mientras que k=3 con silhouette competitivo produce 3 grupos con tamaño e interpretación razonables.

**Los 3 clusters, nombrados por velocidad de resolución (no por ID numérico):**

| Cluster | N° agencias | % del volumen total | Mediana de resolución (promedio del grupo) | Agencias |
|---|---|---|---|---|
| **Rápida (alto volumen)** | 1 | 43.5% | 0.9h | NYPD |
| **Intermedia** | 10 | 48.1% | 39.4h | DEP, HPD, DSNY, DHS, DOT, DCA, NYC311-PRD, DOHMH, OSE, DCWP |
| **Rezago crónico** | 9 | 8.4% | 615.7h (~25.7 días) | DOB, OTI, DOITT, DOE, DPR, DFTA, TLC, OOS, EDC |

**Lectura clave**: el clúster de "Rezago crónico" agrupa 9 agencias que en conjunto manejan solo el 8.4% del volumen total de solicitudes, pero con una mediana de resolución 15 veces más lenta que el clúster intermedio (615.7h vs 39.4h) y 684 veces más lenta que NYPD. Confirma, con evidencia independiente del scatter del dashboard alpha, que **EDC y DPR no son casos aislados** — pertenecen a un grupo más amplio de 9 agencias con el mismo patrón estructural de rezago.

---

## 6. Archivos exportados (`outputs/week-06-311/`)

| Archivo | Contenido | Fila = |
|---|---|---|
| `agency_pca_profile.csv` | Las 9 variables del perfil + `PC1`, `PC2`, `cluster` | agencia (20) |
| `pca_loadings.csv` | Peso de cada variable original en PC1 y PC2 | variable (9) |
| `pca_varianza_explicada.csv` | % de varianza explicada por componente y acumulada | componente (9) |
| `parametros_aplicados_pca.csv` | `MIN_RESUELTOS`, variables usadas, n_components, k, semilla, con justificación | parámetro |
| `validation_checks.csv` | Checks de integridad (sección 6 del notebook) | check |
| `pca_scatter_agencias.png` | Scatter PC1 vs PC2, color por cluster, tamaño por volumen | — |
| `pca_loadings_heatmap.png` | Heatmap de los loadings | — |
| `pca_varianza_explicada.png` | Barras de varianza explicada + acumulada | — |

Conexión en Tableau: `agency_pca_profile.csv` se agrega como fuente **independiente** (no se relaciona con `fact_311` — es un agregado por agencia, no un hecho transaccional). Ver sección 8 de `05-pca-agencias.ipynb` para el detalle de la hoja `E6 - PCA agencias`.

---

## 7. Limitaciones

- **Tamaño de muestra pequeño (N=20).** PCA y K-Means son técnicas diseñadas para conjuntos más grandes; con 20 puntos, tanto los componentes como los clusters pueden ser sensibles a agencias individuales con perfiles extremos (NYPD por volumen, EDC por lentitud). Los resultados deben leerse como una **descripción estructurada** del perfil operativo observado, no como una segmentación estadísticamente robusta que generalice a un dataset distinto.
- **Los clusters no tienen fronteras naturales nítidas.** El silhouette score para k=3 (ver notebook, sección 5) es moderado, no alto — indica que los grupos son razonables pero no están perfectamente separados; algunas agencias en el borde del clúster "Intermedia" podrían caer en "Rezago crónico" con una elección distinta de variables o de k.
- **El perfil no incluye variable temporal.** El PCA describe el perfil acumulado de cada agencia en todo el periodo del dataset, no cómo cambia ese perfil en el tiempo — para eso está la vista longitudinal (`E6 - Tendencia temporal`), que es un análisis complementario, no sustituible por este componente.
