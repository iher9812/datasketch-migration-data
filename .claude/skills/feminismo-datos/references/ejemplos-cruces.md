# Ejemplos de Cruces de Datos con Enfoque Feminista

## Ejemplo 1: Cruce básico encuesta laboral

### Contexto
Encuesta Nacional de Ocupación e Ingresos con variables: sexo, edad, nivel educativo,
tipo de ocupación (formal/informal), ingreso mensual, horas trabajadas.

### Preguntas feministas de investigación
1. ¿Cuál es la brecha salarial por sexo, controlando por nivel educativo y tipo de ocupación?
2. ¿Quién hace más trabajo no remunerado? ¿Cómo se distribuye por nivel socioeconómico?
3. ¿La informalidad afecta desigualmente a mujeres según su nivel educativo?

### Código Python (pandas)

```python
import pandas as pd
import numpy as np

# --- AUDITORÍA INICIAL ---
def auditoria_feminista(df):
    print("=== AUDITORÍA FEMINISTA DEL DATASET ===")
    print(f"\nTotal de registros: {len(df)}")
    
    if 'sexo' in df.columns:
        print(f"\nDistribución por sexo:")
        print(df['sexo'].value_counts(normalize=True).round(3))
    else:
        print("\n⚠️  ALERTA: No hay variable de sexo/género en el dataset")
    
    print(f"\nValores faltantes por variable:")
    missing = df.isnull().sum()
    print(missing[missing > 0])
    
    return None


# --- ANÁLISIS DE BRECHA SALARIAL ---
def brecha_salarial(df, ingreso_col='ingreso_mensual', sexo_col='sexo'):
    """Calcula brecha salarial absoluta, relativa y ratio de paridad"""
    
    stats = df.groupby(sexo_col)[ingreso_col].agg(['mean', 'median', 'count'])
    
    # Asumiendo categorías 'Mujer' y 'Hombre'
    if 'Mujer' in stats.index and 'Hombre' in stats.index:
        brecha_abs = stats.loc['Hombre', 'mean'] - stats.loc['Mujer', 'mean']
        brecha_pct = (brecha_abs / stats.loc['Hombre', 'mean']) * 100
        ratio_paridad = stats.loc['Mujer', 'mean'] / stats.loc['Hombre', 'mean']
        
        print(f"\n=== BRECHA SALARIAL ===")
        print(f"Ingreso promedio hombres: ${stats.loc['Hombre', 'mean']:,.0f}")
        print(f"Ingreso promedio mujeres: ${stats.loc['Mujer', 'mean']:,.0f}")
        print(f"Brecha absoluta: ${brecha_abs:,.0f}")
        print(f"Brecha relativa: {brecha_pct:.1f}%")
        print(f"Ratio de paridad: {ratio_paridad:.2f} (1.0 = paridad completa)")
    
    return stats


# --- CRUCE INTERSECCIONAL ---
def cruce_interseccional(df, variable_resultado, variables_cruce):
    """
    Realiza cruce interseccional de una variable resultado
    con múltiples ejes de desigualdad
    
    Ejemplo: cruce_interseccional(df, 'ingreso_mensual', 
                                   ['sexo', 'nivel_educativo', 'zona'])
    """
    tabla = df.groupby(variables_cruce)[variable_resultado].agg([
        ('promedio', 'mean'),
        ('mediana', 'median'),
        ('n', 'count'),
        ('desv_std', 'std')
    ]).round(2)
    
    # Calcular ratio vs grupo de referencia (el de mayor valor)
    max_val = tabla['promedio'].max()
    tabla['ratio_vs_maximo'] = (tabla['promedio'] / max_val).round(3)
    
    return tabla


# --- ÍNDICE DE CONCENTRACIÓN DE DESVENTAJA ---
def concentracion_desventaja(df, variables_binarias):
    """
    Identifica qué grupos acumulan múltiples desventajas simultáneas.
    variables_binarias: dict con {'nombre_var': valor_desventaja}
    Ejemplo: {'sexo': 'Mujer', 'zona': 'Rural', 'etnia': 'Indígena'}
    """
    
    df_temp = df.copy()
    df_temp['n_desventajas'] = 0
    
    for var, valor_desventaja in variables_binarias.items():
        if var in df_temp.columns:
            df_temp['n_desventajas'] += (df_temp[var] == valor_desventaja).astype(int)
    
    distribucion = df_temp['n_desventajas'].value_counts(normalize=True).sort_index()
    
    print("\n=== CONCENTRACIÓN DE DESVENTAJAS ===")
    print("Número de desventajas simultáneas:")
    for n, pct in distribucion.items():
        barra = "█" * int(pct * 40)
        print(f"  {n} desventajas: {pct:.1%} {barra}")
    
    return df_temp


# --- USO EJEMPLO ---
# df = pd.read_csv('encuesta_laboral.csv')
# auditoria_feminista(df)
# brecha_salarial(df)
# cruce = cruce_interseccional(df, 'ingreso_mensual', ['sexo', 'nivel_educativo'])
# concentracion = concentracion_desventaja(df, 
#     {'sexo': 'Mujer', 'zona': 'Rural', 'etnia': 'Indígena'})
```

---

