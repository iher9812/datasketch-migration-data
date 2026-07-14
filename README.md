# Bancarización de las mujeres migrantes en Colombia (2025)

Análisis de datos con **enfoque de feminismo de datos** (D'Ignazio & Klein, 2020) sobre la
inclusión financiera de las mujeres migrantes —mayoritariamente venezolanas— en Colombia,
a partir de la **GEIH 2025** del DANE, la **Encuesta Pulso de la Migración (EPM Ronda VIII)**
y evidencia externa (estudios CEDE/IPA, RIF 2024).

> La GEIH **no mide bancarización**. Por eso el proyecto usa un diseño **triangulado**:
> la GEIH aporta el perfil sociodemográfico y proxies de vulnerabilidad (lado demanda);
> la EPM aporta la bancarización real a nivel de microdato; y las fuentes externas aportan
> benchmarks y barreras. Ver [`METODOLOGIA.md`](METODOLOGIA.md).

---

## Hallazgos principales

En una frase: **~4 de cada 5 mujeres migrantes adultas no tiene ningún producto financiero
formal**, y su desventaja se concentra en salud contributiva y carga de cuidado. Los resultados
son **descriptivos y observacionales** (asociaciones, no causas), sobre submuestras.

→ Cifras completas, tablas y su interpretación: **[`METODOLOGIA.md`](METODOLOGIA.md) §7** y las
Secciones 5–8 del [notebook](analisis_bancarizacion_mujeres_migrantes.ipynb).

---

## Estructura del proyecto

```
datasketch-migration-data/
├── README.md                     ← este archivo
├── METODOLOGIA.md                ← diseño metodológico completo (marco, fases, definiciones)
├── requirements.txt
├── analisis_bancarizacion_mujeres_migrantes.ipynb   ← notebook de análisis (Secciones 1–8)
├── src/
│   ├── lib_geih.py               ← funciones compartidas (carga robusta, ponderación, brechas)
│   ├── 00_inventario.py          ← Fase 0: verifica los meses disponibles (11, sin abril) × 8 módulos
│   ├── 01_consolidacion_panel.py ← Fase 1: consolida el panel GEIH y deriva variables
│   └── 02_join_epm.py            ← Fase 2: une EPM VIII (bancarización real) con la GEIH
├── docs/
│   ├── fuentes.md                ← registro normalizado de fuentes de triangulación
│   └── pendientes_verificacion.md← supuestos aún no verificados (etiquetas DANE, etc.)
├── outputs/                      ← datasets generados (.parquet) — no versionado
├── Data/                         ← microdatos GEIH + investigaciones .md — no versionado
└── .claude/skills/feminismo-datos/  ← skill de análisis feminista usada en el proyecto
```

> `Data/`, `outputs/` y `.venv/` están en `.gitignore` (microdatos pesados y resultados regenerables).

---

## Cómo ejecutarlo

```bash
# 1. Entorno
python -m venv .venv
.venv\Scripts\activate            # Windows (PowerShell/Git Bash)
pip install -r requirements.txt

# 2. Pipeline de datos (ETL) — genera los .parquet en outputs/
python src/00_inventario.py           # verifica que los meses (11, sin abril) estén completos
python src/01_consolidacion_panel.py  # construye el panel GEIH ponderado
python src/02_join_epm.py             # une la EPM (bancarización real)

# 3. Análisis
# Abrir el notebook y ejecutarlo con el kernel del .venv
jupyter notebook analisis_bancarizacion_mujeres_migrantes.ipynb
```

Los microdatos de la GEIH y la EPM se descargan del portal de microdatos del DANE y se
colocan en `Data/<Mes> 2025/CSV/`. El notebook lee los `.parquet` que produce el ETL.

---

## Cómo se construyó este proyecto (proceso de trabajo con Claude Code)

Este proyecto se desarrolló de forma **iterativa y asistida por IA** (Claude Code), en una
colaboración humano-en-el-bucle donde cada paso se **verificó contra los datos reales** antes
de darlo por bueno. A grandes rasgos, el proceso de *prompting* siguió estas etapas:

1. **Diagnóstico de un notebook heredado.** Se partió de un notebook que "medía" bancarización
   con la GEIH. Se pidió a la IA analizar los archivos y reportar qué había — no asumir que
   funcionaba. Primer arreglo: rutas rotas y entorno de `matplotlib`.

2. **Instalación y uso de una *skill* propia.** Se incorporó una skill de *feminismo de datos*
   (`.claude/skills/feminismo-datos/`) para dar a la IA un marco analítico explícito (los 7
   principios de *Data Feminism*), en lugar de dejar el enfoque implícito.

3. **Red team del análisis.** Se le pidió a la IA **auditar su propio objeto de estudio** con
   ese marco. La auditoría —contrastada con los microdatos— encontró fallas de validez graves:
   la variable usada como "productos financieros" no lo era, falacia ecológica (dato de hogar
   tratado como individual), ausencia de factor de expansión, menores incluidos y una variable
   territorial mal mapeada.

4. **Rediseño desde cero.** En vez de parchar, se pidió una **metodología nueva** ([`METODOLOGIA.md`](METODOLOGIA.md)):
   diseño triangulado (GEIH + EPM + fuentes externas), definiciones operativas y fases. Las
   decisiones de alcance se tomaron con el humano en el bucle (modo plan y preguntas puntuales).

5. **Implementación por capas.** Scripts de ETL reproducibles (`src/`) para lo pesado y
   determinista; notebook para el análisis iterativo con gráficas. Cada script se ejecutó y
   se revisaron sus salidas reales.

6. **Revisión crítica y corrección de errores de la propia IA.** Varias veces la IA **se
   equivocó y se corrigió**: p. ej. escribió una sección con firmas de funciones inventadas y
   una narrativa que **contradecía los datos**; al re-ejecutar y comparar con las tablas reales,
   se reescribió el código y el texto para que la prosa siguiera a los números, no al revés.

**Principios de trabajo que guiaron el *prompting*:**
- *Verificar, no confiar*: cada afirmación numérica se comprobó ejecutando código sobre los datos.
- *La IA audita su propio trabajo* (red team) antes de dar resultados por válidos.
- *Humano en el bucle* para decisiones de alcance y metodología (modo plan, aprobaciones).
- *Documentar las limitaciones como parte del resultado*, no ocultarlas.
- *La prosa sigue a los datos*: si los números contradicen la narrativa, se corrige la narrativa.

> Nota de transparencia (Principio 7 — *hacer visible el trabajo*): este README y buena parte
> del código y la documentación se produjeron con asistencia de Claude Code bajo revisión y
> dirección humana. Los microdatos son del DANE (GEIH y EPM 2025).

---

## Limitaciones

El proyecto documenta seis limitaciones formales que sugieren que la exclusión real es **mayor**
que la observada (sesgo de cobertura, binarismo de sexo, submuestra EPM, diseño observacional…).

→ Detalle en **[`METODOLOGIA.md`](METODOLOGIA.md) §10** y la Sección 8 del notebook.

---

## Referencias y fuentes

Marco teórico, fuentes primarias y de triangulación (con enlaces) en
**[`METODOLOGIA.md`](METODOLOGIA.md) §13** y **[`docs/fuentes.md`](docs/fuentes.md)**.
