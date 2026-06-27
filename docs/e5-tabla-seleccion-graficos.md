# E5 — Tabla de selección y descarte de gráficos

Proyecto: NYC 311 Analytics  
Entrega: 5 — Dashboard Alpha y Visualización Exploratoria  
Fecha: 2026-06-27

---

## Gráficos aceptados

| # | Gráfico | Tipo de análisis | Fuente de datos | Justificación técnica |
|---|---|---|---|---|
| 1 | Bar chart horizontal — Top 10 familias de problema | Comparación | `agg_familia_problema.csv` | Adecuado para comparar muchas categorías con nombres largos. Permite leer magnitudes con precisión. |
| 2 | Histograma de categorías — Tiempo de resolución | Distribución | `metric_sla_resolucion.csv` | Muestra la forma de la distribución y el peso relativo de cada rango de resolución. Más claro que un box plot para audiencia no técnica. |
| 3 | Scatter plot — Volumen de quejas vs. SLA promedio por agencia | Relación | `metric_sla_resolucion.csv` | Permite detectar agencias con alto volumen y bajo desempeño (cuadrante crítico). Justifica decisiones de priorización operativa. |
| 4 | Line chart — Tendencia de quejas por borough 2020–2025 | Tiempo / Tendencia | `agg_borough_year.csv` | Estándar para series temporales comparativas. Permite ver evolución y comparar 5 boroughs simultáneamente. |
| 5 | Heatmap — Borough × familia de problema | Comparación / Distribución | `seg_familia_borough.csv` | Muestra concentración cruzada en una sola vista. Útil cuando hay dos dimensiones categóricas con muchos valores. |

---

## Gráficos descartados

| # | Gráfico propuesto | Tipo de análisis | Razón del descarte | Reemplazado por |
|---|---|---|---|---|
| 1 | Pie chart — Familias de problema | Comparación | El dataset tiene más de 15 familias de problema. El pie chart es ilegible con más de 5-6 segmentos y no permite comparar magnitudes con precisión. | Bar chart horizontal (Gráfico 1) |
| 2 | Treemap — Borough × familia | Composición / Comparación | La diferencia de tamaño entre boroughs (Manhattan vs. Staten Island) es tan grande que los rectángulos pequeños quedan ilegibles. Dificulta la comparación proporcional entre categorías. | Heatmap (Gráfico 5) |
| 3 | _(completar si se descartó otro)_ | | | |

---

## Notas metodológicas

- La tabla de decisiones se construyó después de probar cada gráfico en Tableau con los datos reales, no antes.
- El criterio principal de selección fue: ¿esta vista responde directamente una pregunta analítica del proyecto?
- El criterio principal de descarte fue: legibilidad + precisión de lectura para la audiencia objetivo.
