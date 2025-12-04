

## Vivienda Processamiento de datos - unión y limpieza
## =====================================================:

## Librerias

import pandas as pd
from pathlib import Path
import numpy as np
import os
import datetime as dt
import warnings
import re, unicodedata

warnings.filterwarnings("ignore")

# Fijar directorio
DATA_DIR = Path(rf"C:\Users\PC\Desktop\Proyectos\Proyectos_Py\1.Analisis Vivienda\Analisis_Vivienda\data\raw")
DATA_OUT = Path(rf"C:\Users\PC\Desktop\Proyectos\Proyectos_Py\1.Analisis Vivienda\Analisis_Vivienda\data\processed")

# Lista todos los archivos .csv
csv_files = sorted(DATA_DIR.glob("*.csv"))
print(f"Se listan {len(csv_files)} archivos a procesar:")
for f in csv_files:
    print("-", f.name)

## Lectura de datos
data_raw = []
cols_by_file = {}
for file in csv_files:
    df = pd.read_csv(file, sep="|")
    df["file_origin"] = file.name
    data_raw.append(df)
    cols_by_file[file.name] = set(df.columns)
    
print("\nproceso cargado!")
print("\nUniendo datos!")

raw_all = pd.concat(data_raw, ignore_index=True)
print("Filas totales:", len(raw_all))
print("Columnas:", list(raw_all.columns))


print("\nLimpieza de datos!")

## Limpieza de datos - duplicados Otros. 

dups = raw_all["enlace"].duplicated(keep=False)
print("Registros duplicados por enlace:", dups.sum())

# ¿Cuántos enlaces únicos?
print("Enlaces únicos:", raw_all["enlace"].nunique())

## removeremos duplicados.
raw_all_nd = raw_all.drop_duplicates(subset=["enlace"], keep="first") 
print("se tiene solo enlaces unicos:", raw_all_nd["enlace"].nunique())



## Validando y corrigiendo distritos. 

valores = {
    "Brena": "Breña",
    "Jesus Maria": "Jesús María",
    "San Martin De Porres": "San Martín de Porres",
    "Lurin": "Lurín",
    "Ancon": "Ancón",
    "Santa Maria Del Mar": "Santa María del Mar",
    "Villa Maria Del Triunfo": "Villa María del Triunfo",
}

s = (raw_all_nd["distrito"]
        .astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True))

raw_all_nd["distrito_2"] = s.replace(valores)   # crea la nueva columna

raw_all_nd["distrito_norm"] = raw_all_nd["distrito_2"].str.lower().str.strip()
raw_all_nd["direccion_norm"] = raw_all_nd["direccion"].str.lower().str.strip()

raw_all_nd["distrito_en_direccion"] = raw_all_nd.apply(
    lambda row: row["distrito_norm"] in row["direccion_norm"],
    axis=1
)

cols = [ #"distrito_2", "direccion", 
        "distrito_norm", "direccion_norm", "distrito_en_direccion"]
raw_all_nd[raw_all_nd["distrito_en_direccion"]==False][cols]
df_arreglar = raw_all_nd[raw_all_nd["distrito_en_direccion"]==False].copy()##[["distrito", "direccion", "enlace"]]

canon = {
    # canónico : [alias que podrían aparecer en la dirección]
    "Ate Vitarte": ["ate vitarte", "ate"],
    "Breña": ["breña", "brena"],
    "Carabayllo": ["carabayllo"],
    "Chaclacayo": ["chaclacayo"],
    "El Agustino": ["el agustino", "agustino"],
    "Independencia": ["independencia"],
    "Jesús María": ["jesus maria", "jesús maria", "jesus maría"],
    "Chosica Lurigancho": [ "chosica"], ##"chosica lurigancho", "lurigancho-chosica",
    "Lurín": ["lurin", "lurín"],
    "Pachacámac": ["pachacamac", "pachacámac"],
    "Pucusana": ["pucusana"],
    "Puente Piedra": ["puente piedra"],
    "Punta Negra": ["punta negra"],
    "Rímac": ["rimac", "rímac"],
    "San Juan De Miraflores": ["san juan de miraflores", "sjm"],
    "San Luis": ["san luis"],
    "San Martín De Porres": ["san martin de porres", "san martín de porres", "smp"],
    "Villa María Del Triunfo": ["villa maria del triunfo", "villa maría del triunfo", "vmt"],
    "Ancón": ["ancon", "ancón"],
    "Lince": ["lince"],
    "Santa Rosa": ["santa rosa"],
    "Barranco": ["barranco"],
    "Magdalena": ["magdalena del mar", "magdalena"],
    "Punta Hermosa": ["punta hermosa"],
    "Santiago De Surco": ["santiago de surco", "surco"],
    "San Juan De Lurigancho": ["san juan de lurigancho"],
    "Lima Cercado" : ["cercado", "cercado de lima", "lima cercado"],
    "Los Olivos" : ["los olivos"],
    "Comas" : ["comas"],
    "San Bartolo" : ["san bartolo"], 
    'Villa El Salvador' : ["villa el salvador"],
    "Santa Maria del Mar": ["santa maria del mar"],
    "San Isidro" : ["san isidro"],
    "La Molina" : ["la molina"]
    # agrega aquí el resto hasta completar 43 distritos
}


def strip_accents(s):
    if not isinstance(s, str):
        return s
    return ''.join(ch for ch in unicodedata.normalize("NFD", s) if unicodedata.category(ch) != "Mn")

df_arreglar["dir_norm"]  = df_arreglar["direccion"].astype(str).str.lower().str.replace(r"\s+", " ", regex=True).map(strip_accents)
df_arreglar["dist_norm"] = df_arreglar["distrito_2"].astype(str).str.lower().str.replace(r"\s+", " ", regex=True).map(strip_accents)

