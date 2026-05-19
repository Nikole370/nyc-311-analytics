# Decisiones analíticas — NYC 311 Service Requests

Este documento registra las decisiones metodológicas tomadas en cada etapa del proyecto, con el razonamiento que las sustenta. El objetivo es que cualquier decisión pueda defenderse ante una pregunta directa del tipo "¿por qué elegiste X y no Y?".

---

## Etapa 01 · Perfilado y granularidad

### D1 · Selección de 15 columnas de un total de 44

**Decisión**: cargar únicamente 15 de las 44 columnas disponibles.

**Por qué estas y no todas**: las 44 columnas se pueden clasificar en tres grupos:

| Grupo | Columnas | Decisión |
|---|---|---|
| Analíticamente útiles | Agency, Borough, Problem, Created/Closed Date, Status, Channel, Lat/Lon, Unique Key, Community Board, Police Precinct, Problem Detail | ✅ Incluidas (15 total) |
| Geográfico redundante | Incident Address, Street Name, Cross Street 1/2, Intersection 1/2, Incident Zip, City, Landmark | ❌ Descartadas — lat/lon cubre el caso de uso geográfico con mayor precisión y compatibilidad con Tableau Maps |
| Sparse estructural (>70% nulos) | Bridge Highway Name/Direction/Segment, Road Ramp, Vehicle Type, Taxi Company Borough, Taxi Pick Up Location, Facility Type, BBL, X/Y Coordinate | ❌ Descartadas — solo aplican a subconjuntos de agencias específicas (TLC, DOT), no son variables transversales |

**Por qué no todas las 44**: cargar columnas innecesarias aumenta el uso de RAM en ~30% adicional sin aportar valor analítico. El principio de parsimonia en la selección de variables es una práctica estándar de ingeniería de datos que además fuerza a explicitar qué preguntas se van a responder antes de procesar.

**Qué descartaría el profe si eligiera todas las 44**: que el analista no sabe distinguir entre datos disponibles y datos útiles — un error conceptual más que técnico.

---

### D2 · Carga por chunks en lugar de `pd.read_csv` directo

**Decisión**: iterar el CSV en chunks de 50,000 filas con `usecols` restringido.

**Por qué chunks**: el CSV completo ocupa varios GB en disco. Cargado íntegro con `pd.read_csv` sin parámetros, el DataFrame resultante supera los 4 GB en RAM solo con dtypes por defecto. En la mayoría de equipos locales con 8–16 GB de RAM disponible, esto agota la memoria y provoca un crash del kernel o swap masivo en disco.

**Por qué 50,000 y no otro tamaño**: es un compromiso entre overhead de I/O (chunks muy pequeños = muchas operaciones de lectura) y presión de memoria (chunks muy grandes = derrota el propósito). A 50,000 filas por chunk, la carga completa toma ~418 iteraciones y mantiene cada chunk bajo los 200 MB en RAM.

**Alternativa descartada — Dask o Polars**: ambas bibliotecas manejan datasets grandes de forma más eficiente, pero introducen una API diferente que no se usará en el resto del proyecto (Tableau recibe CSVs estándar). La consistencia de herramientas pesa más que la optimización de rendimiento en un contexto académico.

**`on_bad_lines='skip'`**: el CSV de NYC Open Data contiene ocasionalmente filas con comas dentro de campos no entrecomillados (principalmente en `Resolution Description`). En lugar de fallar en silencio o crashear, `skip` registra el comportamiento y permite continuar. Las filas saltadas son una fracción mínima del total.

---

### D3 · Mediana como medida central para `resolution_hours`

**Decisión**: usar mediana (p50 = 7.1 h) en lugar de media (211.6 h) al describir el tiempo de resolución.

**El problema con la media**: `resolution_hours` tiene una distribución fuertemente sesgada a la derecha. El p75 es 80.4 h, pero la media es 211.6 h — esto indica que una cola larga de casos extremadamente lentos (meses o más de un año) arrastra la media hacia arriba, haciéndola no representativa del caso típico.

```
Estadísticas reales de resolution_hours:
  p25  →   0.8 h   (cuartil inferior)
  p50  →   7.1 h   (mediana — caso típico)
  p75  →  80.4 h   (cuartil superior)
  mean → 211.6 h   (media — inflada por outliers)
  max  → 8760.0 h  (= 365 días, límite aplicado)
```

**Implicación para Tableau**: si se usa la media en un gráfico de barras de "tiempo de resolución por agencia", algunas agencias aparecerán con promedios de cientos de horas cuando en realidad su desempeño típico es razonable. Eso es una mentira visual. La mediana describe lo que le pasa al ciudadano promedio.

