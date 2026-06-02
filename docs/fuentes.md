# Registro de fuentes — Bancarización de mujeres migrantes en Colombia (2025)

> Catálogo normalizado de las fuentes del proyecto. Cada fuente tiene un rol
> específico dentro del diseño triangulado (ver `METODOLOGIA.md §6`):
> **Capa A (demanda/perfil)**, **Capa B (oferta/acceso)** o **Capa C (barreras/contexto)**.

---

## Tabla resumen

| # | Fuente | Tipo | Capa | Desagreg. género | Año | Hueco que llena de la GEIH |
|---|--------|------|------|-------------------|-----|---------------------------|
| 1 | GEIH 2025 — DANE | Encuesta hogares | A | Sí (binario M/F) | 2025 | Fuente primaria; NO mide bancarización |
| 2 | CEDE 2024-48 (Barboni et al.) | Paper académico | C | Sí, por subgrupo | 2024 | Barreras conductuales con evidencia causal |
| 3 | IPA Brief — Inclusión financiera | Divulgación de estudio | C | Parcial (pérdidas por género) | 2024–2025 | Cifras de uso/pérdida de productos por género |
| 4 | Compass/Catálogo de fuentes | Mapa de fuentes | A+B+C | Variable | 2024–2025 | Índice de fuentes de oferta pendientes de descargar |
| 5 | EPM — Encuesta Pulso Migración | Encuesta especializada | A | Sí | 2021–2025 | **Puente cuantitativo**: join por llave con GEIH |
| 6 | SFC Estadísticas Dinámicas | Datos administrativos | B | Parcial (crédito) | 2017–2025 | Productos vinculados a migrantes venezolanos |
| 7 | RIF 2024 (SFC + BdO) | Informe analítico | B | Sí (brecha 6,9 pp) | 2024 | Línea base nacional de bancarización |
| 8 | Global Findex 2025 | Encuesta internacional | B | Sí | 2024–2025 | Benchmark comparativo internacional |

---

## Fuentes en el repositorio (`Data/`)

### 1. GEIH 2025 — Gran Encuesta Integrada de Hogares

- **Ubicación:** `Data/<Mes> 2025/CSV/` (11 meses: ene–dic sin abril)
- **Producida por:** DANE (Departamento Administrativo Nacional de Estadística)
- **Capa:** A — perfil sociodemográfico y proxies de vulnerabilidad
- **Módulos activos en este proyecto:**

| Módulo | Variables clave para el proyecto |
|--------|----------------------------------|
| F1 — Características generales | sexo, edad, etnia, educación, salud, territorio |
| F6 — Migración | lugar de nacimiento (P3373), país (P3373S3), año llegada |
| F7 — Hogar y vivienda | estrato, tenencia, tamaño del hogar |
| Ocupados | tipo contrato (P6440), cotización pensión (P6430) → informalidad |
| Otros ingresos e impuestos | ingreso mensual actividad principal (P7500S1A1) |
| Otras formas de trabajo | horas de cuidado no remunerado (P307xSyA2) |

- **Variable que define al migrante:** `P3373 == 3` (nacido en otro país). País: `P3373S3` (862=Venezuela, ~94 % de migrantes).
- **Limitación crítica:** NO contiene módulo de inclusión financiera. La bancarización debe triangularse con fuentes de la Capa B.
- **Desagregación de género:** variable `P3271` (sexo binario M/F; personas trans/no binarias invisibles por diseño).

---

### 2. Documento CEDE 2024-48 — *Perceived Social Acceptance and Migrants' Financial Inclusion*

- **Ubicación:** `Data/fuente1.md` (también: `Archivo/dcede2024-48.pdf`)
- **Autores:** Giorgia Barboni (Warwick), Nicolás de Roux (Uniandes), Santiago Pérez-Cardona (Chicago)
- **Publicado:** Universidad de los Andes, CEDE. Diciembre 2024, revisado abril 2025
- **Capa:** C — barreras conductuales con evidencia causal
- **Metodología:** Experimento telefónico con 2.115 migrantes venezolanos en Colombia (2024)
- **Hallazgos clave para este proyecto:**
  - El **66 %** de los migrantes subestima la apertura de los colombianos hacia ellos.
  - Corregir esa percepción aumenta significativamente la disposición a abrir cuentas y usar servicios financieros.
  - La **autoexclusión** (no el desconocimiento financiero) es la barrera conductual principal.
  - Efecto diferencial por subgrupo: mayor impacto en quienes inicialmente más subestimaban la aceptación.
- **Cómo se vincula al proyecto:**
  - Aporta la **explicación causal** de las brechas observadas en los proxies de la GEIH.
  - Se cita como anotación de contexto en las visualizaciones de brechas.
  - Justifica por qué la informalidad y el no-acceso no se explican solo por características observables.
- **Desagregación por género:** Sí — las pérdidas de productos al migrar son "particularmente altas entre mujeres".

---

### 3. IPA Brief — *Inclusión financiera de migrantes venezolanos en Colombia*