# precompila patrones regex alias → canónico
patterns = []
for canon_name, aliases in canon.items():
    for alias in aliases:
        pat = re.compile(rf"\b{re.escape(strip_accents(alias))}\b")
        patterns.append((canon_name, pat))

def candidates_from_address(addr_norm: str):
    if not isinstance(addr_norm, str):
        return []
    hits = []
    for canon_name, pat in patterns:
        if pat.search(addr_norm):
            hits.append(canon_name)
    # quitar duplicados preservando orden
    return  list(dict.fromkeys(hits))

df_arreglar["dist_candidates"] = df_arreglar["dir_norm"].map(candidates_from_address)
df_arreglar["distrito_candidato"] = df_arreglar["dist_candidates"].str.get(0) 


data_p1 = raw_all_nd[raw_all_nd["distrito_en_direccion"]==True]

cols_obj =['fuente', 'inmueble', 'operacion', 'distrito', 'zona', 'direccion', 'precio',
            'soles', 'dolares', 'variacion', 'mantenimiento', 'caracteristica',
            'area', 'dormitorio', 'baños', 'estacionamientos', 'detalle', 'enlace',
            'fecha', 'file_origin', 'distrito_candidato', 'distrito_norm',
            'direccion_norm', 'distrito_en_direccion']

data_p2 = df_arreglar[df_arreglar["distrito_candidato"].notna()][cols_obj].copy()

data_p2.columns = ['fuente', 'inmueble', 'operacion', 'distrito', 'zona', 'direccion', 'precio',
            'soles', 'dolares', 'variacion', 'mantenimiento', 'caracteristica',
            'area', 'dormitorio', 'baños', 'estacionamientos', 'detalle', 'enlace',
            'fecha', 'file_origin', 'distrito_2', 'distrito_norm',
            'direccion_norm', 'distrito_en_direccion']

data_vivienda = pd.concat([data_p1, data_p2], axis=0)

def normalizar(texto: str) -> str:
    # 1. Pasar a minúsculas
    texto = texto.lower()
    # 2. Quitar acentos
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    # 3. Quitar dobles espacios y limpiar
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto


data_vivienda["distrito_oficial"] = data_vivienda["distrito_2"].apply(normalizar)


print("\nCreacion de variables!")

cols_analisis = ['fuente','inmueble','operacion',
                'distrito','distrito_2', 'distrito_oficial', 'zona',
                'direccion','precio',
                'soles','dolares','variacion','mantenimiento','caracteristica',
                'area','dormitorio','baños','estacionamientos','detalle','enlace',
                'fecha','file_origin']
data_analisis = data_vivienda[cols_analisis].copy()

# Normalizaciones básicas
data_analisis["fuente"] = data_analisis["fuente"].astype(str).str.strip().str.lower()
data_analisis["distrito_final"] = data_analisis["distrito_oficial"].astype(str).str.strip().str.title()
data_analisis["inmueble"] = data_analisis["inmueble"].astype(str).str.strip().str.lower()
data_analisis["operacion"] = data_analisis["operacion"].astype(str).str.strip().str.lower()
data_analisis["precio_pen"] = data_analisis["soles"]
data_analisis["precio_usd"] = data_analisis["dolares"]

## solo registros con precios
data_analisis["sin_precio"] = (data_analisis["precio_pen"].isna() & data_analisis["precio_usd"].isna()).astype(int)
data_analisis = data_analisis.query("sin_precio == 0").copy()

# AREA robusta
tmp = data_analisis["area"].astype(str).str.replace(r"\s+", " ", regex=True).str.strip()
mm = tmp.str.split(" a ", n=1, expand=True)
data_analisis["area_min"] = pd.to_numeric(mm[0].str.replace(",", "."), errors="coerce")
data_analisis["area_max"] = pd.to_numeric(mm[1].str.replace(",", "."), errors="coerce")
data_analisis["area_promedio"] = data_analisis[["area_min","area_max"]].mean(axis=1)

# DORMITORIO robusto
tmpd = data_analisis["dormitorio"].astype(str).str.replace(r"\s+", " ", regex=True).str.strip()
mmd = tmpd.str.split(" a ", n=1, expand=True)
data_analisis["domitorio_min"] = pd.to_numeric(mmd[0], errors="coerce")
data_analisis["domitorio_max"] = pd.to_numeric(mmd[1], errors="coerce")

# Precio por m2 (división segura)
den = data_analisis["area_promedio"].replace(0, np.nan)
data_analisis["precio_m2_pen"] = (data_analisis["precio_pen"] / den).round(2)
data_analisis["precio_m2_usd"] = (data_analisis["precio_usd"] / den).round(2)

# Flags
data_analisis["tiene_mantenimiento"] = data_analisis["mantenimiento"].notna().astype(int)
data_analisis["tiene_estacionamientos"] = data_analisis["estacionamientos"].notna().astype(int)


cols_final = [
    'fuente','inmueble','operacion','distrito', 'distrito_2', 'distrito_oficial', 'zona','direccion',
    'precio','soles','dolares','precio_pen','precio_usd','variacion',
    'mantenimiento','tiene_mantenimiento','caracteristica',
    'area','area_min','area_max','area_promedio','precio_m2_pen','precio_m2_usd',
    'dormitorio','domitorio_min','domitorio_max','baños','estacionamientos','tiene_estacionamientos',
    'detalle','enlace','fecha','file_origin'
]
data_analisis = data_analisis[cols_final].copy()

print("\nData Final creada satisfactoriamente!")

# Export
out_path = DATA_OUT / "data_dondevivir_analisis.csv"
data_analisis.to_csv(out_path, sep="|", index=False)
print("\nData Final creada satisfactoriamente ->", out_path)