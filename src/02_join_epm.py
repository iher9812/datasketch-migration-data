# -*- coding: utf-8 -*-
"""
02_join_epm.py — Fase 2: join EPM Ronda VIII con panel GEIH 2025.

La EPM es la única fuente que permite medir bancarización real con desagregación
interseccional a nivel de microdato. Comparte llaves (DIRECTORIO + SECUENCIA_P + ORDEN)
con los meses de GEIH sobre los que fue levantada (enero–mayo 2025).

NOTA METODOLOGICA:
  - Match rate 16%: la EPM VIII fue levantada sobre meses específicos de la GEIH.
    Solo los hogares que aparecen en ambas fuentes hacen match (inner join).
    El balance test al final del script evalúa si las matcheadas difieren de las no matcheadas.
  - FEX_C18 (GEIH) se usa como factor de expansión porque la EPM es submuestra de la GEIH.
    Alternativa FEX_PER (EPM) no se usa aquí; si se requiere inferencia puramente EPM,
    usar FEX_PER del archivo EPM8_Personas.csv.
  - pd3__N (tipo de producto) solo se pregunta a quienes tienen al menos un producto (pd1==1).
    El denominador correcto para "% del total con ese producto" es el total de la muestra,
    no solo las bancarizadas. Ambas métricas se reportan explícitamente.
  - Etiquetas PD5 (barreras) son ASUMIDAS por contexto del cuestionario.
    Verificar contra diccionario oficial DANE EPM Ronda VIII:
    https://microdatos.dane.gov.co/index.php/catalog/837

Outputs:
  outputs/epm_geih_join.parquet       — personas EPM8 con perfil GEIH completo
  outputs/bancarizacion_mm.parquet    — subconjunto mujeres migrantes adultas

Uso:
    python src/02_join_epm.py
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.stdout.reconfigure(encoding="utf-8")

from lib_geih import LLAVES_PERSONA

OUTPUTS = Path(__file__).parent.parent / "outputs"
DATA    = Path(__file__).parent.parent / "Data"
PESO    = "FEX_C18"

# ── Etiquetas del módulo PD (productos financieros) ───────────────────────────
# ASUMIDAS por contexto del cuestionario EPM Ronda VIII — verificar contra
# diccionario oficial DANE: https://microdatos.dane.gov.co/index.php/catalog/837
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

# ASUMIDAS — verificar contra cuestionario oficial antes de publicar
ETIQUETAS_PD5 = {
    1: "No tiene documentos",
    2: "No confia en bancos",
    3: "No necesita / no le interesa",
    4: "Cree que no cumple requisitos (autoexclusion)",
}

ETIQUETAS_PD6 = {
    1: "No lo necesita",
    2: "Prefiere efectivo",
    3: "Costo / comisiones",
    4: "No sabe como usarlo",
}


def cargar_epm() -> pd.DataFrame:
    ruta = DATA / "EPM8_Personas" / "EPM8_Personas.csv"
    df = pd.read_csv(ruta, sep=",", encoding="latin-1", low_memory=False)
    print(f"  EPM8 Personas cargado: {len(df):,} personas | {df.shape[1]} columnas")
    return df


def preparar_epm(epm: pd.DataFrame) -> pd.DataFrame:
    """Selecciona y etiqueta variables del módulo PD."""
    cols_pd = ["pd1", "pd4", "pd5", "pd6", "pd7"] + list(ETIQUETAS_PD3.keys())
    cols_disp = [c for c in cols_pd if c in epm.columns]

    sub = epm[LLAVES_PERSONA + cols_disp].copy()

    # pd1: bancarizado (tiene al menos 1 producto)
    sub["bancarizado"] = (sub["pd1"] == 1).astype(float)
    sub.loc[sub["pd1"].isna(), "bancarizado"] = np.nan

    # pd3__N → nombres semánticos
    # IMPORTANTE: pd3 solo se pregunta a quienes tienen producto (pd1==1).
    # Para quienes no tienen (pd1==2), pd3__N queda NaN.
    # El denominador correcto para "% del TOTAL con ese producto" es len(df_total),
    # no pd3.count() (que excluiría los NaN y usaría solo las bancarizadas como denominador).
    for col_raw, col_sem in ETIQUETAS_PD3.items():
        if col_raw in sub.columns:
            sub[col_sem] = (sub[col_raw] == 1).astype(float)
            sub.loc[sub[col_raw].isna(), col_sem] = np.nan

    # pd5: barrera principal (solo entre no bancarizados)
    if "pd5" in sub.columns:
        sub["barrera_principal"] = sub["pd5"].map(ETIQUETAS_PD5)

    # pd4: usa el producto actualmente (1=Sí, 2=No)
    if "pd4" in sub.columns:
        sub["usa_producto"] = (sub["pd4"] == 1).astype(float)
        sub.loc[sub["pd4"].isna(), "usa_producto"] = np.nan

    return sub


def hacer_join(epm_prep: pd.DataFrame, panel: pd.DataFrame) -> pd.DataFrame:
    """Join EPM8 × GEIH via llaves DIRECTORIO+SECUENCIA_P+ORDEN (inner join)."""
    vars_geih = [
        "mes_label", "mes_num", PESO,
        "es_mujer", "es_migrante", "es_mujer_migrante", "adulto",
        "pais_origen", "edad", "departamento", "urbano_rural",
        "etnia", "nivel_educativo", "afiliacion_salud",
        "informal", "cotiza_pension", "ingreso_actividad_ppal",
        "horas_cuidado_dia", "estrato", "total_personas_hogar",
    ]
    vars_disp = [v for v in vars_geih if v in panel.columns]
    panel_slim = panel[LLAVES_PERSONA + vars_disp].drop_duplicates(subset=LLAVES_PERSONA)

    joined = epm_prep.merge(panel_slim, on=LLAVES_PERSONA, how="inner")
    return joined


def balance_test_join(epm_raw: pd.DataFrame, joined: pd.DataFrame) -> None:
    """
    Compara distribuciones de variables disponibles en EPM entre
    personas que matchearon (joined) y las que no (epm_no_match).
    Solo evalúa variables propias de la EPM ya que GEIH no está disponible
    para las no matcheadas.
    """
    llaves_set = set(map(tuple, joined[LLAVES_PERSONA].values))
    epm_no_match = epm_raw[~epm_raw[LLAVES_PERSONA].apply(
        lambda r: tuple(r) in llaves_set, axis=1
    )].copy()

    n_match   = len(joined)
    n_no_match = len(epm_no_match)
    print(f"\n  BALANCE TEST DEL JOIN")
    print(f"  Matcheadas   : {n_match:,}  ({n_match/(n_match+n_no_match)*100:.1f}%)")
    print(f"  No matcheadas: {n_no_match:,}  ({n_no_match/(n_match+n_no_match)*100:.1f}%)")

    # Variables disponibles en EPM para comparar
    vars_balance = {
        "pd1 (bancarizado)":     lambda df: (df["pd1"] == 1).mean() * 100,
        "Estado (departamento)": lambda df: df["Estado"].nunique(),
    }

    print(f"\n  {'Variable':<28} {'Matcheadas':>12} {'No matcheadas':>15} {'Dif':>6}")
    print(f"  {'-'*28} {'-'*12} {'-'*15} {'-'*6}")
    alerta = False
    for label, fn in vars_balance.items():
        try:
            v_m  = fn(epm_raw[epm_raw[LLAVES_PERSONA].apply(lambda r: tuple(r) in llaves_set, axis=1)])
            v_nm = fn(epm_no_match)
            dif  = abs(v_m - v_nm)
            flag = " ⚠" if dif > 10 else ""
            print(f"  {label:<28} {v_m:>11.1f}% {v_nm:>14.1f}%{v_nm:>0.0f} {dif:>5.1f}{flag}")
            if dif > 10:
                alerta = True
        except Exception:
            pass

    if alerta:
        print("\n  ⚠ ADVERTENCIA: diferencia >10 pp en alguna variable — submuestra potencialmente sesgada.")
        print("    Los resultados EPM deben interpretarse como submuestra de conveniencia.")
    else:
        print("\n  ✓ Sin diferencias >10 pp en variables observables de la EPM.")
        print("    Nota: balance limitado — GEIH no disponible para no matcheadas.")


def pct_productos(mm: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula % de cada producto con DOS denominadores explícitos:
      - % de bancarizadas (n=bancarizadas): denominador correcto para "entre quienes tienen producto"
      - % del total (n=total MM):          denominador correcto para "del total de mujeres migrantes"

    pd3__N solo se pregunta a bancarizadas (pd1==1), por lo que su mean() excluye NaN
    y usaría solo bancarizadas como denominador — lo cual es CORRECTO para la primera métrica
    pero INCORRECTO si se quiere reportar sobre el total.
    """
    n_total = len(mm)
    n_banc  = int(mm["bancarizado"].eq(1).sum())

    productos = [v for v in ETIQUETAS_PD3.values() if v in mm.columns]
    filas = []
    for prod in productos:
        n_tiene = int(mm[prod].eq(1).sum())
        pct_de_banc  = (n_tiene / n_banc  * 100) if n_banc  > 0 else np.nan
        pct_del_total = (n_tiene / n_total * 100) if n_total > 0 else np.nan
        filas.append({
            "Producto":          prod,
            "n tiene":           n_tiene,
            "% (de bancarizadas)": round(pct_de_banc, 1),
            "% (del total MM)":  round(pct_del_total, 1),
        })
    return pd.DataFrame(filas).sort_values("% (del total MM)", ascending=False)


