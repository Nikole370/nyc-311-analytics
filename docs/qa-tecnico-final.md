# QA técnico final — NYC 311 Analytics (Entrega 6)

Documento de validación técnica, accesibilidad y limitaciones del proyecto, exigido como entregable de la Entrega 6 ("documento de QA con validación técnica, limitaciones y decisiones de diseño"). No repite lo que ya está documentado en otros archivos — donde existe una referencia más detallada, se enlaza en vez de duplicar.

**Fecha**: 2026-07-11. **Estado del pipeline evaluado**: notebooks 01-05 completos, dashboard `Final` en Tableau completo con 4 KPIs y 6 vistas (comparación, distribución, relación, tendencia longitudinal, comparación por borough y componente avanzado PCA).

---

## 1. Validación técnica del pipeline

Cada notebook corre sus propios checks de integridad antes de exportar (sección "Validación" de cada uno). Resultados reales de la última ejecución:

| Notebook | Check | Resultado |
|---|---|---|
| 03 · Modelado | Filas de entrada = filas en `fact_311` | 20,855,981 = 20,855,981 ✅ |
| 03 · Modelado | `Unique Key` sin pérdida ni duplicación | 20,855,981 = 20,855,981 ✅ |
| 03 · Modelado | Filas con `Borough` válido | 20,778,839 de 20,855,981 (99.6%) |
| 03 · Modelado | Filas con `resolution_hours` no nulo | 20,403,323 de 20,855,981 (97.8%) |
| 03 · Modelado | Dimensiones exportadas | `dim_fecha` 2,299 filas · `dim_geo` 5 · `dim_agencia` 21 · `dim_problema` 272 |
| 04 · Analítica | Segmento cubre exactamente `fact_periodo` (sin pérdida ni duplicación) | ✅ (`suma_n_segmento_vs_periodo_ok = True`) |
| 04 · Analítica | `pct_share_borough` suma 100% por borough | ✅ (`pct_share_suma_100_por_borough = True`) |
| 04 · Analítica | Filas en el periodo analizado (2024-2025) | 7,106,481 de 20,855,981 (34.1%) — ver nota en sección 6 |
| 05 · PCA | Sin nulos en las 9 variables del perfil tras el filtro | ✅ (`sin_nulos_en_features = True`) |
| 05 · PCA | Estandarización correcta (media≈0, std≈1) | ✅ |
| 05 · PCA | Los 3 clusters cubren las 20 agencias filtradas, sin pérdida | ✅ (`suma_agencias_por_cluster_ok = True`) |

Detalle completo de cada check: `outputs/week-04-311/validation_checks.csv`, `outputs/week-05-311/validation_checks.csv`, `outputs/week-06-311/validation_checks.csv`.

**Reproducibilidad**: los notebooks 03-05 solo dependen de la salida del notebook anterior (`outputs/week-0X-311/`), no del CSV crudo — se pueden re-ejecutar sin reprocesar 20.8M filas desde cero. Pendiente real heredado de E4: no se ha corrido "Kernel → Restart & Run All" de la cadena completa 01→05 desde el CSV crudo en esta máquina, porque el archivo crudo (`data/311_Service_Requests_from_2020_to_Present_20260418.csv`, excluido del repo por tamaño) no está presente en este entorno. Los notebooks 04 y 05 sí se ejecutaron completos y sin errores a partir de los CSVs ya generados por los anteriores.

---

## 2. Contraste y accesibilidad

Se midió la relación de contraste real (fórmula WCAG, función `contrast_ratio` de `notebooks/_shared.py`) de cada combinación de color usada en el dashboard. Referencia WCAG 2.1 AA: ≥ 4.5:1 para texto normal, ≥ 3:1 para texto grande o elementos gráficos.

| Combinación | Contraste | ¿Cumple AA? |
|---|---|---|
| Texto blanco sobre encabezado azul oscuro `#1F3A5C` | 11.55:1 | ✅ Sí, con margen amplio |
| Texto gris oscuro `#333333` sobre fondo crema de insights `#FFF8E7` | 11.93:1 | ✅ Sí, con margen amplio |
| Número rojo `#C0392B` sobre fondo blanco (KPI rezago crítico) | 5.44:1 | ✅ Sí |
| Número verde `#1E8449` sobre fondo blanco (KPI resuelto rápido) | 4.72:1 | ✅ Sí, pero con poco margen — no oscurecer más el fondo ni aclarar más el verde |
| Título azul oscuro `#1F3A5C` sobre fondo blanco | 11.55:1 | ✅ Sí |

