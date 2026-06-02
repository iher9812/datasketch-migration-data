# Metodología Interseccional para Análisis de Datos Sociales

## ¿Qué es la interseccionalidad en datos?

Concepto acuñado por Kimberlé Crenshaw (1989): las identidades sociales (género, raza,
clase, discapacidad, orientación sexual, territorio) no operan de forma aislada sino que
se superponen y crean experiencias únicas de privilegio y opresión. En datos, esto significa
que "las mujeres" no es una categoría homogénea — una mujer indígena rural enfrenta una
combinación diferente de barreras que una mujer blanca urbana.

---

## Niveles de análisis interseccional

### Nivel 1: Desagregación básica
Solo por una variable (sexo, raza, etc.). Es el mínimo aceptable pero insuficiente.

```
Ejemplo: % de empleo informal por sexo
Hombres: 42%  |  Mujeres: 58%
→ Muestra brecha, pero no explica qué mujeres ni por qué
```

### Nivel 2: Desagregación cruzada (2 variables)
Más informativo, permite ver cómo interactúan dos ejes de desigualdad.

```
Ejemplo: % de empleo informal por sexo × nivel educativo
              Sin estudios  Primaria  Secundaria  Superior
Hombres:         72%          55%        38%        18%
Mujeres:         89%          71%        52%        24%
→ La brecha de género persiste en todos los niveles pero varía
```

### Nivel 3: Análisis interseccional completo (3+ variables)
Ideal cuando el dataset lo permite. Revela concentración de desventajas.

```
Ejemplo: % sin acceso a salud reproductiva por sexo × etnicidad × zona
              Indígena rural  Indígena urbana  No-indígena rural  No-indígena urbana
Mujeres:          87%              61%               43%                19%
→ La combinación de ser mujer + indígena + rural concentra la máxima desventaja
```

---

## Matriz de Dominación (Patricia Hill Collins)

Para identificar qué ejes de poder están operando en un dataset, usar esta grilla:

| Eje de poder | Variables de datos asociadas |
|---|---|
| Género/sexo | Sexo, identidad de género, estado civil |
| Raza/etnicidad | Autoidentificación, lengua materna, comunidad de origen |
| Clase social | Decil de ingreso, nivel educativo, tipo de ocupación |
| Edad | Grupos etarios, ciclo de vida |
| Territorio | Región, rural/urbano, marginalidad geográfica |
| Discapacidad | Tipo y grado de discapacidad |
| Orientación sexual | Cuando disponible (poco frecuente en encuestas masivas) |

---

## Protocolo de auditoría de sesgos en datasets

### Sesgos en recolección
- **Sesgo de cobertura**: ¿quién quedó fuera de la muestra? (personas sin hogar, sin acceso digital, en instituciones)
- **Sesgo de respuesta diferencial**: ¿algunos grupos responden menos? ¿por miedo, desconfianza, barreras lingüísticas?
- **Sesgo de encuestador/a**: ¿el género/raza del encuestador afecta las respuestas?

### Sesgos en categorización
- **Binarios de género**: encuestas que solo ofrecen M/F excluyen personas no binarias y trans
- **Categorías raciales impuestas**: clasificaciones que no coinciden con autoidentificación
- **Agregación problemática**: "América Latina" como categoría homogénea oculta diferencias nacionales enormes

### Sesgos en análisis
- **Falacia ecológica**: inferir comportamiento individual de datos grupales
- **Variable omitida**: ignorar factores de confusión que explican diferencias observadas
- **Normalización del grupo dominante**: comparar todo contra el "promedio" que en realidad es el grupo mayoritario

---

## Técnicas estadísticas recomendadas

### Para describir brechas
- **Diferencia absoluta**: valor_grupo_A − valor_grupo_B
- **Ratio de paridad**: valor_grupo_A / valor_grupo_B (1.0 = paridad)
- **Índice de disimilitud**: mide segregación entre grupos (0=integración total, 1=segregación total)

### Para analizar interseccionalidad
- **Regresión con interacciones**: incluir términos de interacción (sexo × raza, sexo × clase)
- **Análisis de subgrupos**: estimar efectos separadamente para cada intersección
- **Decomposición de Oaxaca-Blinder**: descompone brechas en parte "explicada" e "inexplicada"

### Para datos cualitativos mezclados con cuantitativos
- **Triangulación**: corroborar patrones estadísticos con testimonios
- **Análisis temático sensible al género**: codificar testimonios con categorías informadas por teoría feminista
- **Contar lo que no se puede medir**: documentar qué fenómenos importantes quedan fuera de los datos disponibles

---

## Visualización feminista de datos

### Principios de diseño (basados en D'Ignazio & Klein cap. 3)

1. **Nombra la desigualdad**: los títulos deben comunicar el hallazgo, no solo describir la variable
2. **Muestra la varianza**: evita solo mostrar promedios; usa boxplots, distribuciones, intervalos de confianza
3. **Incluye el n**: siempre muestra el tamaño de muestra por subgrupo
4. **Anota el contexto**: una nota al pie con factores explicativos convierte un gráfico en argumento
5. **Cuida los colores**: no usar rojo/azul para mujer/hombre — refuerza binarios y estereotipos
6. **Accesibilidad**: paletas daltónicas, texto alternativo, contraste adecuado

### Tipos de gráfico recomendados por tipo de análisis

| Análisis | Tipo de gráfico recomendado |
|---|---|
| Brecha entre dos grupos | Lollipop chart o barras con línea de paridad |
| Evolución temporal de brecha | Líneas dobles con área sombreada = brecha |
| Interseccionalidad (3+ grupos) | Heatmap o small multiples |
| Distribución dentro de grupos | Violin plot o ridgeline |
| Geografía de desigualdad | Mapa coroplético desagregado |
| Comparación múltiple | Slope chart (antes/después) |
