# Script de exposición — Entrega 5

Tiempo total: 2 minutos  
Formato: 1 minuto contexto + 1 minuto dashboard

---

## MINUTO 1 — Contexto

*[Mostrar el dashboard en pantalla, sin hacer zoom todavía]*

"El proyecto analiza **20.8 millones de solicitudes ciudadanas** del sistema 311 de Nueva York entre 2020 y 2025.

La pregunta que guía el análisis es: **¿qué patrones de quejas revelan ineficiencias en la respuesta municipal?**

El dataset tiene dimensiones temporales, geográficas y operativas — agencias, tipos de problemas, tiempos de resolución. Para esta entrega construimos tres visualizaciones exploratorias que cubren comparación, distribución y relación."

---

## MINUTO 2 — Dashboard: insights y acción sugerida

*[Señalar cada vista al mencionarla]*

"**Primer hallazgo** *(señalar distribución SLA)*: el sistema resuelve el 57% de los casos en menos de un día — eso es eficiente. Pero el **20% tarda más de 7 días**. Son 4 millones de solicitudes con rezago estructural.

**Segundo hallazgo** *(señalar scatter)*: NYPD maneja 9 millones de quejas y las resuelve casi de inmediato. EDC, en cambio, tiene pocas quejas pero **8,000 horas de resolución promedio**. Alto volumen no significa baja eficiencia — el problema está focalizado en agencias específicas.

**Tercer hallazgo** *(señalar comparación)*: Ruido y Tráfico concentran el 40% de la demanda. Pero la categoría más grande es 'Otros' con el 36% — lo que revela una **limitación en la taxonomía del propio sistema 311**.

**Conclusión y acción sugerida:** El 311 no tiene un problema generalizado de lentitud — tiene un problema focalizado en EDC, DPR y en solicitudes sin clasificar. La recomendación es auditar las categorías residuales e implementar SLAs diferenciados por tipo de problema."

---

## Notas de presentación

- Hablar despacio en el minuto 1 — el contexto se tiende a apresurar
- En el minuto 2, señalar físicamente cada vista antes de mencionarla
- Si el profe interrumpe con preguntas: los datos exactos están en `e5-insights-exploratorios.md`
- No leer el script — usarlo solo como guía de estructura
