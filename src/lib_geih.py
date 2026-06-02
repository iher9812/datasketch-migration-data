# -*- coding: utf-8 -*-
"""
lib_geih.py — Funciones compartidas para el proyecto datasketch-migration-data.

Proporciona carga robusta de la GEIH (resistente a espacios NBSP en nombres de
archivo), validación de llaves, ponderación y cálculo de brechas interseccionales.
"""

from __future__ import annotations
import re
from pathlib import Path
import pandas as pd
import numpy as np

# ── Constantes ────────────────────────────────────────────────────────────────

DATA_ROOT = Path(__file__).parent.parent / "Data"

MESES_2025 = [
    "Enero 2025", "Febrero 2025", "Marzo 2025", "Abril 2025",
    "Mayo 2025", "Junio 2025", "Julio 2025", "Agosto 2025",
    "Septiembre 2025", "Octubre 2025", "Noviembre 2025", "Diciembre 2025",
]

PAISES_ISO: dict[int, str] = {
    # América Latina y el Caribe
    28:  "Antigua y Barbuda",
    32:  "Argentina",
    68:  "Bolivia",
    76:  "Brasil",
    124: "Canadá",
    152: "Chile",
    170: "Colombia*",
    188: "Costa Rica",
    192: "Cuba",
    214: "Rep. Dominicana",
    218: "Ecuador",
    222: "El Salvador",
    320: "Guatemala",
    332: "Haití",
    340: "Honduras",
    388: "Jamaica",
    484: "México",
    558: "Nicaragua",
    591: "Panamá",
    600: "Paraguay",
    604: "Perú",
    630: "Puerto Rico",
    533: "Aruba",
    660: "Anguila",
    780: "Trinidad y Tobago",
    858: "Uruguay",
    862: "Venezuela",
    # América del Norte
    840: "Estados Unidos",
    # Europa
    8:   "Albania",
    56:  "Bélgica",
    112: "Bielorrusia",
    276: "Alemania",
    250: "Francia",
    300: "Grecia",
    348: "Hungría",
    352: "Islandia",
    380: "Italia",
    528: "Países Bajos",
    616: "Polonia",
    620: "Portugal",
    642: "Rumanía",
    643: "Rusia",
    724: "España",
    756: "Suiza",
    804: "Ucrania",
    826: "Reino Unido",
    # Asia
    4:   "Afganistán",
    20:  "Andorra",
    51:  "Armenia",
    156: "China",
    344: "Hong Kong",
    376: "Israel",
    400: "Jordania",
    422: "Líbano",
    446: "Macao",
    586: "Pakistán",
    682: "Arabia Saudita",
    704: "Vietnam",
    # África y Oceanía
    36:  "Australia",
    74:  "Isla Bouvet",
    180: "R.D. Congo",
    226: "Guinea Ecuatorial",
    504: "Marruecos",
    548: "Vanuatu",
    776: "Tonga",
    798: "Tuvalu",
}

LLAVES_PERSONA = ["DIRECTORIO", "SECUENCIA_P", "ORDEN"]
LLAVES_HOGAR   = ["DIRECTORIO", "SECUENCIA_P"]

# Actividades de cuidado no remunerado en módulo "Otras formas de trabajo"
# P30xx → códigos DANE actividades 76-82 (excluye 80 que no es cuidado)
# A2 = horas/día; lista explícita para evitar falsos positivos con regex
PREFIJOS_CUIDADO = [f"P30{x}" for x in ["76", "77", "78", "79", "81", "82"]]

# ── Localización de archivos ──────────────────────────────────────────────────

def buscar_csv(
    carpeta: Path,
    *palabras_clave: str,
    excluir: tuple[str, ...] = (),
) -> Path:
    """
    Devuelve el primer CSV de `carpeta` cuyo nombre contiene TODAS las
    `palabras_clave` y NINGUNA de las `excluir` (insensible a mayúsculas y NBSP).

    Los archivos del DANE llevan caracteres NBSP (\\xa0); esta función los
    normaliza antes de comparar para que la búsqueda por palabra clave sea robusta.

    Ejemplo:
        buscar_csv(c, "ocupados", excluir=("no",))  # evita "No ocupados.CSV"
    """
    if not carpeta.exists():
        raise FileNotFoundError(f"Carpeta no encontrada: {carpeta.resolve()}")

    def _normalizar(texto: str) -> str:
        return re.sub(r"\s+", " ", texto).lower().strip()

    for archivo in carpeta.iterdir():
        if archivo.suffix.lower() != ".csv":
            continue
        nombre_norm = _normalizar(archivo.name)
        if not all(_normalizar(k) in nombre_norm for k in palabras_clave):
            continue
        if any(_normalizar(e) in nombre_norm for e in excluir):
            continue
        return archivo

    raise FileNotFoundError(
        f"No se encontró CSV con {palabras_clave!r} (excluir={excluir!r}) en {carpeta}"
    )


