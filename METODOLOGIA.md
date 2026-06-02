# Metodología — Panorama de la bancarización de las mujeres migrantes en Colombia (2025)

> Diseño de investigación con enfoque de **feminismo de datos** (D'Ignazio & Klein, 2020) y **metodología interseccional** (Crenshaw, 1989; Hill Collins).
> Versión 1.0 · Junio 2026 · Proyecto `datasketch-migration-data`

---

## 0. Por qué este documento (y qué corrige)

El primer notebook intentó medir bancarización directamente desde la GEIH y produjo resultados **no válidos**. La auditoría (red team) encontró que:

1. **La GEIH no tiene módulo de inclusión financiera.** Las variables `P5222` del módulo de vivienda que se usaron **no son productos financieros** sino formas de pago (la subvariable de texto contiene "EFECTIVO", "CRÉDITO POR LIBRANZA"). Solo 0,9 % de hogares figuraba con "cuenta de ahorro" frente al ~96 % nacional: imposible.
2. La pregunta era de **hogar**, no de persona → medir "brecha por sexo" con ella es **falacia ecológica** (hombres y mujeres comparten hogar; la diferencia observada fue de 0,5 pp, puro ruido de composición).
3. No se usó el **factor de expansión** (`FEX_C18`), se incluyeron **menores de edad**, se confundió **"No" con dato faltante**, y se mapeó mal el **urbano/rural** (se usó `AREA`, que es código de ciudad; el correcto es `CLASE`).

**Conclusión de diseño:** la bancarización de mujeres migrantes **no puede medirse con una sola fuente**. Esta metodología adopta un **diseño mixto y triangulado** (Principio 5 — *Abrazar el pluralismo*): la GEIH aporta el **perfil sociodemográfico-laboral y proxies de vulnerabilidad** del lado de la **demanda**; las fuentes administrativas y los estudios académicos aportan las **tasas y barreras reales** de inclusión financiera. El "panorama" nace del cruce de ambas, no de un único dato.

---

## 1. Marco teórico: los 7 principios aplicados a este proyecto

| Principio | Cómo se aplica aquí |
|---|---|
| 1. Examinar el poder | Preguntar quién produce cada dato (DANE, Superfinanciera, academia) y a quién deja fuera (irregulares, sin teléfono, sin hogar). |
| 2. Desafiar el poder | No describir la exclusión como "característica" de las migrantes, sino nombrar las **barreras estructurales** (documentación, xenofobia, autoexclusión). |
| 3. Elevar emoción y corporalidad | Integrar testimonios y hallazgos conductuales del estudio CEDE/IPA (miedo al rechazo, autoexclusión) junto a las cifras. |
| 4. Repensar binarios | Declarar que el sexo en GEIH es binario (M/F) e invisibiliza a personas trans/no binarias; no naturalizar "informal/formal". |
| 5. Abrazar el pluralismo | **Triangular** GEIH + fuentes de oferta + estudios cualitativos. Ninguna fuente sola cuenta la historia. |
| 6. Considerar el contexto | Fechar y contextualizar cada cifra (mes de la GEIH, año de la regularización PPT/PEP, política migratoria vigente). |
| 7. Hacer visible el trabajo | Documentar cada decisión de limpieza/operacionalización; acreditar al DANE y a los equipos de investigación citados. |

---

## 2. Pregunta de investigación y objetivos

**Pregunta general:**
¿Cuál es el panorama de la inclusión financiera de las mujeres migrantes (mayoritariamente venezolanas) en Colombia en 2025, y cómo se diferencia según los ejes interseccionales de origen, edad, etnia, clase y territorio?

**Objetivo general:** construir un panorama triangulado de la bancarización de mujeres migrantes que combine perfil de demanda (GEIH), oferta financiera (datos administrativos) y barreras (evidencia académica).

**Objetivos específicos:**
1. Caracterizar interseccionalmente a la población de mujeres migrantes en Colombia con la GEIH 2025 (12 meses, ponderada).
2. Construir **proxies de vulnerabilidad financiera** desde la GEIH (informalidad laboral, no afiliación a seguridad social, ingresos, jefatura de hogar, trabajo de cuidado).
3. Estimar **brechas** mujer migrante vs. mujer nacida en Colombia vs. hombre migrante en esos proxies, con índice de paridad.
4. Triangular con fuentes de oferta (SFC, RIF, Findex) y estudios (CEDE/IPA) para situar las tasas y barreras reales de bancarización.
5. Identificar y nombrar las **brechas de datos** (qué no se puede medir y por qué eso también es un hallazgo).

---

## 3. Definiciones operativas (decididas y justificadas)

| Concepto | Definición operativa | Fuente / variable |
|---|---|---|
| **Mujer** | `P3271 == 2` (sexo registrado en GEIH; binario, ver límite F2). | F1 — Características generales |
| **Migrante internacional** | Nacida en otro país: `P3373 == 3`. País de nacimiento: `P3373S3` (862=Venezuela). **No** equivale a estatus migratorio. | F6 — Migración |
| **Población de interés** | Mujer migrante **adulta** (`P6040 >= 18`) — la inclusión financiera se define para adultos. | F1 |
| **Grupos de comparación** | (a) Mujer nacida en Colombia, (b) Hombre migrante, (c) Hombre nacido en Colombia. | F1 + F6 |
| **Bancarización / inclusión financiera** | Medida directamente via **join EPM Ronda VIII × GEIH** (`src/02_join_epm.py`). Variable `pd1` (1=tiene al menos 1 producto formal). Complementada con benchmarks externos (SFC, RIF, Findex, CEDE/IPA). | EPM Ronda VIII + Ver §5 |
| **Proxies de vulnerabilidad financiera (GEIH)** | Informalidad laboral, no cotización a pensión, no afiliación a salud contributiva, ingresos bajos, jefatura femenina del hogar, dedicación a trabajo de cuidado no remunerado. | Ocupados, Fuerza de trabajo, Otros ingresos, Otras formas de trabajo, F1 |
| **Clase** | Estrato (`P4030S1A1`), ingresos (módulo Otros ingresos), nivel educativo (`P3042`), informalidad. | F7 + módulos laborales |
| **Etnia** | Autorreconocimiento `P6080`. | F1 |
| **Territorio** | Departamento de residencia (`DPTO`) y **urbano/rural = `CLASE`** (1=cabecera, 2=rural). **No usar `AREA`.** | F1 |
| **Ponderación** | Todas las estimaciones usan el factor de expansión `FEX_C18`. El panel apila 11 meses **sin re-escalar** los pesos: el total ponderado (~8.8M) es un **flujo de personas-mes**, no un stock poblacional. Para comparar con estadísticas nacionales usar la estimación mensual (~800k personas/mes = total/11). | todos los módulos |

---

## 4. Inventario de datos disponibles

### 4.1 GEIH 2025 — DANE (fuente primaria, lado demanda)

- **Cobertura temporal:** 12 meses completos, enero–diciembre 2025 → permite **serie mensual** y análisis de estacionalidad/tendencia.
- **Ubicación:** `Data/<Mes> 2025/{CSV,DTA,SAV}/`. Se usa **CSV** (sep `;`, encoding `latin-1`).
- **8 módulos por mes** (los 5 en negrita son los que esta metodología incorpora; el notebook original solo usaba los 3 primeros):
  - **Características generales, seguridad social en salud y educación** (F1) — sexo, edad, educación, etnia, afiliación a salud, territorio.
  - **Migración** (F6) — lugar de nacimiento, país, año/mes de llegada, tiempo en Colombia.
  - **Datos del hogar y la vivienda** (F7) — estrato, tenencia, tamaño del hogar.
  - **Ocupados** — ocupación, tipo de contrato (`P6440`), formalidad → **informalidad laboral**.
  - **Otros ingresos e impuestos** — ingresos (`P7500…`) → **clase / suficiencia económica**.
  - **Otras formas de trabajo** — **trabajo de cuidado y doméstico no remunerado** (núcleo del análisis feminista).
  - Fuerza de trabajo · No ocupados — situación laboral / inactividad.
- **Advertencias técnicas:** nombres de archivo con **espacios no separables (NBSP)** → localizar por palabra clave, no por nombre literal. Llaves: persona = `DIRECTORIO+SECUENCIA_P+ORDEN`; hogar = `DIRECTORIO+SECUENCIA_P(+HOGAR)`.

### 4.2 Lo que la GEIH NO tiene (y cómo se resuelve)

| Limitación | Solución implementada |
|---|---|
| No mide tenencia/uso de productos financieros | **Resuelta:** join EPM Ronda VIII (`src/02_join_epm.py`) aporta `bancarizado`, tipo de producto y barreras a nivel de microdato |
| No capta estatus migratorio PPT/PEP/irregular | **Pendiente:** fuente alternativa Migración Colombia OM3 |
| No incluye población sin hogar ni en instituciones | **Brecha declarada** (sesgo de cobertura — Principio 1): las más excluidas son las menos observadas |

---

## 5. Las tres investigaciones `.md`: qué son y cómo se vinculan al proyecto

El usuario incorporó tres documentos en `Data/`. Cumplen funciones **distintas y complementarias** dentro del diseño:

| Archivo | Qué es | Rol metodológico | Cómo se vincula |
|---|---|---|---|
| `compass_artifact_..._markdown.md` | **Catálogo de fuentes** de datos y reportes (SFC, RIF, EPM, Findex, OIT, R4V, Migración Colombia). | **Mapa de la capa de oferta** y de triangulación. Define de dónde sacar las tasas de bancarización que la GEIH no da. | Se convierte en el **registro de fuentes** (`docs/fuentes.md`): cada fila → un dato a descargar (RIF 2024, EPM ronda VIII, Findex 2025, tablero SFC). |
| `fuente1.md` | **Paper académico CEDE 2024‑48** (Barboni, de Roux, Pérez‑Cardona): experimento con migrantes venezolanos sobre aceptación social percibida e inclusión financiera. | **Evidencia causal y de barreras conductuales** (autoexclusión, percepción). Capa cualitativa/explicativa (Principios 2, 3, 6). | Aporta el **marco interpretativo** de las brechas y las cifras de barreras (p. ej. 66 % subestima la apertura de los colombianos). Se cita en la narrativa, no se "cruza" estadísticamente. |
| `inclusion-financiera-migrantes-venezolanos-colombia.md` | **Brief del estudio IPA** (versión divulgativa del anterior + diagnóstico, 8.200 migrantes). | **Datos de demanda específicos de migrantes** con representatividad por género. | Fuente de **cifras de contraste** (24 % pierde productos al migrar; pérdidas mayores en mujeres; billeteras digitales como puerta de entrada; 41 % cree que el banco no le atenderá). Triangula los proxies de la GEIH. |

**Mecanismo de vinculación (3 niveles):**

1. **Documental** — crear `docs/fuentes.md` que normalice las tres en una tabla con: fuente, tipo (oferta/demanda/cualitativa), variable que aporta, desagregación por género, año, URL, y "qué hueco de la GEIH llena".
2. **Cuantitativo (implementado)** — la **EPM Ronda VIII** del DANE fue descargada y procesada via `src/02_join_epm.py`. El join `DIRECTORIO+SECUENCIA_P+ORDEN` produce 595 mujeres migrantes adultas con perfil GEIH completo + bancarización real medida. Hallazgos: 21.5% bancarización formal, 56.2% con giros/remesas, barreras 88% conductuales.
3. **Interpretativo** — los hallazgos del CEDE/IPA se usan como **anotaciones de contexto** en cada visualización y como hipótesis explicativas de las brechas observadas en los proxies (Principio 6).

---

## 6. Diseño metodológico: triangulación en tres capas

```
                 PANORAMA DE BANCARIZACIÓN DE MUJERES MIGRANTES
                                     │
        ┌────────────────────────────┼────────────────────────────┐
   CAPA A: DEMANDA              CAPA B: OFERTA               CAPA C: BARRERAS
   (perfil + vulnerabilidad)    (acceso real a productos)    (por qué / contexto)
   ─ GEIH 2025 (12 meses)       ─ SFC Estadísticas Dinám.    ─ CEDE 2024-48 (fuente1)
   ─ ponderada FEX_C18          ─ RIF 2024 / Banca Oport.    ─ IPA brief
   ─ proxies: informalidad,     ─ Global Findex 2025         ─ OIT, R4V (compass)
     ingresos, cuidado, etnia   ─ EPM (puente microdato)
                                     │
                          Indicadores + brechas + índice de paridad
                                     │
                          Narrativa feminista + visualización
```

La GEIH responde **"quiénes son y qué tan vulnerables están"**; la oferta responde **"a cuántas llega el sistema financiero"**; las barreras responden **"por qué no llega"**. El panorama es la integración honesta de las tres.

---

## 7. Plan de análisis por fases

| Fase | Descripción | Estado | Script / Notebook |
|---|---|---|---|
| 0 | Inventario y auditoría feminista del dataset | ✓ Completada | `src/00_inventario.py` |
| 1 | Consolidación panel GEIH 2025 (11 meses × 6 módulos) | ✓ Completada | `src/01_consolidacion_panel.py` |
| 2 | Join EPM Ronda VIII × GEIH — bancarización real | ✓ Completada | `src/02_join_epm.py` |
| 3 | Caracterización interseccional de mujeres migrantes | ✓ Completada | notebook §3 |
| 4 | Proxies de vulnerabilidad financiera (GEIH, ponderados) | ✓ Completada | notebook §4-5 |
| 5 | Bancarización real: productos, barreras, perfil (EPM VIII) | ✓ Completada | notebook §6 |
| 6 | Regresión logística: predictores de bancarización | ✓ Completada | notebook §6b |
| 7 | Triangulación con benchmarks externos (IPA, CEDE, RIF) | ✓ Completada | notebook §7 |
| 8 | Exportar figuras y producir entregable final | ⏳ Pendiente | — |

### Hallazgos principales (resumen ejecutivo)

- **Población:** ~8.8M mujeres migrantes adultas ponderadas; 97% venezolanas; 89.5% en cabeceras urbanas.
- **Bancarización real (EPM VIII, n=595):** 21.5% tiene producto formal. El producto más usado es giros/remesas (56%) — no cuentan como "formal".
- **Barrera principal:** conductual (88%), no documental (12%). El 48.6% dice "no necesita", que encubre desconfianza y falta de información.
- **Proxy más discriminatorio:** exclusión de salud contributiva — 28.4% de mujeres migrantes vs. 2.1% de mujeres locales (+26 pp).
- **Carga de cuidado:** 8.2 h/día vs. 7.2 h/día de mujeres locales — mayor trabajo invisible.

### Detalle de fases completadas

**Fase 0:** `src/00_inventario.py` — audita 12 meses × 8 módulos; genera `outputs/inventario_geih_2025.csv`. Detecta NBSP en 4 módulos; `lib_geih.buscar_csv()` los maneja automáticamente.

**Fase 1:** `src/01_consolidacion_panel.py` — une F1 ← F6 ← Ocupados ← Ingresos ← Cuidado ← F7 por mes; apila 11 meses disponibles. Output: `outputs/panel_geih_2025.parquet` (749k filas × 60 cols) y `outputs/mujeres_migrantes_adultas.parquet` (11,163 filas).

**Fase 2:** `src/02_join_epm.py` — join EPM VIII (`Data/EPM8_Personas/EPM8_Personas.csv`) con panel GEIH via `DIRECTORIO+SECUENCIA_P+ORDEN`. Match: 1,208 personas (16%), de las cuales 595 son mujeres migrantes adultas. Output: `outputs/bancarizacion_mm.parquet`.

**Fases 3-7:** `analisis_bancarizacion_mujeres_migrantes.ipynb` — 8 secciones ejecutadas con outputs embebidos.

---

## 8. Indicadores y métricas clave

| Indicador | Cálculo | Lectura feminista |
|---|---|---|
| Tasa de informalidad | % ocupadas sin cotización/contrato, ponderado | Proxy de barrera de acceso (sin soporte de ingresos formal) |
| Brecha absoluta | tasa(grupo A) − tasa(grupo B), en pp | Magnitud de la desigualdad |
| Índice de paridad | tasa(mujer migrante) / tasa(hombre local) | 1,0 = paridad; <1 = desventaja |
| Carga de cuidado | horas medias de trabajo no remunerado por sexo×origen | Hace visible el trabajo invisibilizado |
| Missing diferencial | % sin dato por subgrupo | La ausencia como evidencia de exclusión |
| Bancarización (externo) | de RIF/Findex/IPA, desagregado por sexo×origen | Tasa real de acceso, vía triangulación |

---

## 9. Cruces interseccionales priorizados

- **Nivel 1:** indicador × sexo; indicador × origen (migrante/local).
- **Nivel 2:** indicador × sexo × origen; × sexo × edad; × sexo × educación.
- **Nivel 3:** indicador × sexo × territorio (urbano/rural, departamento); × sexo × etnia; × sexo × estrato.
- **Triple:** mujer × migrante × (rural | étnica | sin afiliación) → concentración de desventaja.
- **Temporal:** evolución mensual 2025 de las brechas (¿se amplían o cierran?).

---

## 10. Limitaciones y consideraciones metodológicas

Estas limitaciones son parte integral de los resultados, no notas al pie. Declararlas es rigor metodológico (Principio 1 — Examinar el poder).

**L1 — Sesgo de cobertura estructural (las más excluidas son invisibles)**
La GEIH y la EPM solo capturan personas en hogares con dirección fija. Las mujeres migrantes en albergues, en situación de calle o sin domicilio estable no aparecen en ninguna fuente. Son exactamente las más excluidas financieramente. La tasa de bancarización observada (21.5%) es un **límite superior optimista** — la población real más vulnerable es inobservable con estos instrumentos. Alternativa: OIM DTM / R4V GIFMM JNA.

**L2 — Binarismo de sexo (P3271 invisibiliza personas trans y no binarias)**
La variable P3271 es binaria (1=Hombre, 2=Mujer). Personas trans, no binarias e intersex son completamente invisibles. No es un dato faltante corregible — es un déficit de diseño del instrumento DANE. Alternativa: no existe fuente pública representativa en Colombia.

**L3 — Sesgo de deseabilidad social en barreras autodeclaradas**
El 48.6% declara "no necesitar" producto financiero, lo que puede enmascarar miedo a discriminación, desconocimiento o vergüenza. Las barreras son autopercibidas bajo condiciones de entrevista. La clasificación "88% conductual / 12% documental" es una hipótesis plausible, no causa establecida. Adicionalmente, las etiquetas de `pd5` son asumidas — verificar contra cuestionario DANE (ver `docs/pendientes_verificacion.md`). Alternativa: diseño experimental (CEDE 2024-48).

**L4 — Submuestra EPM no demostrada representativa (16% match)**
Solo el 16% de la EPM VIII hizo match con el panel GEIH. Las 595 mujeres migrantes matcheadas corresponden a enero–mayo 2025 y a hogares que aparecen en ambas fuentes. El balance test en `src/02_join_epm.py` es limitado — no puede comparar características GEIH de las no matcheadas. Los resultados EPM son indicativos, no representativos. Alternativa: unir rondas EPM I–VIII para mayor n y cobertura temporal.

**L5 — Diseño observacional: asociaciones, no causas**
Todos los análisis son transversales y observacionales. Los coeficientes de la regresión logística miden asociación estadística, no efecto causal. Alternativa: diseño cuasi-experimental (instrumento, diferencia en diferencias).

**L6 — Riesgo de uso adverso de datos geográficamente desagregados**
Resultados que identifican concentraciones de mujeres migrantes sin bancarización en departamentos específicos pueden usarse para fines no previstos en contextos de tensión migratoria. Recomendación: suprimir celdas con n<30 antes de publicar; anonimizar datasets compartidos.

**L7 — Denominador de productos EPM (corrección aplicada)**
Las variables `pd3__N` (tipo de producto) solo se preguntan a personas bancarizadas (`pd1==1`). Las personas sin producto tienen `NaN`. La función `pandas.mean()` excluye NaN, lo que inflaría los porcentajes si se calcularan como `mean() * 100`. Este error fue identificado en revisión Red Team y corregido en `src/02_join_epm.py`: ahora se reportan dos métricas explícitas — "% de bancarizadas" (denominador n=128) y "% del total MM" (denominador n=595).

**L8 — Etiquetas pd5 asumidas sin cuestionario verificado**
Las etiquetas de barreras (`ETIQUETAS_PD5` en `src/02_join_epm.py`) fueron asignadas por contexto sin verificar contra el cuestionario oficial DANE EPM Ronda VIII. Si las etiquetas son incorrectas, la clasificación de barreras cambia. Ver `docs/pendientes_verificacion.md` para lista completa de asunciones pendientes.

---

## 11. Consideraciones éticas

- Datos sensibles (migración, etnia): no producir desagregaciones que permitan reidentificar o estigmatizar comunidades pequeñas; suprimir celdas con n muy bajo.
- Lenguaje que preserve la dignidad: "personas/mujeres migrantes", nunca "ilegales".
- Transparencia total de decisiones metodológicas (Principio 7) en un cuaderno de bitácora.
- Evitar que los proxies de vulnerabilidad se lean como "déficit" de las mujeres y no como fallas estructurales del sistema (Principio 2).

---

## 12. Entregables y estructura propuesta del proyecto

```
datasketch-migration-data/
├── METODOLOGIA.md                  ← este documento
├── README.md                       ← resumen ejecutivo + cómo correr
├── requirements.txt
├── docs/
│   ├── fuentes.md                  ← registro normalizado de las 3 investigaciones + fuentes a descargar
│   ├── diccionario_variables.md    ← operacionalización completa con códigos DANE
│   └── bitacora_decisiones.md      ← log de decisiones (Principio 7)
├── src/
│   ├── 00_inventario.py            ← Fase 0 ✓
│   ├── 01_consolidacion_panel.py   ← Fase 1 ✓
│   ├── 02_join_epm.py              ← Fase 2 ✓ (join EPM VIII × GEIH)
│   └── lib_geih.py                 ← funciones compartidas (carga, ponderación, brechas, OR)
├── analisis_bancarizacion_mujeres_migrantes.ipynb  ← Fases 3–7 ✓ (8 secciones)
├── Data/                           ← (en .gitignore) 12 meses + 3 investigaciones .md
└── outputs/                        ← tablas, figuras, panorama final
```

**Entregable final:** un *Panorama de la bancarización de las mujeres migrantes en Colombia (2025)* — informe con perfil interseccional, proxies de vulnerabilidad, brechas con índice de paridad, tasas de oferta trianguladas, barreras explicativas y un mapa de brechas de datos.

---

## 13. Referencias

### Fuentes teóricas

- D'Ignazio, C. & Klein, L. F. (2020). *Data Feminism*. MIT Press. https://data-feminism.mitpress.mit.edu/
- Crenshaw, K. (1989). *Demarginalizing the Intersection of Race and Sex*.

### Fuentes de datos — Primarias

- DANE (2025). *Gran Encuesta Integrada de Hogares (GEIH) 2025*. Recuperado de https://microdatos.dane.gov.co/index.php/catalog/879/study-description
- DANE (s.f.). *Gran Encuesta Integrada de Hogares (GEIH) — Módulo F1: Características generales, seguridad social en salud y educación*. Recuperado de https://microdatos.dane.gov.co/index.php/catalog/853/data-dictionary/F1?file_name=Caracteristicas%20generales,%20seguridad%20social%20en%20salud%20y%20educacion
- DANE. *Encuesta Pulso de la Migración (EPM) Ronda VIII*. Catálogo de microdatos DANE. https://microdatos.dane.gov.co/

### Fuentes de datos — Investigación académica y aplicada

- Barboni, G., de Roux, N. & Pérez‑Cardona, S. (2024). *Perceived Social Acceptance and Migrants' Financial Inclusion*. Documento CEDE 2024‑48, Universidad de los Andes. https://repositorio.uniandes.edu.co/flip/?pdf=/bitstreams/94acbfa4-596a-40cb-a5f3-7d781a0bbd16/download
- Innovations for Poverty Action (2024–2025). *Financial Inclusion of Venezuelan Migrants in Colombia*. IPA Colombia Office. Recuperado de https://es.poverty-action.org/financial-inclusion-venezuelan-migrants-colombia

### Fuentes de datos — Oferta financiera

- Superintendencia Financiera de Colombia & Banca de las Oportunidades. *Reporte de Inclusión Financiera (RIF) 2024*.
- Banco Mundial. *Global Findex 2025*.
