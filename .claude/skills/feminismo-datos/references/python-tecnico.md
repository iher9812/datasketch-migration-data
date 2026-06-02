# Python Técnico para Análisis Feminista de Datos

Basado en: Grus, J. (2019). *Ciencia de datos desde cero: Principios básicos con Python*.
Adaptado para investigación social con enfoque de feminismo de datos.

---

## Tabla de contenidos
1. [Estadística descriptiva](#estadistica)
2. [Correlación y la Paradoja de Simpson](#correlacion)
3. [Pruebas de hipótesis e intervalos de confianza](#hipotesis)
4. [Limpieza y exploración de datos](#limpieza)
5. [Visualización con matplotlib/seaborn](#visualizacion)
6. [Reducción de dimensionalidad (PCA)](#pca)
7. [Modelos de clasificación](#clasificacion)
8. [Clustering interseccional](#clustering)
9. [NLP para encuestas cualitativas](#nlp)
10. [Auditoría de equidad algorítmica](#equidad)

---

## 1. Estadística descriptiva {#estadistica}

```python
from typing import List
import math
from collections import Counter

# --- TENDENCIAS CENTRALES ---

def media(xs: List[float]) -> float:
    return sum(xs) / len(xs)

def mediana(xs: List[float]) -> float:
    """Preferir sobre la media para ingresos y distribuciones sesgadas"""
    n = len(xs)
    sorted_xs = sorted(xs)
    midpoint = n // 2
    if n % 2 == 1:
        return sorted_xs[midpoint]
    else:
        return (sorted_xs[midpoint - 1] + sorted_xs[midpoint]) / 2

# --- DISPERSIÓN ---

def rango_intercuartil(xs: List[float]) -> float:
    """Más robusto que la desviación estándar ante outliers (p.ej. salarios extremos)"""
    sorted_xs = sorted(xs)
    n = len(sorted_xs)
    q1 = sorted_xs[n // 4]
    q3 = sorted_xs[3 * n // 4]
    return q3 - q1

def desviacion_estandar(xs: List[float]) -> float:
    m = media(xs)
    varianza = sum((x - m) ** 2 for x in xs) / (len(xs) - 1)
    return math.sqrt(varianza)

# --- RESUMEN ESTADÍSTICO FEMINISTA ---
# Siempre calcular para CADA subgrupo, nunca solo el agregado

def resumen_por_grupo(df, variable, grupo='sexo'):
    """
    Genera estadísticas descriptivas desagregadas.
    Aplica el principio: los datos nunca hablan solos — contexto primero.
    """
    import pandas as pd
    
    resultado = df.groupby(grupo)[variable].agg([
        ('n', 'count'),
        ('media', 'mean'),
        ('mediana', 'median'),
        ('desv_std', 'std'),
        ('q25', lambda x: x.quantile(0.25)),
        ('q75', lambda x: x.quantile(0.75)),
        ('minimo', 'min'),
        ('maximo', 'max')
    ]).round(2)
    
    # Calcular ratio de paridad (valor_grupo / valor_referencia)
    if len(resultado) >= 2:
        grupos = resultado.index.tolist()
        for col in ['media', 'mediana']:
            max_val = resultado[col].max()
            resultado[f'ratio_paridad_{col}'] = (resultado[col] / max_val).round(3)
    
    print(f"\n📊 Estadísticas de '{variable}' por '{grupo}':")
    print(resultado.to_string())
    print(f"\n⚠️  Nota: n < 30 en algún grupo requiere cautela interpretativa")
    
    return resultado
```

---

## 2. Correlación y la Paradoja de Simpson {#correlacion}

```python
def correlacion(xs: List[float], ys: List[float]) -> float:
    """
    Coeficiente de correlación de Pearson.
    IMPORTANTE: correlación ≠ causalidad.
    """
    n = len(xs)
    mx, my = media(xs), media(ys)
    sdx, sdy = desviacion_estandar(xs), desviacion_estandar(ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / ((n - 1) * sdx * sdy)


def detectar_paradoja_simpson(df, variable_resultado, variable_explicativa, variable_grupo):
    """
    Verifica si la correlación agregada invierte su signo al desagregar por grupo.
    Crítico en análisis feministas: una tendencia "positiva" global puede ocultar
    discriminación sistemática en subgrupos.
    
    Ejemplo clásico: admisiones a Berkeley parecían favorecer a mujeres en global,
    pero dentro de cada departamento favorecían a hombres (sesgo de autoselección).
    """
    import pandas as pd
    import numpy as np
    
    # Correlación global
    r_global = df[[variable_resultado, variable_explicativa]].corr().iloc[0,1]
    
    # Correlación por subgrupo
    correlaciones_grupo = {}
    for grupo, subdf in df.groupby(variable_grupo):
        if len(subdf) > 5:
            r = subdf[[variable_resultado, variable_explicativa]].corr().iloc[0,1]
            correlaciones_grupo[grupo] = r
    
    # Detectar inversión
    signo_global = "positiva" if r_global > 0 else "negativa"
    inversos = [g for g, r in correlaciones_grupo.items() 
                if (r > 0) != (r_global > 0)]
    
    print(f"\n🔍 ANÁLISIS DE PARADOJA DE SIMPSON")
    print(f"Correlación global {variable_resultado} ~ {variable_explicativa}: r = {r_global:.3f} ({signo_global})")
    print(f"\nCorrelaciones por {variable_grupo}:")
    for g, r in correlaciones_grupo.items():
        signo = "✅ misma dirección" if g not in inversos else "⚠️ DIRECCIÓN OPUESTA"
        print(f"  {g}: r = {r:.3f} {signo}")
    
    if inversos:
        print(f"\n🚨 PARADOJA DE SIMPSON DETECTADA en grupos: {inversos}")
        print("   La tendencia global NO refleja la realidad de estos subgrupos.")
        print("   Reportar los resultados desagregados, no el agregado.")
    
    return r_global, correlaciones_grupo
```

---

## 3. Pruebas de hipótesis e intervalos de confianza {#hipotesis}

```python
import scipy.stats as stats
import numpy as np

def prueba_diferencia_grupos(grupo_a, grupo_b, nombre_a="Grupo A", nombre_b="Grupo B",
                              alpha=0.05):
    """
    Prueba t de Welch para comparar medias entre dos grupos.
    Más robusto que t de Student cuando los grupos tienen varianzas distintas
    (común en datos sociales desagregados por género).
    
    Reporta intervalo de confianza además del p-valor.
    """
    t_stat, p_valor = stats.ttest_ind(grupo_a, grupo_b, equal_var=False)
    
    # Intervalo de confianza para la diferencia
    diferencia = np.mean(grupo_a) - np.mean(grupo_b)
    se = np.sqrt(np.var(grupo_a)/len(grupo_a) + np.var(grupo_b)/len(grupo_b))
    ic_inf = diferencia - 1.96 * se
    ic_sup = diferencia + 1.96 * se
    
    # Tamaño del efecto (d de Cohen)
    sd_pooled = np.sqrt((np.var(grupo_a) + np.var(grupo_b)) / 2)
    d_cohen = diferencia / sd_pooled if sd_pooled > 0 else 0
    
    print(f"\n📊 COMPARACIÓN: {nombre_a} vs {nombre_b}")
    print(f"  Media {nombre_a}: {np.mean(grupo_a):.2f} (n={len(grupo_a)})")
    print(f"  Media {nombre_b}: {np.mean(grupo_b):.2f} (n={len(grupo_b)})")
    print(f"  Diferencia: {diferencia:.2f}")
    print(f"  IC 95%: [{ic_inf:.2f}, {ic_sup:.2f}]")
    print(f"  p-valor: {p_valor:.4f} {'✅ significativo' if p_valor < alpha else '❌ no significativo'}")
    print(f"  Tamaño del efecto (d de Cohen): {d_cohen:.2f}")
    
    # Interpretación del tamaño del efecto
    if abs(d_cohen) < 0.2:
        efecto = "pequeño (puede ser estadísticamente significativo pero poco relevante)"
    elif abs(d_cohen) < 0.5:
        efecto = "mediano"
    else:
        efecto = "grande"
    print(f"  Magnitud del efecto: {efecto}")
    print(f"\n⚠️  Nota: significancia estadística ≠ relevancia práctica o social")
    
    return {'diferencia': diferencia, 'ic': (ic_inf, ic_sup), 'p': p_valor, 'd': d_cohen}


def bootstrap_brecha(grupo_a, grupo_b, n_bootstrap=1000, estadistico=np.mean):
    """
    Estimación bootstrap del IC para brechas entre grupos.
    Útil cuando los supuestos de normalidad no se cumplen.
    Basado en el concepto de bootstrap de Grus cap. 15.
    """
    brechas = []
    for _ in range(n_bootstrap):
        muestra_a = np.random.choice(grupo_a, size=len(grupo_a), replace=True)
        muestra_b = np.random.choice(grupo_b, size=len(grupo_b), replace=True)
        brechas.append(estadistico(muestra_a) - estadistico(muestra_b))
    
    ic_inf = np.percentile(brechas, 2.5)
    ic_sup = np.percentile(brechas, 97.5)
    
    print(f"\n🔁 Bootstrap IC 95% para la brecha: [{ic_inf:.2f}, {ic_sup:.2f}]")
    print(f"   (basado en {n_bootstrap} remuestras)")
    
    return ic_inf, ic_sup
```

---

## 4. Limpieza y exploración de datos {#limpieza}

```python
import pandas as pd

def explorar_dataset_feminista(df):
    """
    Exploración inicial con lente feminista.
    Documenta ausencias como hallazgos, no solo como problemas técnicos.
    """
    print("=" * 60)
    print("EXPLORACIÓN FEMINISTA DEL DATASET")
    print("=" * 60)
    
    print(f"\n📐 Dimensiones: {df.shape[0]} filas × {df.shape[1]} columnas")
    
    # Tipos de variables
    print(f"\n📋 Variables disponibles:")
    for col in df.columns:
        dtype = df[col].dtype
        n_unique = df[col].nunique()
        n_missing = df[col].isnull().sum()
        pct_missing = 100 * n_missing / len(df)
        print(f"  {col}: {dtype} | {n_unique} valores únicos | {pct_missing:.1f}% faltante")
    
    # Verificar variable de género
    posibles_genero = [c for c in df.columns if any(p in c.lower() 
                        for p in ['sexo', 'genero', 'gender', 'sex'])]
    if posibles_genero:
        print(f"\n✅ Variables de género encontradas: {posibles_genero}")
        for var in posibles_genero:
            print(f"\n  Distribución de '{var}':")
            print(df[var].value_counts(normalize=True).round(3).to_string())
            if df[var].nunique() <= 2:
                print(f"  ⚠️  Solo 2 categorías — posible codificación binaria excluyente")
    else:
        print("\n🚨 ALERTA: No se detectó variable de sexo/género")
        print("   Los datos pueden estar sin desagregar — verificar documentación")
    
    # Datos faltantes por grupo si hay variable de género
    if posibles_genero:
        var_gen = posibles_genero[0]
        print(f"\n📊 Valores faltantes por {var_gen} (la ausencia como dato):")
        missing_por_grupo = df.groupby(var_gen).apply(
            lambda x: x.isnull().sum()
        ).T
        print(missing_por_grupo[missing_por_grupo.sum(axis=1) > 0].to_string())
    
    return None


def limpiar_con_documentacion(df, decisiones_log=None):
    """
    Limpieza documentada — aplica el principio 'Hacer visible el trabajo'.
    decisiones_log: lista donde se agregan las decisiones tomadas.
    """
    if decisiones_log is None:
        decisiones_log = []
    
    df_limpio = df.copy()
    
    # Registrar estado inicial
    n_inicial = len(df_limpio)
    decisiones_log.append(f"Dataset inicial: {n_inicial} registros")
    
    # Duplicados
    n_dupes = df_limpio.duplicated().sum()
    if n_dupes > 0:
        df_limpio = df_limpio.drop_duplicates()
        decisiones_log.append(f"Eliminados {n_dupes} registros duplicados")
    
    print("📝 Log de decisiones de limpieza:")
    for d in decisiones_log:
        print(f"   - {d}")
    print("\nEsta documentación debe incluirse en el reporte final.")
    
    return df_limpio, decisiones_log
```

---

## 5. Visualización con perspectiva feminista {#visualizacion}

```python
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np

# Paleta accesible (no usa rojo/azul estereotípico de género)
PALETA_FEMINISTA = {
    'primario': '#4C72B0',
    'secundario': '#DD8452', 
    'terciario': '#55A868',
    'cuaternario': '#C44E52',
    'neutro': '#8C8C8C'
}

def grafico_brecha(df, variable, grupo='sexo', titulo=None):
    """
    Visualiza brecha entre grupos con IC.
    Título descriptivo que nombra la desigualdad, no la neutraliza.
    """
    stats = df.groupby(grupo)[variable].agg(['mean', 'sem', 'count']).reset_index()
    
    fig, ax = plt.subplots(figsize=(8, 5))
    
    colores = list(PALETA_FEMINISTA.values())
    bars = ax.barh(stats[grupo], stats['mean'],
                   xerr=1.96 * stats['sem'],
                   color=colores[:len(stats)],
                   alpha=0.85, capsize=4)
    
    # Añadir n en cada barra
    for i, (_, row) in enumerate(stats.iterrows()):
        ax.text(0.02, i, f"n={int(row['count'])}", 
                va='center', fontsize=9, color='white', fontweight='bold')
    
    # Título que nombra, no solo describe
    if titulo:
        ax.set_title(titulo, fontsize=13, pad=12)
    
    ax.set_xlabel(variable)
    ax.axvline(0, color='black', linewidth=0.5)
    
    # Línea de paridad si aplica
    if stats['mean'].min() > 0:
        media_global = df[variable].mean()
        ax.axvline(media_global, color='gray', linestyle='--', alpha=0.7,
                   label=f'Promedio global: {media_global:.1f}')
        ax.legend(fontsize=9)
    
    plt.tight_layout()
    return fig


def violin_interseccional(df, variable, var_x, var_color, titulo=None):
    """
    Violin plot para mostrar distribución completa (no solo media).
    Útil para revelar desigualdad dentro de grupos.
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    sns.violinplot(data=df, x=var_x, y=variable, hue=var_color,
                   split=True, inner='quart', ax=ax,
                   palette=list(PALETA_FEMINISTA.values())[:2])
    
    if titulo:
        ax.set_title(titulo, fontsize=13)
    
    ax.set_xlabel(var_x)
    ax.set_ylabel(variable)
    
    # Nota contextual obligatoria
    fig.text(0.5, -0.02, 
             '* Las líneas internas muestran cuartiles. Ancho = densidad de observaciones.',
             ha='center', fontsize=8, style='italic', color='gray')
    
    plt.tight_layout()
    return fig
```

---

## 6. Reducción de dimensionalidad (PCA) {#pca}

```python
def pca_interseccional(df, variables_numericas, variable_grupo=None, n_componentes=2):
    """
    PCA para explorar estructura en datos sociales multidimensionales.
    Útil para descubrir patrones de desigualdad sin imponer categorías previas.
    Aplica el principio 'Abrazar el pluralismo': los datos revelan su propia estructura.
    """
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
    import pandas as pd
    import matplotlib.pyplot as plt
    
    # Estandarizar (necesario para PCA — distancias comparables)
    X = df[variables_numericas].dropna()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Ajustar PCA
    pca = PCA(n_components=n_componentes)
    componentes = pca.fit_transform(X_scaled)
    
    varianza_explicada = pca.explained_variance_ratio_
    print(f"\n📊 PCA — Varianza explicada:")
    for i, v in enumerate(varianza_explicada):
        print(f"  Componente {i+1}: {v:.1%}")
    print(f"  Total: {sum(varianza_explicada):.1%}")
    
    # Cargas (qué variables contribuyen más a cada componente)
    print(f"\n📋 Cargas de variables por componente:")
    cargas = pd.DataFrame(pca.components_.T, 
                           index=variables_numericas,
                           columns=[f'CP{i+1}' for i in range(n_componentes)])
    print(cargas.round(3).to_string())
    
    # Visualizar si hay variable de grupo
    if variable_grupo is not None:
        df_comp = pd.DataFrame(componentes, columns=['CP1', 'CP2'])
        grupos = df[variable_grupo].values[X.index]
        df_comp[variable_grupo] = grupos
        
        fig, ax = plt.subplots(figsize=(8, 6))
        for grupo, color in zip(df_comp[variable_grupo].unique(), 
                                 list(PALETA_FEMINISTA.values())):
            subset = df_comp[df_comp[variable_grupo] == grupo]
            ax.scatter(subset['CP1'], subset['CP2'], 
                      label=grupo, alpha=0.6, color=color)
        
        ax.set_xlabel(f'CP1 ({varianza_explicada[0]:.1%} varianza)')
        ax.set_ylabel(f'CP2 ({varianza_explicada[1]:.1%} varianza)')
        ax.legend()
        ax.set_title('Estructura de datos por grupos — PCA')
        plt.tight_layout()
    
    return pca, componentes
```

---

## 7. Modelos de clasificación con auditoría de equidad {#clasificacion}

```python
def regresion_logistica_interpretable(df, variable_resultado, predictores, 
                                       variable_protegida='sexo'):
    """
    Regresión logística con:
    1. Coeficientes interpretados substantivamente
    2. Auditoría de equidad por grupo protegido
    
    La interpretabilidad es un requisito ético en investigación social.
    """
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, confusion_matrix
    import pandas as pd
    import numpy as np
    
    df_modelo = df[predictores + [variable_resultado, variable_protegida]].dropna()
    
    X = pd.get_dummies(df_modelo[predictores], drop_first=True)
    y = df_modelo[variable_resultado]
    grupos = df_modelo[variable_protegida]
    
    X_train, X_test, y_train, y_test, g_train, g_test = train_test_split(
        X, y, grupos, test_size=0.3, random_state=42, stratify=y
    )
    
    modelo = LogisticRegression(max_iter=1000)
    modelo.fit(X_train, y_train)
    
    y_pred = modelo.predict(X_test)
    
    # Reporte general
    print("📊 DESEMPEÑO GENERAL:")
    print(classification_report(y_test, y_pred))
    
    # Auditoría de equidad por grupo protegido
    print(f"\n⚖️  AUDITORÍA DE EQUIDAD por '{variable_protegida}':")
    print("(¿El modelo funciona igualmente bien para todos los grupos?)\n")
    
    for grupo in g_test.unique():
        mascara = g_test == grupo
        if mascara.sum() > 10:
            reporte = classification_report(y_test[mascara], y_pred[mascara], 
                                           output_dict=True)
            exactitud = reporte['accuracy']
            print(f"  {grupo}: exactitud = {exactitud:.3f} (n={mascara.sum()})")
    
    print("\n⚠️  Si la exactitud varía >5pp entre grupos, el modelo tiene sesgo algorítmico")
    print("   No usar este modelo para tomar decisiones sobre grupos con menor exactitud\n")
    
    # Coeficientes
    coef_df = pd.DataFrame({
        'variable': X.columns,
        'coeficiente': modelo.coef_[0],
        'odds_ratio': np.exp(modelo.coef_[0])
    }).sort_values('coeficiente', key=abs, ascending=False)
    
    print("📋 Coeficientes (ordenados por magnitud):")
    print(coef_df.round(3).to_string(index=False))
    
    return modelo, coef_df
```

---

## 8. Clustering interseccional {#clustering}

```python
def clustering_sin_binarios(df, variables, n_clusters_max=6, variable_grupo=None):
    """
    K-means para descubrir grupos naturales en los datos.
    Aplica el principio 'Repensar binarios': los datos pueden revelar
    más de 2 grupos sin que nosotros los impongamos.
    """
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    import pandas as pd
    import matplotlib.pyplot as plt
    
    X = df[variables].dropna()
    X_scaled = StandardScaler().fit_transform(X)
    
    # Elegir k óptimo (método del codo)
    inercias = []
    ks = range(2, n_clusters_max + 1)
    for k in ks:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        km.fit(X_scaled)
        inercias.append(km.inertia_)
    
    # Gráfico del codo
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(ks, inercias, 'bo-')
    ax.set_xlabel('Número de clusters (k)')
    ax.set_ylabel('Inercia')
    ax.set_title('Método del codo — ¿Cuántos grupos naturales hay?')
    plt.tight_layout()
    plt.show()
    
    print(f"\nRevisa el gráfico: elige k donde la curva 'dobla el codo'")
    print("Nota: más clusters no siempre significa más insight — prefiere interpretabilidad")
    
    # Ajustar con k elegido (aquí usamos 3 por defecto, cambiar según análisis)
    k_optimo = 3
    km_final = KMeans(n_clusters=k_optimo, random_state=42, n_init=10)
    etiquetas = km_final.fit_predict(X_scaled)
    
    df_result = X.copy()
    df_result['cluster'] = etiquetas
    
    # Describir cada cluster
    print(f"\n📊 Descripción de {k_optimo} clusters:")
    print(df_result.groupby('cluster')[variables].mean().round(2).to_string())
    
    # Si hay variable de grupo, ver composición
    if variable_grupo and variable_grupo in df.columns:
        comp = pd.crosstab(etiquetas, df[variable_grupo].values[X.index], 
                           normalize='index').round(3)
        print(f"\n📋 Composición por '{variable_grupo}' en cada cluster:")
        print(comp.to_string())
    
    return km_final, etiquetas
```

---

## 9. NLP para preguntas abiertas de encuestas {#nlp}

```python
def analizar_respuestas_abiertas(df, columna_texto, columna_grupo, 
                                  n_palabras_top=20):
    """
    Análisis de frecuencia de términos en preguntas abiertas de encuestas,
    desagregado por grupo demográfico.
    
    Revela narrativas diferenciadas: ¿qué temas menciona cada grupo?
    """
    from collections import Counter
    import re
    
    # Stopwords básicas en español
    stopwords = {'de', 'la', 'el', 'en', 'y', 'que', 'a', 'los', 'las',
                 'es', 'se', 'un', 'una', 'con', 'no', 'por', 'para',
                 'del', 'al', 'lo', 'su', 'sus', 'mi', 'me', 'más',
                 'como', 'pero', 'o', 'le', 'si', 'son', 'hay', 'ya',
                 'porque', 'cuando', 'muy', 'también', 'he', 'era'}
    
    def tokenizar(texto):
        if not isinstance(texto, str):
            return []
        texto = texto.lower()
        texto = re.sub(r'[^\w\s]', '', texto)
        palabras = texto.split()
        return [p for p in palabras if p not in stopwords and len(p) > 2]
    
    print(f"📝 ANÁLISIS DE RESPUESTAS ABIERTAS")
    print(f"   Variable: {columna_texto}")
    print(f"   Desagregado por: {columna_grupo}\n")
    
    resultados = {}
    for grupo in df[columna_grupo].dropna().unique():
        textos = df[df[columna_grupo] == grupo][columna_texto].dropna()
        todas_palabras = []
        for texto in textos:
            todas_palabras.extend(tokenizar(texto))
        
        frecuencias = Counter(todas_palabras).most_common(n_palabras_top)
        resultados[grupo] = frecuencias
        
        print(f"  Grupo '{grupo}' (n={len(textos)} respuestas):")
        print(f"  Top {min(10, n_palabras_top)} términos: {[p for p, _ in frecuencias[:10]]}")
        print()
    
    # Términos exclusivos por grupo (lo que un grupo menciona y otro no)
    if len(resultados) >= 2:
        grupos = list(resultados.keys())
        for i in range(len(grupos)):
            terminos_i = set(p for p, _ in resultados[grupos[i]])
            terminos_otros = set()
            for j in range(len(grupos)):
                if i != j:
                    terminos_otros.update(p for p, _ in resultados[grupos[j]])
            exclusivos = terminos_i - terminos_otros
            if exclusivos:
                print(f"  🔍 Términos únicos del grupo '{grupos[i]}': {list(exclusivos)[:10]}")
    
    print("\n⚠️  Nota: frecuencia ≠ importancia. Interpretar en contexto cualitativo.")
    
    return resultados
```

---

## 10. Auditoría de equidad algorítmica {#equidad}

```python
def auditoria_equidad_completa(y_true, y_pred, grupos, nombre_grupos='grupo'):
    """
    Auditoría sistemática de sesgo en modelos predictivos.
    Basado en principios de ética de datos (Grus cap. 26) + Data Feminism.
    
    Métricas calculadas por grupo:
    - Exactitud (accuracy)
    - Tasa de falsos positivos (FPR) 
    - Tasa de falsos negativos (FNR)
    - Disparate impact ratio
    """
    import pandas as pd
    from sklearn.metrics import confusion_matrix
    
    print("⚖️  AUDITORÍA DE EQUIDAD ALGORÍTMICA")
    print("=" * 50)
    
    metricas = {}
    predicciones_positivas = {}
    
    for grupo in pd.Series(grupos).unique():
        mascara = pd.Series(grupos) == grupo
        yt = pd.Series(y_true)[mascara]
        yp = pd.Series(y_pred)[mascara]
        
        n = len(yt)
        if n < 10:
            print(f"  {grupo}: n={n} — muestra insuficiente para auditoría")
            continue
        
        tn, fp, fn, tp = confusion_matrix(yt, yp).ravel() if yt.nunique() > 1 else (0,0,0,0)
        
        exactitud = (tp + tn) / n if n > 0 else 0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0  # Falso positivo: dañino (ej. crédito negado)
        fnr = fn / (fn + tp) if (fn + tp) > 0 else 0  # Falso negativo: dañino (ej. diagnóstico perdido)
        pct_prediccion_positiva = (tp + fp) / n
        
        metricas[grupo] = {
            'n': n, 'exactitud': exactitud,
            'tasa_FP': fpr, 'tasa_FN': fnr,
            'pct_pred_positiva': pct_prediccion_positiva
        }
        predicciones_positivas[grupo] = pct_prediccion_positiva
        
        print(f"\n  Grupo '{grupo}' (n={n}):")
        print(f"    Exactitud: {exactitud:.3f}")
        print(f"    Tasa de falsos positivos: {fpr:.3f}")
        print(f"    Tasa de falsos negativos: {fnr:.3f}")
    
    # Disparate Impact Ratio (estándar legal: ratio < 0.8 = impacto desproporcionado)
    if len(predicciones_positivas) >= 2:
        grupos_lista = list(predicciones_positivas.keys())
        max_pp = max(predicciones_positivas.values())
        
        print(f"\n  📊 Disparate Impact Ratio (referencia: >= 0.8 = equitativo):")
        for grupo, pp in predicciones_positivas.items():
            ratio = pp / max_pp if max_pp > 0 else 1
            semaforo = "🟢" if ratio >= 0.8 else ("🟡" if ratio >= 0.6 else "🔴")
            print(f"    {grupo}: {ratio:.3f} {semaforo}")
    
    print(f"\n⚠️  Un modelo con sesgo no debe usarse para tomar decisiones")
    print("   que afecten a los grupos perjudicados.")
    
    return metricas
```

---

## Referencias técnicas

- Grus, J. (2019). *Data Science from Scratch*. O'Reilly.
- Pedregosa et al. (2011). Scikit-learn: Machine Learning in Python. *JMLR 12*, 2825-2830.
- D'Ignazio, C. & Klein, L.F. (2020). *Data Feminism*. MIT Press.
- Chouldechova, A. (2017). Fair prediction with disparate impact. *Big Data 5*(2).
