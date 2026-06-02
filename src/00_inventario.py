# -*- coding: utf-8 -*-
"""
00_inventario.py — Fase 0: auditoría feminista del dataset GEIH 2025.

Verifica la existencia e integridad de los 12 meses × 8 módulos CSV.
Genera outputs/inventario_geih_2025.csv con el reporte.

Uso:
    python src/00_inventario.py
"""

import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
sys.stdout.reconfigure(encoding="utf-8")

from lib_geih import DATA_ROOT, MESES_2025, buscar_csv, cargar_modulo, LLAVES_PERSONA

# Módulos a auditar: (clave, palabras_clave_para_buscar)
MODULOS = [
    ("F1 Características generales", ("caracter", "generales")),
    ("F6 Migración",                 ("migraci",)),
    ("F7 Hogar y vivienda",          ("hogar", "vivienda")),
    ("Ocupados",                     ("ocupados",)),
    ("Otros ingresos",               ("otros ingresos",)),
    ("Otras formas de trabajo",      ("otras", "trabajo")),
    ("Fuerza de trabajo",            ("fuerza",)),
    ("No ocupados",                  ("no ocupados",)),
]

VARS_CLAVE = ["DIRECTORIO", "SECUENCIA_P", "ORDEN", "FEX_C18",
              "P3271", "P3373", "P3373S3", "P6040", "CLASE"]

OUTPUTS_DIR = Path(__file__).parent.parent / "outputs"


def auditar_mes(mes: str) -> list[dict]:
    carpeta = DATA_ROOT / mes / "CSV"
    filas = []

    for mod_nombre, palabras in MODULOS:
        fila: dict = {"mes": mes, "modulo": mod_nombre}
        try:
            ruta = buscar_csv(carpeta, *palabras)
        except FileNotFoundError:
            fila.update({"existe": False, "n_filas": None, "n_cols": None,
                         "tiene_nbsp": None, "vars_clave_presentes": None})
            filas.append(fila)
            continue

        fila["existe"] = True
        fila["tiene_nbsp"] = "\xa0" in ruta.name

        # Cabecera y conteo de filas (sin cargar todo en memoria)
        try:
            header = pd.read_csv(ruta, sep=";", encoding="latin-1",
                                 nrows=0, low_memory=False)
            fila["n_cols"] = len(header.columns)
            # Contar filas eficientemente
            with ruta.open("rb") as f:
                fila["n_filas"] = sum(1 for _ in f) - 1  # -1 por cabecera
        except Exception as e:
            fila["n_cols"] = None
            fila["n_filas"] = None
            fila["error_lectura"] = str(e)

        # Verificar variables clave
        if fila.get("n_cols"):
            presentes = [v for v in VARS_CLAVE if v in header.columns]
            fila["vars_clave_presentes"] = ", ".join(presentes)

        filas.append(fila)

    return filas


def main():
    print("=" * 65)
    print("  INVENTARIO GEIH 2025 — Fase 0")
    print("=" * 65)

    OUTPUTS_DIR.mkdir(exist_ok=True)

    todas = []
    for mes in MESES_2025:
        carpeta = DATA_ROOT / mes / "CSV"
        if not carpeta.exists():
            print(f"\n  [AVISO] Carpeta no encontrada: {mes}")
            continue
        print(f"\n  Auditando {mes}...", end=" ", flush=True)
        filas = auditar_mes(mes)
        todas.extend(filas)
        encontrados = sum(1 for f in filas if f.get("existe"))
        print(f"{encontrados}/{len(MODULOS)} módulos ✓")

    df = pd.DataFrame(todas)

    # ── Resumen en consola ─────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("  TABLA RESUMEN: MÓDULOS POR MES")
    print("=" * 65)

    pivot = df.pivot_table(
        index="modulo", columns="mes", values="existe",
        aggfunc=lambda x: "✓" if all(x) else "✗"
    )
    # Reordenar columnas cronológicamente
    cols_ordenadas = [m for m in MESES_2025 if m in pivot.columns]
    print(pivot[cols_ordenadas].to_string())

    # ── Módulos con NBSP ───────────────────────────────────────────────────
    nbsp = df[df["tiene_nbsp"] == True]["modulo"].unique()
    if len(nbsp):
        print(f"\n  ⚠ Módulos con NBSP en nombre de archivo: {list(nbsp)}")
        print("    → lib_geih.buscar_csv() los maneja automáticamente.")

    # ── Verificación de variables clave en F1 del primer mes disponible ───
    print("\n  Variables clave en F1 (primer mes disponible):")
    f1_rows = df[(df["modulo"] == "F1 Características generales") & df["existe"]]
    if not f1_rows.empty:
        print(f"    {f1_rows.iloc[0]['vars_clave_presentes']}")

    # ── Guardar reporte ────────────────────────────────────────────────────
    salida = OUTPUTS_DIR / "inventario_geih_2025.csv"
    df.to_csv(salida, index=False, encoding="utf-8-sig")
    print(f"\n  Reporte guardado en: {salida}")

    # ── Advertencias finales ───────────────────────────────────────────────
    faltantes = df[df["existe"] == False]
    if len(faltantes):
        print(f"\n  ⚠ {len(faltantes)} módulo(s) no encontrado(s):")
        print(faltantes[["mes", "modulo"]].to_string(index=False))
    else:
        print("\n  ✓ Todos los módulos encontrados en todos los meses.")


if __name__ == "__main__":
    main()