## Ejemplo 2: Análisis de encuesta de violencia de género

### Preguntas de investigación
1. ¿Qué factores estructurales se asocian con mayor prevalencia de violencia?
2. ¿Cómo varía el acceso a servicios de apoyo por zona geográfica y nivel educativo?
3. ¿Qué porcentaje de casos fue denunciado? ¿Qué barreras explican la no-denuncia?

### Notas metodológicas críticas

```
⚠️  ADVERTENCIAS para datos de violencia:

1. SUB-REGISTRO: Las encuestas de victimización capturan aprox. 10-30% del total real.
   Nunca presentar datos sin mencionar esta limitación.

2. SESGO DE RESPUESTA: Mujeres en contextos de control por la pareja pueden no
   reportar violencia honestamente en encuestas cara a cara.

3. DEFINICIÓN OPERACIONAL: "Violencia" se define diferente en cada instrumento.
   Siempre especificar qué tipos incluye el dato que se analiza.

4. DENOMINADOR CORRECTO: La tasa debe calcularse sobre mujeres en riesgo
   (p.ej. que han tenido pareja), no sobre la población total.

5. LENGUAJE: Usar "personas que han experimentado violencia", no "víctimas"
   (que puede ser estigmatizante). No usar "violencia doméstica" — oscurece
   el perpetrador; usar "violencia ejercida por la pareja íntima".
```

### Código para análisis de prevalencia con contexto

```python
def analizar_prevalencia_violencia(df, tipo_violencia_col, factores):
    """
    tipo_violencia_col: columna binaria (1=experimentó violencia, 0=no)
    factores: lista de variables contextuales a cruzar
    """
    
    # Prevalencia general con IC al 95%
    n = len(df)
    p = df[tipo_violencia_col].mean()
    ic_inf = p - 1.96 * np.sqrt(p*(1-p)/n)
    ic_sup = p + 1.96 * np.sqrt(p*(1-p)/n)
    
    print(f"Prevalencia: {p:.1%} (IC95%: {ic_inf:.1%} - {ic_sup:.1%}, n={n})")
    print("⚠️  Nota: dato basado en encuesta; el sub-registro es sustancial\n")
    
    # Prevalencia por factores contextuales
    for factor in factores:
        tabla = df.groupby(factor)[tipo_violencia_col].agg(
            prevalencia='mean',
            n='count'
        ).round(3)
        tabla['prevalencia_pct'] = (tabla['prevalencia'] * 100).round(1)
        print(f"--- Por {factor} ---")
        print(tabla[['prevalencia_pct', 'n']])
        print()
    
    return None
```

---

## Ejemplo 3: Cruce de datos de participación política

### Variables típicas en censos electorales
- Cargo (presidencia, congreso, alcaldía, concejo)
- Nivel territorial (nacional, estatal, municipal)
- Partido político
- Resultado (electo/a, candidato/a)
- Año de elección

### Métricas clave

```python
def indice_paridad_politica(df, cargo_col, sexo_col, resultado_col):
    """
    Calcula índice de paridad para cargos electivos.
    Retorna tabla con % mujeres electas por tipo de cargo.
    """
    
    electos = df[df[resultado_col] == 'Electo/a']
    
    paridad = electos.groupby(cargo_col)[sexo_col].apply(
        lambda x: (x == 'Mujer').sum() / len(x)
    ).rename('pct_mujeres').reset_index()
    
    paridad['indice_paridad'] = paridad['pct_mujeres'] / 0.5  # 0.5 = paridad
    paridad['semáforo'] = paridad['indice_paridad'].apply(
        lambda x: '🔴 Crítico' if x < 0.5 else ('🟡 Bajo' if x < 0.8 else '🟢 Paridad')
    )
    
    print("\n=== PARIDAD EN CARGOS ELECTIVOS ===")
    print(paridad.to_string(index=False))
    print("\nReferencia: Índice de paridad 1.0 = 50% mujeres electas")
    
    return paridad
```

---

## Plantilla de reporte con perspectiva feminista

```markdown
# Análisis de [TEMA] con perspectiva de feminismo de datos

## 1. Sobre los datos
- **Fuente**: [nombre, institución, año]
- **Universo**: [quiénes están incluidos]
- **Grupos ausentes**: [quiénes no están y por qué importa]
- **Metodología de recolección**: [cómo se levantaron los datos]
- **Limitaciones conocidas**: [sesgos, sub-registros, definiciones]

## 2. Hallazgos principales
### 2.1 Brecha general
[Dato principal con contexto]

### 2.2 Análisis interseccional
[Cómo varían las brechas según combinaciones de factores]

### 2.3 Quién concentra la desventaja
[El grupo o grupos con peores indicadores acumulados]

## 3. Contexto estructural
[Factores históricos, normativos, culturales que explican los patrones]

## 4. Lo que los datos no dicen
[Variables que faltan, dimensiones no capturadas, perspectivas ausentes]

## 5. Implicaciones para política pública / acción
[Qué demanda la evidencia en términos de intervenciones]

---
*Análisis realizado con enfoque de feminismo de datos basado en D'Ignazio & Klein (2020)*
*Datos disponibles para descarga/verificación en: [link]*
```