**Hallazgo — no usar texto blanco sobre el ámbar del semáforo de SLA.** Los tonos ámbar de la distribución de tiempos (`#E9A23B` claro, `#C9791F` oscuro) dan **2.17:1** y **3.37:1** con texto blanco encima — ambos por debajo del mínimo AA. Esto no es un problema en la implementación actual porque las etiquetas de dato se colocan **fuera** de la barra (sobre el canvas blanco, no superpuestas), pero es una restricción explícita a mantener: si en algún ajuste futuro se mueven las etiquetas dentro de la barra, hay que usar texto oscuro (`#111111`, que da 8.72:1 sobre el ámbar claro), nunca blanco.

**Hallazgo — el semáforo rojo/verde no es seguro para daltonismo rojo-verde (protanopia/deuteranopia), el tipo más común.** Es una limitación real del diseño actual, no resuelta en esta entrega por restricción de tiempo. Mitigación parcial ya presente: los 3 KPIs con semáforo (`Resuelto en < 1 día`, `Rezago crítico`) ya incluyen una referencia textual explícita (`"Referencia: > 50% = aceptable"` / `"< 10% = aceptable"`) que no depende del color para comunicar si el valor es bueno o malo — eso cubre el caso de uso de los KPIs. La distribución de tiempos (barras verde/ámbar/ámbar/rojo) y el clustering del PCA (verde/azul/rojo) **no** tienen ese respaldo textual además del color; ambas ya tienen las categorías nombradas en el eje o en la leyenda (`< 1 día`, `Rezago crónico`, etc.), lo que da una vía de lectura alternativa a alguien que no distingue el color, aunque no sea tan inmediata. **Recomendación para una iteración futura**: si se dispone de tiempo, agregar un ícono o símbolo (✓/✗, ▲/▼) redundante al color en los 3 KPIs, no solo el texto de referencia.

---

## 3. Uso intencional del color

Regla aplicada consistentemente en todo el proyecto: **rojo o verde solo cuando hay una base de comparación clara** (un umbral, un promedio, un "mejor/peor"); azul neutro `#1F3A5C` para todo lo demás.

Verificación por gráfico:

| Gráfico | Color | ¿Justificado? |
|---|---|---|
| `¿Qué tipo de queja domina el sistema?` (barras por familia) | Azul único | ✅ Sí — comparación de volumen sin juicio de bueno/malo |
| `¿En cuánto tiempo se resuelven las quejas?` (distribución SLA) | Semáforo verde→rojo por rango | ✅ Sí — cada rango tiene una lectura de desempeño explícita |
| `¿Las agencias con más quejas son las más lentas?` (scatter) | Azul + rojo en outliers (EDC, DPR) | ✅ Sí — el rojo marca agencias que superan el umbral de rezago, no una categoría arbitraria |
| KPIs (Resuelto rápido / Rezago crítico) | Verde/rojo según umbral | ✅ Sí — el umbral está impreso en el propio KPI |
| PCA — clusters de agencias | Verde (rápida) / azul (intermedia) / rojo (rezago crónico) | ✅ Sí — el cluster se nombra explícitamente por velocidad de resolución, no es un color arbitrario por categoría |

---

## 4. Jerarquía visual y tipografía

Ya validado y cerrado en la ronda de ajustes de alpha: una sola familia tipográfica en todo el workbook, escala de tamaños consistente (título 20-22px, KPI 28-32px, títulos de gráfico/KPI 12px, insights 11-12px), títulos de KPI sin jerga técnica, contenedores distribuidos en partes iguales.

Las hojas nuevas de E6 (`E6 - Tendencia temporal`, `E6 - Comparación por Borough`, `E6 - PCA agencias`) ya están integradas al dashboard `Final` siguiendo la misma escala de tamaños y la misma paleta de 3 colores cerrada en alpha — no se introdujo una paleta nueva.

---

## 5. Limitaciones del análisis

Limitaciones reales del proyecto, con su cifra de impacto — no genéricas:

