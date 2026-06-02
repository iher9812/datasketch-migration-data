# -*- coding: utf-8 -*-
"""
01_consolidacion_panel.py — Fase 1: consolidación del panel GEIH 2025.

Carga los 11 meses disponibles (enero–diciembre 2025, sin abril), cruza los
6 módulos activos por persona/hogar y deriva las variables operativas definidas
en METODOLOGIA.md §3. Guarda el resultado en formato Parquet.

Uso:
    python src/01_consolidacion_panel.py
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.stdout.reconfigure(encoding="utf-8")

from lib_geih import (
    DATA_ROOT, MESES_2025, LLAVES_PERSONA, LLAVES_HOGAR, PREFIJOS_CUIDADO,
    buscar_csv, cargar_modulo, validar_llaves, derivar_variables,
)

OUTPUTS_DIR = Path(__file__).parent.parent / "outputs"

# ── Diccionarios de variables por módulo ──────────────────────────────────────

VARS_F1 = {
    "DIRECTORIO": "DIRECTORIO", "SECUENCIA_P": "SECUENCIA_P", "ORDEN": "ORDEN",
    "PERIODO": "periodo_dane", "MES": "mes_dane",
    "FEX_C18": "FEX_C18",
    "P3271":   "sexo",                    # 1=Hombre, 2=Mujer
    "P6040":   "edad",
    "P6070":   "estado_civil",
    "P6080":   "etnia",                   # autorreconocimiento (1=indígena...6=ninguno)
    "P6090":   "afiliacion_salud",        # 1=contributivo, 2=subsidiado, 3=no afiliado...
    "P3042":   "nivel_educativo",
    "DPTO":    "departamento",
    "CLASE":   "clase_zona",              # 1=cabecera, 2=rural
}

VARS_F6 = {
    "DIRECTORIO": "DIRECTORIO", "SECUENCIA_P": "SECUENCIA_P", "ORDEN": "ORDEN",
    "P3373":    "lugar_nacimiento",       # 1=este mpio, 2=otro mpio CO, 3=otro país
    "P3373S3":  "P3373S3",               # código ISO del país de nacimiento
    "P3373S3A1": "anio_llegada_colombia",
    "P3373S3A2": "mes_llegada_colombia",
    "P3375S1":  "tiempo_colombia_meses",
    "P3376":    "vivio_otro_pais_6m",    # 1=Sí, 2=No
}

VARS_F7 = {
    "DIRECTORIO": "DIRECTORIO", "SECUENCIA_P": "SECUENCIA_P",
    "P4030S1A1": "estrato",
    "P5090":     "tenencia_vivienda",
    "P6008":     "total_personas_hogar",
}

VARS_OCUPADOS = {
    "DIRECTORIO": "DIRECTORIO", "SECUENCIA_P": "SECUENCIA_P", "ORDEN": "ORDEN",
    "P6400": "posicion_ocupacional",      # 1=obrero/emp priv, 2=obrero/emp gob, 4=cta propia...
    "P6440": "tipo_contrato",             # 1=término fijo, 2=término indefinido
    "P6430": "cotiza_pension",            # 1=cotiza, 4=no cotiza, etc.
    "P6450": "tamanio_empresa",
    "P6460": "actividad_economica",
}

VARS_INGRESOS = {
    "DIRECTORIO": "DIRECTORIO", "SECUENCIA_P": "SECUENCIA_P", "ORDEN": "ORDEN",
    "P7500S1A1": "ingreso_actividad_ppal",   # ingreso mensual actividad principal
    "P7500S2A1": "ingreso_actividad_sec",    # ingreso actividad secundaria
    "P7510S1A1": "arriendo_imputado",
}

# PREFIJOS_CUIDADO importado desde lib_geih para garantizar consistencia entre scripts


def _seleccionar_renombrar(df: pd.DataFrame, mapa: dict, nombre: str) -> pd.DataFrame:
    disp = {o: n for o, n in mapa.items() if o in df.columns}
    aus  = [o for o in mapa if o not in df.columns]
    if aus:
        print(f"    [{nombre}] vars ausentes (se omiten): {aus}")
    return df[list(disp)].rename(columns=disp).copy()


def _cols_horas_cuidado(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns
            if any(c.startswith(p) for p in PREFIJOS_CUIDADO) and c.endswith("A2")]


def consolidar_mes(mes: str, num_mes: int) -> pd.DataFrame:
    c = DATA_ROOT / mes / "CSV"
    print(f"\n  [{num_mes:02d}] {mes}", flush=True)

    # Carga
    f1  = _seleccionar_renombrar(
        cargar_modulo(buscar_csv(c, "caracter", "generales")), VARS_F1, "F1")
    f6  = _seleccionar_renombrar(
        cargar_modulo(buscar_csv(c, "migraci")), VARS_F6, "F6")
    f7  = _seleccionar_renombrar(
        cargar_modulo(buscar_csv(c, "hogar", "vivienda")), VARS_F7, "F7")
    ocu = _seleccionar_renombrar(
        cargar_modulo(buscar_csv(c, "ocupados", excluir=("no",))), VARS_OCUPADOS, "Ocupados")
    ing = _seleccionar_renombrar(
        cargar_modulo(buscar_csv(c, "otros ingresos")), VARS_INGRESOS, "Ingresos")

    # Cuidado: carga completa (para extraer cols horas) + llaves
    raw_cuid = cargar_modulo(buscar_csv(c, "otras", "trabajo"))
    horas_cols = _cols_horas_cuidado(raw_cuid)
    cuid = raw_cuid[LLAVES_PERSONA + horas_cols].copy()

    # Cruce: F1 (base) ← F6 ← Ocupados ← Ingresos ← Cuidado
    n0 = len(f1)
    base = f1.merge(f6,  how="left", on=LLAVES_PERSONA, suffixes=("", "_f6"))
    base = base.merge(ocu, how="left", on=LLAVES_PERSONA, suffixes=("", "_ocu"))
    base = base.merge(ing, how="left", on=LLAVES_PERSONA, suffixes=("", "_ing"))
    base = base.merge(cuid, how="left", on=LLAVES_PERSONA, suffixes=("", "_cuid"))

    # Cruce con F7 (nivel hogar: 1:N esperado → deduplicar)
    base = base.merge(f7, how="left", on=LLAVES_HOGAR, suffixes=("", "_f7"))
    if len(base) > n0:
        base = base.drop_duplicates(subset=LLAVES_PERSONA, keep="first")

    assert len(base) == n0, f"Error: el panel creció de {n0} a {len(base)} en {mes}"

    # Metadatos temporales
    base["mes_num"] = num_mes
    base["mes_label"] = mes

    # Derivar variables operativas
    base = derivar_variables(base)

    n_mig = int(base["nacido_exterior"].sum()) if "nacido_exterior" in base.columns else "?"
    n_mm  = int((base["es_mujer_migrante"] & base["adulto"]).sum()) if "adulto" in base.columns else "?"
    print(f"      {len(base):,} personas | migrantes: {n_mig} | mujeres migrantes adultas: {n_mm}")
    return base


def main():
    print("=" * 65)
    print("  CONSOLIDACIÓN PANEL GEIH 2025 — Fase 1")
    print("=" * 65)

    OUTPUTS_DIR.mkdir(exist_ok=True)

    # Instalar pyarrow si no está disponible
    try:
        import pyarrow
    except ImportError:
        print("  Instalando pyarrow...", end=" ")
        import subprocess
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "pyarrow", "-q"], check=True
        )
        print("OK")

    meses_disponibles = []
    for mes in MESES_2025:
        if (DATA_ROOT / mes / "CSV").exists():
            meses_disponibles.append(mes)
        else:
            print(f"\n  [AVISO] Mes no disponible, se omite: {mes}")

    paneles = []
    for num_mes, mes in enumerate(meses_disponibles, 1):
        try:
            df_mes = consolidar_mes(mes, num_mes)
            paneles.append(df_mes)
        except Exception as e:
            print(f"\n  [ERROR] {mes}: {e}")

    print("\n" + "=" * 65)
    print("  APILANDO MESES")
    panel = pd.concat(paneles, ignore_index=True)
    print(f"  Panel total: {len(panel):,} filas × {panel.shape[1]} columnas")
    print(f"  Meses: {panel['mes_label'].nunique()} | Rango: {panel['mes_num'].min()}–{panel['mes_num'].max()}")
    print(f"  Migrantes: {panel['nacido_exterior'].sum():,} "
          f"({panel['nacido_exterior'].mean()*100:.2f}%)")
    print(f"  Mujeres migrantes adultas: "
          f"{(panel['es_mujer_migrante'] & panel['adulto']).sum():,}")

    # ── Guardar panel completo ─────────────────────────────────────────────
    ruta_panel = OUTPUTS_DIR / "panel_geih_2025.parquet"
    panel.to_parquet(ruta_panel, index=False, engine="pyarrow")
    print(f"\n  ✓ Panel completo guardado: {ruta_panel}")

    # ── Guardar subconjunto: mujeres migrantes adultas ─────────────────────
    mm = panel[panel["es_mujer_migrante"] & panel["adulto"]].copy()
    ruta_mm = OUTPUTS_DIR / "mujeres_migrantes_adultas.parquet"
    mm.to_parquet(ruta_mm, index=False, engine="pyarrow")
    print(f"  ✓ Subconjunto mujeres migrantes adultas: {ruta_mm}")
    print(f"    {len(mm):,} registros")


if __name__ == "__main__":
    main()
