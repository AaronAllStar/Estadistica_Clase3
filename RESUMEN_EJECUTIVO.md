# Reporte de Storytelling de Datos: Retencion y Riesgo Academico
**Oficina de Ingenieria de Datos y Retencion Estudiantil**

En base al analisis del conjunto de datos institucional de 800,000 registros de estudiantes (ulead_visualizacion_800k.csv), se presentan los siguientes dos storytelling analiticos estructurados para guiar las decisiones de retencion academica.

---

## Storytelling 1: Modalidad y Retencion Academica

### 1. ¿Que problema estamos intentando resolver?
El objetivo es identificar los factores criticos que determinan que un estudiante sea clasificado en Riesgo Academico Alto. Con este entendimiento, la institucion puede optimizar el despliegue de recursos de tutoria y apoyo academico de manera proactiva, previniendo la reprobacion y la desercion escolar.

### 2. ¿Que patron importante aparecio?
El analisis de los datos revela que la modalidad de estudio es la variable mas determinante del riesgo academico:
* **Riesgo por Modalidad:**
  - Presencial: El riesgo academico alto es de solo el 5.44%.
  - Virtual: El riesgo academico alto asciende al 12.93% (un incremento de mas del doble).
  - Hibrida: El riesgo academico alto se situa en el 12.75%.
* **Concentracion del Riesgo:** El 82.44% de todos los alumnos de la institucion clasificados en riesgo alto cursan bajo modalidades virtuales o hibridas.
* **Variable de Comportamiento Critica:** La asistencia promedio de los alumnos en riesgo alto en las modalidades virtual e hibrida se desploma a ~60.5%, en contraste con el ~85.0% observado en los alumnos de bajo riesgo.
* **Factores no Influyentes:** El estatus laboral (trabajar o no) y las horas de estudio declaradas por semana no muestran diferencias estadisticamente significativas entre los distintos niveles de riesgo.

### 3. ¿Que grafico o metrica respalda el hallazgo?
* **Distribucion de Riesgo por Modalidad:**
  - Presencial: 72.90% Bajo, 21.66% Medio, 5.44% Alto
  - Hibrida: 50.96% Bajo, 36.29% Medio, 12.75% Alto
  - Virtual: 50.69% Bajo, 36.38% Medio, 12.93% Alto
* **Matriz de Correlacion:**
  - La entrega de tareas es la variable con mayor correlacion conductual positiva con la nota final (coeficiente de 0.31).
  - La asistencia muestra una correlacion directa positiva con la nota final (coeficiente de 0.22).

### 4. ¿Por que importa?
Los resultados modifican la hipotesis de la institucion respecto a la educacion en linea. El bajo rendimiento en entornos virtuales o hibridos no se debe a la falta de tiempo de estudio o al empleo del estudiante, sino a la falta de compromiso y desenganche de asistencia en la virtualidad. Esto exige centrar las estrategias de retencion en el control de asistencia y alertas tempranas en lugar de simplificar el contenido academico.

### 5. ¿Que recomendacion harian a ULEAD con base en los datos?
Se sugieren tres acciones inmediatas:
1. **Implementar el Sistema de Alertas Tempranas de Asistencia (SATA):** Activar notificaciones automaticas cuando un estudiante de modalidad virtual o hibrida registre una asistencia inferior al 75% en las primeras tres semanas del ciclo.
2. **Rediseño de Clases Virtuales e Hibridas:** Incorporar actividades síncronas que requieran participacion y verificacion activa del estudiante en la plataforma.
3. **Focalizacion Presupuestaria:** Asignar el 80% de los recursos de tutoria a estudiantes en modalidades no presenciales, dado que representan el 82.44% de la poblacion en riesgo.

---

## Storytelling 2: Brecha Academica del Estudiante Trabajador

### 1. ¿Que problema estamos intentando resolver?
Mitigar la brecha de rendimiento escolar y optimizar el promedio de calificacion final del segmento de estudiantes que trabajan, quienes promedian notas inferiores y muestran mayor dispersion en sus resultados.

### 2. ¿Que patron importante aparecio?
El estado laboral del alumno es la variable mas determinante del promedio de calificaciones de la nota final:
* **Brecha de Calificaciones:**
  - Estudiantes que no trabajan: Promedio de nota final de 96.32 (Std de 5.32).
  - Estudiantes que si trabajan: Promedio de nota final de 89.37 (Std de 7.99).
* **Brecha Neta:** Existe una brecha directa de 6.95 puntos porcentuales de rendimiento en detrimento de los estudiantes que trabajan.
* **Variabilidad:** Los estudiantes que trabajan muestran una desviacion estandar mucho mayor, reflejando una alta inestabilidad en sus notas.

### 3. ¿Que grafico o metrica respalda el hallazgo?
* **Diagrama de Caja Comparativo (Boxplot):** Ilustra visualmente la caida de los limites de percentiles (primer, segundo y tercer cuartil) para el grupo de estudiantes que trabajan, ademas de la dispersion de datos atipicos en el limite inferior.

### 4. ¿Por que importa?
Demuestra que la doble jornada de combinar el trabajo y el estudio impacta de forma negativa y directa el rendimiento academico global de los alumnos. Esta reduccion en el promedio afecta directamente su permanencia, renovacion de becas y egreso, a pesar de que el analisis muestra que reportan horas de estudio semanales similares al resto.

### 5. ¿Que recomendacion harian a ULEAD con base en los datos?
Se proponen las siguientes acciones de integracion:
1. **Politica de Gracia Automatica:** Otorgar una extension de gracia automatica de 48 horas para la entrega de tareas a estudiantes con estado de trabajo certificado.
2. **Materiales y Soporte Asincrono:** Habilitar canales de tutoria los fines de semana y asegurar que todas las clases sincronas cuenten con grabaciones completas en el LMS.
3. **Modalidades de Evaluacion Flexibles:** Implementar formatos de evaluacion basados en proyectos de aplicacion practica laboral que permitan a los alumnos capitalizar su experiencia de trabajo.