def carpeta_csv(mes: str) -> Path:
    """Devuelve la ruta a la carpeta CSV de un mes."""
    return DATA_ROOT / mes / "CSV"


# ── Carga de módulos ──────────────────────────────────────────────────────────

def cargar_modulo(ruta: Path, nombre: str = "") -> pd.DataFrame:
    """
    Carga un CSV de la GEIH con fallback de encoding latin-1 → utf-8.
    Separador: punto y coma (`;`).
    """
    for enc in ("latin-1", "utf-8"):
        try:
            df = pd.read_csv(ruta, sep=";", encoding=enc, low_memory=False)
            return df
        except UnicodeDecodeError:
            continue
    raise ValueError(f"No se pudo leer {ruta} con latin-1 ni UTF-8")


def cargar_mes(mes: str) -> dict[str, pd.DataFrame]:
    """
    Carga los 6 módulos activos de un mes y los devuelve en un dict.

    Claves: "f1", "f6", "f7", "ocupados", "ingresos", "cuidado"
    """
    c = carpeta_csv(mes)
    return {
        "f1":       cargar_modulo(buscar_csv(c, "caracter", "generales")),
        "f6":       cargar_modulo(buscar_csv(c, "migraci")),
        "f7":       cargar_modulo(buscar_csv(c, "hogar", "vivienda")),
        "ocupados": cargar_modulo(buscar_csv(c, "ocupados")),
        "ingresos": cargar_modulo(buscar_csv(c, "otros ingresos")),
        "cuidado":  cargar_modulo(buscar_csv(c, "otras", "trabajo")),
    }


# ── Validación de llaves ──────────────────────────────────────────────────────

def validar_llaves(df: pd.DataFrame, nombre: str, llaves: list[str]) -> bool:
    """
    Verifica existencia, ausencia de nulos y unicidad de las `llaves`.
    Devuelve True si todo es correcto; imprime advertencias si no.
    """
    faltantes = [c for c in llaves if c not in df.columns]
    if faltantes:
        print(f"  [{nombre}] ⚠ llaves ausentes: {faltantes}")
        return False

    nulos = df[llaves].isnull().sum()
    if nulos.any():
        print(f"  [{nombre}] ⚠ nulos en llaves:\n{nulos[nulos > 0]}")

    llave_comp = df[llaves].astype(str).agg("-".join, axis=1)
    n_dup = len(df) - llave_comp.nunique()
    if n_dup:
        print(f"  [{nombre}] ⚠ {n_dup:,} duplicados en llave compuesta")
        return False

    return True


# ── Derivación de variables ───────────────────────────────────────────────────