- **Ubicación:** `Data/inclusion-financiera-migrantes-venezolanos-colombia.md`
- **Producido por:** IPA (Innovations for Poverty Action), en colaboración con DNP y Fundación Conrad N. Hilton
- **Año:** 2024–2025 | **Estado:** Completo
- **Capa:** C — barreras conductuales + cifras de demanda específicas
- **Metodología:** Diagnóstico (5.999 migrantes + 519 colombianos) + evaluación aleatoria (2.115 migrantes); 13 ciudades.
- **Cifras clave para triangulación:**

| Indicador | Valor | Nota |
|-----------|-------|------|
| Bancarización de colombianos | ~95 % | Línea base nacional |
| % migrantes con al menos un producto | ~27,6 % | Dato Banca de las Oportunidades citado en fuente |
| % hombres migrantes con producto | 31,6 % | Desagregado por género |
| % mujeres migrantes con producto | 23,7 % | **Brecha de 7,9 pp** |
| Perdieron productos al migrar | 24 % de quienes los tenían | Pérdidas mayores en mujeres, jóvenes y activos |
| Billetera digital como 1er producto | 35 % de nuevos usuarios | Puerta de entrada clave |
| Uso de efectivo (vs. colombianos) | +17 % | Subutilización de cuentas |
| Creían que el banco no les atendería | 41 % sin productos | Autoexclusión, no falta de educación financiera |

- **Cómo se vincula al proyecto:**
  - Aporta las **tasas de bancarización por género** que la GEIH no tiene.
  - Los 23,7 % (mujeres) vs 31,6 % (hombres) son los benchmarks de la Capa B para contextualizar proxies.
  - Justifica el diseño de análisis: la barrera conductual (autoexclusión) es más importante que la barrera de acceso documental.

---

### 4. Catálogo de fuentes (compass_artifact)

- **Ubicación:** `Data/compass_artifact_wf-6d439649-cce5-4d44-9651-57a349e4d312_text_markdown.md`
- **Capa:** A+B+C — mapa completo de fuentes
- **Contenido:** 330 líneas con descripción detallada de 9+ fuentes de datos para triangulación, incluyendo:
  - SFC Estadísticas Dinámicas (Power BI, trimestral desde 2017)
  - RIF 2024 (PDF + Excel)
  - EPM rondas I–VIII (microdatos DANE)
  - Global Findex 2025 (Banco Mundial)
  - Migración Colombia / Observatorio OM3
  - OIT, R4V/GIFMM, Asobancaria Semana Económica
- **Uso en este proyecto:** Sirve de guía para descargar las fuentes de Capa B (ver §Fuentes pendientes).

---

## El puente cuantitativo: EPM (Encuesta Pulso de la Migración)

La **EPM** es la única fuente que permite un **join directo con los microdatos de la GEIH** y que sí pregunta sobre productos financieros.

| Característica | Detalle |
|---|---|
| Producida por | DANE |
| Rondas disponibles | I–VIII (2021–2025) |
| Ronda más reciente | VIII, publicada oct. 2025 (7.532 personas / 4.110 hogares) |
| Cómo hacer el join | `DIRECTORIO + SECUENCIA_P + ORDEN` (comparte llaves con GEIH del mes anterior) |
| Variables financieras | Tenencia de productos (cuenta, crédito, billetera) + barreras de acceso |
| Desagregación por género | Sí |
| URL microdatos | microdatos.dane.gov.co/index.php/catalog/837 |

**Por qué es el puente:** La EPM es una *submuestra* de la GEIH del mes anterior. Eso significa que se puede cruzar EPM (que tiene datos de bancarización) con GEIH (que tiene el perfil sociodemográfico completo) usando las mismas llaves identificadoras. Esta es la **única forma metodológicamente válida de medir bancarización con desagregación interseccional** a nivel de microdato sin depender de datos administrativos agregados.

> **Próximo paso:** Descargar los microdatos de la EPM ronda VIII (y rondas anteriores si se quiere serie temporal) y ejecutar el join con la GEIH correspondiente.

---

## Fuentes pendientes de descarga (Capa B — oferta)

| Fuente | URL/Sistema | Variables de interés | Prioridad |
|--------|------------|---------------------|-----------|
| **SFC Estadísticas Dinámicas** | superfinanciera.gov.co/powerbi/reportes/508/504/ | Productos vinculados a migrantes por tipo, género, región | Alta |
| **RIF 2024** (PDF + Excel) | bancadelasoportunidades.gov.co/es/publicaciones/reportes-anuales | Brecha género acceso/uso, indicador nacional 96,3 % | Alta |
| **Global Findex 2025** | Banco Mundial, publicado julio 2025 | Benchmark internacional por género y país | Media |
| **EPM Ronda VIII microdatos** | microdatos.dane.gov.co/index.php/catalog/837 | Tenencia productos + barreras, join con GEIH | **Crítica** |
| **Migración Colombia OM3** | migracioncolombia.gov.co | Denominadores por departamento, género, estatus PPT/irregular | Media |

---

## Marco normativo de referencia

- **Circular Externa SFC 082/2019:** habilita el PEP y pasaporte venezolano como documentos válidos para abrir productos financieros en Colombia. Pieza clave para entender el antes/después normativo.
- **PPT (Permiso Temporal de Protección):** estatus migratorio regular vigente desde 2021; determinante del acceso a productos bancarios.

---

*Última actualización: junio 2026 | Proyecto: datasketch-migration-data*