def resumen(df: pd.DataFrame, label: str) -> None:
    n = len(df)
    banc = df["bancarizado"].mean() * 100 if "bancarizado" in df.columns else np.nan
    print(f"\n  [{label}]")
    print(f"    n muestral  : {n:,}")
    if PESO in df.columns:
        print(f"    n ponderado : {df[PESO].sum():,.0f}")
    print(f"    bancarizado : {banc:.1f}%")


def main():
    print("=" * 65)
    print("  JOIN EPM RONDA VIII × GEIH 2025 — Fase 2")
    print("=" * 65)

    OUTPUTS.mkdir(exist_ok=True)

    print("\n  Cargando fuentes...")
    epm_raw = cargar_epm()
    panel   = pd.read_parquet(OUTPUTS / "panel_geih_2025.parquet")
    print(f"  Panel GEIH: {len(panel):,} personas-mes | {panel.shape[1]} columnas")

    print("\n  Preparando módulo PD...")
    epm_prep = preparar_epm(epm_raw)

    print("\n  Ejecutando join...")
    joined = hacer_join(epm_prep, panel)
    print(f"  Match: {len(joined):,} de {len(epm_raw):,} personas "
          f"({len(joined)/len(epm_raw)*100:.1f}%)")

    meses = joined["mes_label"].value_counts().sort_index()
    print(f"  Meses del panel que matchean:")
    for mes, n in meses.items():
        print(f"    {mes}: {n}")

    # ── Balance test ───────────────────────────────────────────────────────────
    balance_test_join(epm_raw, joined)

    # ── Resúmenes por grupo ────────────────────────────────────────────────────
    print("\n  " + "="*50)
    print("  BANCARIZACION POR GRUPO")
    print("  " + "="*50)

    adultos = joined[joined["adulto"]].copy()

    def grupo(row):
        m   = bool(row.get("es_mujer", False))
        mig = bool(row.get("es_migrante", False))
        if m and mig: return "Mujer migrante"
        if m:         return "Mujer local"
        if mig:       return "Hombre migrante"
        return "Hombre local"

    adultos["grupo"] = adultos.apply(grupo, axis=1)

    for g in ["Mujer migrante", "Hombre migrante", "Mujer local", "Hombre local"]:
        sub = adultos[adultos["grupo"] == g]
        resumen(sub, g)

    # ── Productos con denominadores correctos ─────────────────────────────────
    mm = adultos[(adultos["es_mujer"]) & (adultos["es_migrante"])].copy()

    print("\n  " + "="*50)
    print("  PRODUCTOS — MUJERES MIGRANTES ADULTAS")
    print("  (dos denominadores: % de bancarizadas | % del total)")
    print("  " + "="*50)
    prod_df = pct_productos(mm)
    print(prod_df.to_string(index=False))

    print("\n  ⚠ NOTA: etiquetas PD5 (barreras) son asumidas — verificar diccionario DANE")
    print("\n  " + "="*50)
    print("  BARRERAS — ENTRE SIN PRODUCTO (mujeres migrantes)")
    print("  " + "="*50)
    sin_prod = mm[mm["bancarizado"] == 0]
    if "barrera_principal" in sin_prod.columns:
        bar = sin_prod["barrera_principal"].value_counts(dropna=False)
        for barrera, n in bar.items():
            pct = n / len(sin_prod) * 100
            print(f"  {str(barrera):<45} {pct:>5.1f}%  (n={n})")

    # ── Guardar outputs ────────────────────────────────────────────────────────
    print("\n  Guardando outputs...")
    joined.to_parquet(OUTPUTS / "epm_geih_join.parquet", index=False, engine="pyarrow")
    print(f"  ✓ epm_geih_join.parquet ({len(joined):,} filas)")

    mm_out = adultos[(adultos["es_mujer"]) & (adultos["es_migrante"])].copy()
    mm_out.to_parquet(OUTPUTS / "bancarizacion_mm.parquet", index=False, engine="pyarrow")
    print(f"  ✓ bancarizacion_mm.parquet ({len(mm_out):,} filas)")

    print("\n  DONE.")


if __name__ == "__main__":
    main()
