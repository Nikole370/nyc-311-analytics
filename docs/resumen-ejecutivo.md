# Resumen ejecutivo — NYC 311 Analytics

**Proyecto**: Diseño, construcción y defensa de un dashboard interactivo sobre 20,855,981 solicitudes del sistema 311 de Nueva York (2020–2026).
**Dashboard**: [Ver en Tableau Public →](https://public.tableau.com/app/profile/nikole.garcia/viz/Libro2_17838084521540/Final?publish=yes)
**Fecha**: 2026-07-11 · Estado: pipeline y dashboard final completos, componente avanzado integrado.

---

## Pregunta y usuario

**¿Qué patrones de quejas ciudadanas en NYC revelan ineficiencias operativas en la respuesta municipal, y cómo varían por tipo de problema, agencia y borough?**

Dirigido a un **gestor de operaciones del sistema 311** que necesita decidir dónde auditar procesos y cómo priorizar recursos entre agencias y tipos de problema.

## Qué se construyó

- **Pipeline reproducible en Python** (5 notebooks): perfilado → limpieza → modelado en estrella (`fact_311` + 4 dimensiones) → métricas derivadas y segmentación → componente avanzado.
- **Dashboard final en Tableau**: 4 KPIs y 6 vistas (comparación por familia, distribución SLA, relación volumen-eficiencia, tendencia temporal 2020–2026, comparación por borough, y el componente avanzado).
- **Componente avanzado**: PCA + clustering sobre un perfil de 9 variables por agencia (20 agencias), para identificar qué agencias comparten un mismo patrón operativo más allá de una sola métrica.
- **QA técnico**: validación de integridad del pipeline, contraste de color medido (WCAG), uso intencional del color y limitaciones documentadas.

## Hallazgos clave

1. **El sistema es eficiente en general, pero con rezago focalizado**: 57.4% de las solicitudes se resuelve en menos de 1 día; 17.6% (3,674,950 solicitudes) tarda más de 7 días — un patrón estructural, no ruido aleatorio.
2. **Alto volumen no implica baja eficiencia**: NYPD gestiona 9 millones de quejas con resolución casi inmediata. El rezago se concentra en un grupo específico de agencias, no es un problema generalizado del sistema.
3. **El PCA confirma con evidencia independiente** que EDC y DPR no son casos aislados: pertenecen a un clúster de **9 agencias de "rezago crónico"** que en conjunto maneja solo el 8.4% del volumen total, pero con una mediana de resolución de 615.7 horas (~25.7 días) — 684 veces más lenta que NYPD.
4. **"Otros" concentra el 36% de las solicitudes**, más que Ruido (22.8%) y Tráfico (17.5%) juntos — una limitación de la taxonomía del propio sistema 311, no del análisis.
5. **Brooklyn concentra el mayor volumen** (29.9%), consistente con su población; Ruido domina en Bronx y Manhattan, Tráfico domina en el resto de boroughs.

## Recomendación

El 311 **no tiene un problema generalizado de lentitud** — tiene un problema **focalizado** en 9 agencias identificables y en la categoría residual "Otros". Se recomienda:
1. Auditar los procesos de las 9 agencias del clúster de rezago crónico (EDC, DPR, DOB, TLC, DOE, DFTA, OOS, OTI, DOITT) y evaluar si sus tipos de problema requieren un SLA diferenciado.
2. Investigar qué compone realmente la categoría "Otros" a nivel del campo `Problem` granular, para revelar familias emergentes no capturadas por la clasificación actual.

## Limitaciones principales

- El componente avanzado se calculó sobre una muestra de solo 20 agencias — describe el perfil observado, no una segmentación estadísticamente robusta generalizable.
- El semáforo rojo/verde usado en el dashboard no es seguro para daltonismo rojo-verde; mitigado parcialmente con referencias textuales en los KPIs.
- El filtro geográfico retiene 98.1% de las filas; 0.22% de registros con `resolution_hours` negativo se excluyó por ser error de captura, no imputado.

Detalle completo de cada punto: `docs/qa-tecnico-final.md`, `docs/reglas-componente-avanzado-pca.md`, `docs/decisiones-analiticas.md`, `docs/reglas-metricas-segmentos-parametros.md`.