1. **Filtro geográfico de latitud/longitud** (`decisiones-analiticas.md`, D4): retiene 98.1% de las filas (20,469,468 de 20,855,981). El 1.9% descartado son registros sin coordenada válida o fuera del rango de NYC — no afecta las conclusiones agregadas, pero cualquier mapa del dashboard excluye ese 1.9%.
2. **Exclusión de `resolution_hours < 0`** (D5/D8): 46,334 registros (0.22%) excluidos por ser errores de captura (`Closed Date < Created Date`), no imputados. Volumen despreciable.
3. **La categoría "Otros" concentra 36% de las solicitudes** (Insight 4 en `docs/e5-insights-exploratorios.md`): es una limitación de la taxonomía del propio sistema 311, no del pipeline — reduce la capacidad del análisis para identificar problemas específicos dentro de ese 36%.
4. **El componente PCA se calculó sobre 20 agencias** (`docs/reglas-componente-avanzado-pca.md`, sección 7): es una muestra pequeña para técnicas de reducción de dimensionalidad; los componentes y clusters describen el perfil observado, no una segmentación estadísticamente robusta que generalice a otro dataset. El silhouette score del clustering (k=3) es moderado, no alto — los clusters son razonables pero sin fronteras nítidas.
5. **La vista longitudinal y transversal de E6 usan `fact_311` completo (todos los años), mientras que las métricas del notebook 04 (`seg_familia_borough`, `metric_sla_resolucion`) están acotadas a 2024-2025** (`ANIO_INICIO`/`ANIO_FIN`, ver `docs/reglas-metricas-segmentos-parametros.md`, P1). Al construir el dashboard final, si una vista mezcla ambas fuentes sin dejarlo explícito, puede confundir al lector sobre qué periodo cubre cada cifra — revisar que los títulos de las hojas de E6 indiquen el rango de años cuando corresponda.
6. **No se completó "Restart & Run All" de la cadena 01→05 desde el CSV crudo en esta máquina** (ver sección 1) — la lógica de cada notebook está validada de forma aislada contra las salidas del anterior, pero no hay una ejecución de punta a punta reciente registrada.

---

## 6. Decisiones de diseño ya justificadas (índice, no duplicado aquí)

| Decisión | Por qué | Dónde está documentada |
|---|---|---|
| Mediana y no media para tiempos de resolución | Distribución sesgada (p50=7.1h vs media=211.6h) | `docs/decisiones-analiticas.md`, D3 |
| Modelo estrella y no tabla plana | Evita redundancia y duplicación de métricas en joins de Tableau | `docs/decisiones-analiticas.md`, D9 |
| Agregaciones pre-calculadas en Python, no campos calculados en Tableau | Auditable y versionado en Git | `docs/decisiones-analiticas.md`, D10 |
| Agrupación semántica de `Problem` en 11 familias (no top-N) | Top-N agrupa por popularidad, no por significado | `docs/decisiones-analiticas.md`, D7 |
| Umbrales SLA de 24h y 72h (no uno solo) | Evita un único umbral arbitrario que favorezca ciertas familias | `docs/reglas-metricas-segmentos-parametros.md`, P2 |
| PCA y no t-SNE para el componente avanzado | Muestra de solo 20 agencias — t-SNE necesita cientos/miles de puntos para ser confiable | `docs/reglas-componente-avanzado-pca.md`, sección 1 |
| Paleta de 3 colores, rojo/verde solo con base de comparación | Evita "decorar" el dashboard con color sin significado | Aplicada en el dashboard `Final` de `tableau/Libro2.twb` |

---

## 7. Estado frente a los criterios de aprobación de E6

| Criterio | Estado |
|---|---|
| El dashboard final responde la pregunta principal sin explicación externa extensa | ✅ Dashboard `Final` integra KPIs, comparación, distribución, relación, tendencia, borough y PCA |
| El pipeline técnico es reproducible y entendible | ✅ Notebooks 01-05, cada uno documentado y con sus propios checks |
| El equipo evidencia cobertura de todo el curso | ✅ Pipeline completo, componente avanzado, historia visual y defensa preparados |
| Se valida contraste, uso de color, etiquetas y títulos analíticos | ✅ Este documento, secciones 2-4 |
| Se incluye una vista longitudinal y una transversal claramente defendibles | ✅ `E6 - Tendencia temporal` y `E6 - Comparación por Borough` integradas al dashboard `Final` |
| La defensa muestra control de supuestos, límites y decisiones | ✅ Secciones 5-6 de este documento |
