# E5 — Insights exploratorios

Proyecto: NYC 311 Analytics  
Entrega: 5 — Dashboard Alpha y Visualización Exploratoria  
Fecha: 2026-06-27

Pregunta analítica: ¿Qué patrones de quejas ciudadanas en NYC revelan ineficiencias operativas en la respuesta municipal, y cómo varían por tipo de problema y agencia?

---

## Insight 1 — La mayoría se resuelve rápido, pero 1 de cada 5 solicitudes supera los 7 días

**Observación:** De 20.8M de solicitudes, el 57.5% se resuelve en menos de 1 día (11.97M), mientras que el 19.8% tarda más de 7 días (4.13M). Solo el 9.4% cae en el rango intermedio de 3 a 7 días.

**Interpretación:** La distribución bimodal (muy rápido o muy lento) sugiere que el sistema 311 no tiene un problema generalizado de lentitud, sino un problema focalizado: existe un subconjunto estructural de solicitudes que sistemáticamente escapa a la resolución rápida. Esto no es ruido aleatorio — es un patrón que apunta a tipos de problemas o agencias específicas.

**Acción sugerida:** Identificar qué tipos de problemas concentran las 4.13M solicitudes con más de 7 días de resolución y si una o pocas agencias son responsables de ese rezago. Ese es el foco operativo.

**Evidencia:** Vista "E5 - Distribución SLA"

---

## Insight 2 — Ruido y Tráfico concentran el 40% de la demanda, pero no son los más lentos

**Observación:** Las familias "Ruido" (22.8%) y "Tráfico / Estacionamiento" (17.5%) representan el 40.3% de todas las solicitudes. Sin embargo, en el scatter de agencias, NYPD — responsable de la mayoría de estas quejas — aparece con tiempo de resolución promedio cercano a 0 horas a pesar de manejar ~9M de solicitudes.

**Interpretación:** Alta demanda no implica baja eficiencia. NYPD gestiona el mayor volumen del sistema y lo resuelve casi de inmediato, lo que sugiere que tiene protocolos de cierre rápido para quejas de ruido y tráfico. El problema de lentitud está en otro segmento del sistema.

**Acción sugerida:** Las agencias con alto volumen y baja latencia como NYPD pueden servir de referencia metodológica para agencias con bajo volumen y alta latencia. Investigar qué tipo de cierre/resolución usan.

**Evidencia:** Vistas "E5 - Comparación por familia" + "E5 - Relación volumen vs SLA"

---

## Insight 3 — EDC y DPR combinan bajo volumen con tiempos de resolución extremos

**Observación:** EDC (Economic Development Corporation) registra aproximadamente 8,000 horas de tiempo promedio de resolución con un volumen bajo de solicitudes. DPR (Parks & Recreation) presenta ~4,500 horas con volumen moderado (~1M). Ambas agencias aparecen como outliers claros en el scatter.

**Interpretación:** Estas agencias no están dimensionadas para cerrar solicitudes con la rapidez que el sistema 311 supone. Sus tiempos de resolución extremos pueden deberse a la naturaleza de los problemas que atienden (infraestructura, proyectos de largo plazo) o a falta de protocolos de cierre. En cualquier caso, concentran una parte desproporcionada del rezago total del sistema.

**Acción sugerida:** Revisar si los tipos de problemas asignados a EDC y DPR corresponden a proyectos que por naturaleza no pueden cerrarse en días (en cuyo caso el 311 los está categorizando mal), o si hay un problema de gestión interna que puede corregirse.

**Evidencia:** Vista "E5 - Relación volumen vs SLA"

---

## Insight 4 — "Otros" es la categoría más grande y eso es en sí un problema de datos

**Observación:** La familia de problema "Otros" representa el 36% de todas las solicitudes — más que Ruido (22.8%) y Tráfico (17.5%) combinados. Es la categoría dominante por un margen amplio.

**Interpretación:** Una categoría residual que agrupa más de un tercio de las solicitudes indica una limitación estructural en el sistema de clasificación del 311. O bien muchos tipos de quejas no tienen categoría asignada, o la taxonomía no está actualizada con los problemas reales que reportan los ciudadanos. Esto reduce la utilidad analítica del dataset para identificar problemas específicos.

**Acción sugerida:** Para E6, investigar qué tipos de quejas concretas componen "Otros" usando el campo `Problem` (nivel granular). Esto permitirá segmentar mejor y posiblemente revelar familias emergentes no capturadas por la clasificación actual.

**Evidencia:** Vista "E5 - Comparación por familia"

---

## Notas para la exposición

El guion de presentación vive en el repositorio de documentación (`nyc-311-analytics-docs/guias/`), no en este repo de código.
