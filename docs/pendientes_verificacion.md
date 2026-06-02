# Pendientes de verificación — datasketch-migration-data

> Asunciones que requieren verificación contra fuentes primarias antes de publicar.
> Actualizar este archivo cuando se resuelva cada ítem.

---

## CRITICO — Verificar antes de publicar

### PV-1 — Etiquetas del módulo PD5 (barreras EPM)

**Archivo:** `src/02_join_epm.py` líneas 47–52

**Asunción actual:**
```python
ETIQUETAS_PD5 = {
    1: "No tiene documentos",
    2: "No confia en bancos",
    3: "No necesita / no le interesa",
    4: "Cree que no cumple requisitos (autoexclusion)",
}
```

**Fuente a consultar:** Cuestionario oficial EPM Ronda VIII (DANE)
- URL microdatos: https://microdatos.dane.gov.co/index.php/catalog/837
- Buscar: diccionario de variables o cuestionario PDF → módulo PD, pregunta PD5

**Impacto si es incorrecta:** La clasificación "88% conductual / 12% documental" puede invertirse
si las etiquetas están en orden diferente.

**Estado:** ⏳ Pendiente

---

### PV-2 — Etiquetas del módulo PD3 (tipos de producto)

**Archivo:** `src/02_join_epm.py` líneas 33–45

**Asunción actual:**
```python
ETIQUETAS_PD3 = {
    "pd3__1":  "cuenta_ahorros",
    "pd3__2":  "cuenta_corriente",
    "pd3__3":  "credito_consumo",
    "pd3__4":  "tarjeta_credito",
    "pd3__5":  "billetera_digital",
    "pd3__6":  "microcredito",
    "pd3__7":  "giros_remesas",
    "pd3__8":  "seguro",
    "pd3__9":  "cdt_ahorro_prog",
    "pd3__10": "fondo_pension_vol",
    "pd3__11": "otro_producto",
}
```

**Evidencia de apoyo:** PD3__5 tiene 600 respondentes (mayor que cuenta corriente),
consistente con el 35% billetera como primer producto reportado por IPA 2024.
PD3__7 (giros_remesas) tiene 752 respondentes — el más alto, consistente con patrón migratorio.

**Fuente a consultar:** Mismo cuestionario EPM Ronda VIII (DANE)

**Impacto si es incorrecta:** Los % de cada producto específico son incorrectos. La bancarización
total (pd1) no se ve afectada.

**Estado:** ⏳ Pendiente

---

### PV-3 — Factor de expansión FEX_C18 vs. FEX_PER para análisis EPM

**Archivo:** `src/02_join_epm.py` línea 29

**Decisión actual:** `PESO = "FEX_C18"` (factor GEIH, traído via join)

**Justificación:** La EPM es submuestra de la GEIH y comparte sus llaves. El join inner
preserva la representatividad del panel GEIH para las personas matcheadas.

**Alternativa a explorar:** Usar `FEX_PER` (columna propia de EPM8_Personas.csv) para
estimaciones específicas de bancarización. FEX_PER fue diseñado para inferir sobre la
población EPM, no sobre la GEIH.

**Impacto:** Las tasas de bancarización podrían variar si FEX_PER pondera diferente a FEX_C18
para las personas matcheadas.

**Estado:** ⏳ Pendiente — análisis de sensibilidad recomendado

---

## MODERADO — Verificar antes de citar en publicacion

### PV-4 — Interpretación de pd4 (uso actual del producto)

**Variable:** `pd4` en EPM8_Personas.csv (1=Sí usa, 2=No usa)

**Asunción actual:** pd4==1 → `usa_producto = True`

**Verificar:** ¿pd4 pregunta si usa el producto "en los últimos 3 meses" o "actualmente"?
La ventana temporal afecta la interpretación de sub-uso.

**Estado:** ⏳ Pendiente

---

### PV-5 — Período de referencia de la EPM VIII

**Asunción actual:** EPM VIII levantada sobre GEIH de enero–mayo 2025 (inferido del match)

**Verificar:** Documento metodológico DANE EPM Ronda VIII → confirmar qué meses de GEIH
sirvieron como marco muestral y período de referencia exacto.

**URL:** https://microdatos.dane.gov.co/index.php/catalog/837

**Impacto:** Afecta la interpretación temporal de los resultados de bancarización.

**Estado:** ⏳ Pendiente

---

## RESUELTO

*(Mover ítems aquí cuando se verifiquen)*

---

*Última actualización: junio 2026 | Proyecto: datasketch-migration-data*