def derivar_variables(base: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica las definiciones operativas sobre la base consolidada.
    Modifica el DataFrame in-place y lo devuelve.

    Convenciones (documentadas en METODOLOGIA.md §3):
    - nacido_exterior  : bool  P3373 == 3
    - pais_origen      : str   etiqueta ISO a partir de P3373S3
    - urbano_rural     : int   CLASE (1=cabecera, 2=rural)  — NO usar AREA
    - adulto           : bool  P6040 >= 18
    - es_mujer         : bool  P3271 == 2
    - es_migrante      : bool  nacido_exterior
    - es_mujer_migrante: bool  es_mujer & es_migrante
    - informal         : bool  P6430 != 1 (no cotiza a pensión)  — solo ocupados
    - horas_cuidado    : float suma de horas/día de actividades de cuidado no remunerado
    """
    # Migración — acepta tanto el nombre DANE crudo (P3373) como el renombrado
    col_nac = "lugar_nacimiento" if "lugar_nacimiento" in base.columns else (
              "P3373" if "P3373" in base.columns else None)
    if col_nac:
        base["nacido_exterior"] = base[col_nac] == 3

    col_pais = "P3373S3" if "P3373S3" in base.columns else None
    if col_pais is None and "pais_nacimiento" in base.columns:
        col_pais = "pais_nacimiento"
    if col_pais:
        def _etiqueta_pais(cod):
            if pd.isna(cod):
                return np.nan
            try:
                return PAISES_ISO.get(int(float(str(cod).strip())), str(cod).strip())
            except (ValueError, TypeError):
                return str(cod).strip()
        base["pais_origen"] = base[col_pais].apply(_etiqueta_pais)

    # Territorio (corregido: CLASE, no AREA)
    col_clase = "clase_zona" if "clase_zona" in base.columns else (
                "CLASE" if "CLASE" in base.columns else None)
    if col_clase:
        base["urbano_rural"] = base[col_clase].map({1: "Cabecera", 2: "Rural"})

    # Edad y grupo
    col_edad = "edad" if "edad" in base.columns else (
               "P6040" if "P6040" in base.columns else None)
    if col_edad:
        base["adulto"] = base[col_edad] >= 18

    col_sexo = "sexo" if "sexo" in base.columns else (
               "P3271" if "P3271" in base.columns else None)
    if col_sexo:
        base["es_mujer"] = base[col_sexo] == 2

    # Indicadores derivados
    nacido = base.get("nacido_exterior", pd.Series(False, index=base.index))
    mujer  = base.get("es_mujer",        pd.Series(False, index=base.index))
    base["es_migrante"]      = nacido
    base["es_mujer_migrante"] = mujer & nacido

    # Informalidad (proxy: no cotiza a pensión)
    col_cot = "cotiza_pension" if "cotiza_pension" in base.columns else (
              "P6430" if "P6430" in base.columns else None)
    if col_cot:
        base["informal"] = (base[col_cot] != 1) & base[col_cot].notna()

    # Horas de cuidado no remunerado — usar lista explícita (más segura que regex)
    horas_cols = [c for c in base.columns
                  if any(c.startswith(p) for p in PREFIJOS_CUIDADO) and c.endswith("A2")]
    if horas_cols:
        base["horas_cuidado_dia"] = base[horas_cols].apply(
            pd.to_numeric, errors="coerce"
        ).sum(axis=1, min_count=1)

    return base


# ── Estadísticas ponderadas y brechas ─────────────────────────────────────────

def tasa_ponderada(
    df: pd.DataFrame,
    var_binaria: str,
    grupo: str,
    peso: str = "FEX_C18",
) -> pd.DataFrame:
    """
    Calcula la tasa ponderada de `var_binaria==True/1` por cada categoría de `grupo`.

    Devuelve DataFrame con columnas: grupo, n_muestral, n_ponderado, tasa_pct.
    """
    if var_binaria not in df.columns:
        raise KeyError(f"Variable '{var_binaria}' no existe en el DataFrame")
    if peso not in df.columns:
        raise KeyError(f"Peso '{peso}' no existe en el DataFrame")

    resultado = []
    for cat, sub in df.groupby(grupo, dropna=False):
        n_m = len(sub)
        n_p = sub[peso].sum()
        positivos_p = sub.loc[sub[var_binaria].fillna(False).astype(bool), peso].sum()
        tasa = (positivos_p / n_p * 100) if n_p > 0 else np.nan
        resultado.append({
            grupo: cat,
            "n_muestral": n_m,
            "n_ponderado": round(n_p),
            "tasa_pct": round(tasa, 2),
        })
    return pd.DataFrame(resultado)


def brecha_paridad(tasas: pd.DataFrame, grupo_col: str, ref: str, comp: str) -> dict:
    """
    Calcula brecha absoluta (pp) e índice de paridad entre dos grupos.

    Args:
        tasas   : DataFrame producido por tasa_ponderada()
        grupo_col: nombre de la columna de grupo
        ref     : categoría de referencia (denominador del índice)
        comp    : categoría de comparación (numerador del índice)

    Returns:
        dict con keys: brecha_absoluta_pp, indice_paridad, interpretacion
    """
    t = tasas.set_index(grupo_col)["tasa_pct"]
    if ref not in t.index or comp not in t.index:
        raise KeyError(f"Grupos '{ref}' o '{comp}' no encontrados en {list(t.index)}")

    t_ref  = t[ref]
    t_comp = t[comp]
    brecha = round(t_comp - t_ref, 2)
    indice = round(t_comp / t_ref, 4) if t_ref != 0 else np.nan

    if indice is np.nan:
        interp = "No calculable (referencia = 0)"
    elif indice < 1:
        interp = f"{comp} tiene {(1-indice)*100:.1f}% menos que {ref}"
    elif indice > 1:
        interp = f"{comp} tiene {(indice-1)*100:.1f}% más que {ref}"
    else:
        interp = "Paridad exacta"

    return {
        "brecha_absoluta_pp": brecha,
        "indice_paridad": indice,
        "interpretacion": interp,
    }