**Qué descartaría el profe si usara la media**: que el analista no exploró la distribución antes de elegir la medida de tendencia central — un error de EDA, no de código.

---

### D4 · Filtro geográfico: Latitud entre 40.4 y 41.0

**Decisión**: filtrar filas donde `Latitude` cae fuera del rango 40.4–41.0 antes de exportar para Tableau.

**Por qué ese rango**: los 5 boroughs de NYC ocupan aproximadamente entre 40.48° N (punta sur de Staten Island) y 40.92° N (norte del Bronx). El rango 40.4–41.0 añade un margen de ~0.1° en cada extremo para no excluir registros legítimos en los límites.

**Qué pasa si no se filtra**: Tableau Maps intentará colocar puntos con coordenadas (0, 0) (el Océano Atlántico frente a África) o valores claramente erróneos, distorsionando cualquier mapa de densidad o distribución espacial.

**Impacto del filtro**: se retienen 20,469,468 filas de 20,855,981 → 98.1%. El 1.9% descartado corresponde a registros sin coordenada (`Latitude` nula) o con valores fuera de rango, lo cual es consistente con el 1.9% de nulos observado en el perfil. El filtro no elimina datos válidos.

---

### D5 · Valores negativos en `resolution_hours`: exclusión, no imputación

**Decisión**: excluir los 46,334 registros con `resolution_hours < 0` en lugar de imputarlos.

**Por qué son negativos**: solo ocurren cuando `Closed Date < Created Date`, lo cual es un error de captura de datos, no un valor faltante. Imputarlos con la mediana sería introducir información falsa sobre cuándo se cerró un caso.

**Por qué no corregirlos**: no hay forma de saber cuál de las dos fechas es la correcta. Podría ser que `Created Date` está mal registrada, o que `Closed Date` lo está. Sin información adicional, cualquier corrección sería especulación.

**Impacto**: 46,334 / 20,855,981 = 0.22% del total — un volumen despreciable que no afecta las distribuciones ni las conclusiones analíticas.


---

## Etapa 02 · Limpieza de datos

### D6 · Tratamiento de nulos en `Borough`
**Decisión**: eliminar filas con `Borough` nulo (0.2% del total).  
**Por qué**: Borough es clave foránea del modelo estrella — sin Borough, la fila no puede relacionarse con `dim_geo` y queda huérfana en Tableau. Imputar un borough arbitrario introduciría error geográfico.

### D7 · Agrupación de `Problem` en 11 familias temáticas
**Decisión**: crear `problem_family` agrupando los 272 valores únicos de `Problem` en 11 categorías semánticas.  
**Alternativa descartada**: top-N por frecuencia.  
**Por qué**: top-N agrupa por popularidad, no por significado — Ruido nocturno y Ruido de construcción quedarían en grupos distintos aunque pertenecen a la misma familia. La agrupación semántica es defendible analíticamente; la frecuencial no lo es.

### D8 · Valores negativos en `resolution_hours`
**Decisión**: excluir registros con `Closed Date < Created Date`.  
**Por qué**: es un error de captura, no un valor faltante. Imputar sería introducir información falsa.

---

## Etapa 03 · Modelado de fuentes

### D9 · Modelo estrella vs tabla plana
**Decisión**: modelo estrella con `fact_311` + 4 dimensiones.  
**Por qué**: la tabla plana repite atributos de Borough, Agency y Problem en cada una de las 94,500 filas. El modelo estrella elimina esa redundancia, garantiza que Tableau no duplique métricas al hacer joins, y hace el pipeline auditable en Git.

### D10 · Agregaciones pre-calculadas en Python
**Decisión**: exportar `agg_borough_year`, `agg_resolucion_agencia`, `agg_hora`, `agg_familia_problema` como CSVs independientes.  
**Alternativa descartada**: campos calculados en Tableau.  
**Por qué**: los campos calculados de Tableau no se versionan en Git. Las agregaciones en Python son auditables, reproducibles y consistentes entre todas las vistas del workbook.

---

## Etapa 04 · Visualizaciones Tableau

> ⏳ **Pendiente**

Decisiones previstas a documentar:
- Tipo de gráfico elegido para cada pregunta analítica y alternativas descartadas
- Nivel de granularidad temporal (día vs semana vs mes)
- Paleta de colores y justificación de accesibilidad
- Estructura del dashboard (filtros, jerarquías, tooltips)