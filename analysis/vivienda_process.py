

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

canon = {
    # canónico : [alias que podrían aparecer en la dirección]
    "Ate Vitarte": ["ate vitarte", "ate"],
    "Breña": ["breña", "brena"],
    "Carabayllo": ["carabayllo"],
    "Chaclacayo": ["chaclacayo"],
    "El Agustino": ["el agustino", "agustino"],
    "Independencia": ["independencia"],
    "Jesús María": ["jesus maria", "jesús maria", "jesus maría"], ## Jesús María
    "Chosica Lurigancho": [ "chosica"],
    "Lurín": ["lurin", "lurín"],
    "Pachacamac": ["pachacamac", "pachacámac"],
    "Pucusana": ["pucusana"],
    "Puente Piedra": ["puente piedra"],
    "Punta Negra": ["punta negra"],
    "Rimac": ["rimac", "rímac"],
    "San Juan de Miraflores": ["san juan de miraflores", "sjm"],
    "San Luis": ["san luis"],
    "San Martin de Porres": ["san martin de porres", "san martín de porres", "smp"],
    "Villa Maria del Triunfo": ["villa maria del triunfo", "villa maría del triunfo", "vmt"],
    "Ancón": ["ancon", "ancón"],
    "Lince": ["lince"],
    "Santa Rosa": ["santa rosa"],
    "Barranco": ["barranco"],
    "Magdalena": ["magdalena del mar", "magdalena"],
    "Punta Hermosa": ["punta hermosa"],
    "Santiago de Surco": ["santiago de surco", "surco"],
    "San Juan de Lurigancho": ["san juan de lurigancho"],
    "Lima Cercado" : ["cercado", "cercado de lima", "lima cercado"],
    "Los Olivos" : ["los olivos"],
    "Comas" : ["comas"],
    "San Bartolo" : ["san bartolo"], 
    'Villa El Salvador' : ["villa el salvador"],
    "Santa Maria del Mar": ["santa maria del mar"],
    "San Isidro" : ["san isidro"],
    "La Molina" : ["la molina"],
    "Chorrillos" : ["chorrillos"],
    "San Borja" : ["san borja"],
    "Miraflores" : ["miraflores"],
    "Surquillo" : ["surquillo"],
    "Cieneguilla" : ["cieneguilla"],
    "Ventanilla" : ["ventanilla"],
    "La Victoria" : ["la victoria"],
    'Pueblo Libre' : ["pueblo libre"], 
    'San Miguel' : ["san miguel"], 
    'Santa Anita' : ["santa anita"], 
    'Ventanilla' : ["ventanilla"], 
}

def strip_accents(s):
    if not isinstance(s, str):
        return s
    return ''.join(ch for ch in unicodedata.normalize("NFD", s) if unicodedata.category(ch) != "Mn")

raw_all_nd["dir_norm"]  = raw_all_nd["direccion"].astype(str).str.lower().str.replace(r"\s+", " ", regex=True).map(strip_accents)
raw_all_nd["dist_norm"] = raw_all_nd["distrito"].astype(str).str.lower().str.replace(r"\s+", " ", regex=True).map(strip_accents)

# precompila patrones regex alias
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

raw_all_nd["dist_candidates"] = raw_all_nd["dir_norm"].map(candidates_from_address)
raw_all_nd["distrito_candidato"] = raw_all_nd["dist_candidates"].str.get(0) 


raw_all_nd2 = raw_all_nd[(raw_all_nd["distrito_candidato"].notnull()) & (raw_all_nd["distrito_candidato"] != "Ventanilla") ].copy()

cols_obj =['fuente', 'inmueble', 'operacion', 'distrito_candidato' , 'zona', 'direccion', 'precio',
            'soles', 'dolares', 'variacion', 'mantenimiento', 'caracteristica',
            'area', 'dormitorio', 'baños', 'estacionamientos', 'detalle', 'enlace',
            'fecha', 'file_origin']

data_vivienda = raw_all_nd2[cols_obj].copy()

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


data_vivienda["distrito_oficial"] = data_vivienda["distrito_candidato"] ## .apply(normalizar)


print("\nCreacion de variables!")

cols_analisis = ['fuente','inmueble','operacion',
                'distrito_oficial', 'zona',
                'direccion','precio',
                'soles','dolares','variacion','mantenimiento','caracteristica',
                'area','dormitorio','baños','estacionamientos','detalle','enlace',
                'fecha','file_origin']
data_analisis = data_vivienda[cols_analisis].copy()

# Normalizaciones básicas
data_analisis["fuente"] = data_analisis["fuente"].astype(str).str.strip().str.lower()
data_analisis["distrito"] = data_analisis["distrito_oficial"].astype(str).str.strip().str.title()
data_analisis["inmueble"] = data_analisis["inmueble"].astype(str).str.strip().str.lower()
data_analisis["operacion"] = data_analisis["operacion"].astype(str).str.strip().str.lower()
data_analisis["precio_pen"] = data_analisis["soles"]
data_analisis["precio_usd"] = data_analisis["dolares"]

# solo registros con precios
data_analisis["sin_precio"] = (data_analisis["precio_pen"].isna() & data_analisis["precio_usd"].isna()).astype(int)
data_analisis = data_analisis.query("sin_precio == 0").copy()

# area
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

# Flags
data_analisis["tiene_mantenimiento"] = data_analisis["mantenimiento"].notna().astype(int)
data_analisis["tiene_estacionamientos"] = data_analisis["estacionamientos"].notna().astype(int)
data_analisis["banios"] = data_analisis["caracteristica"].str.extract(r"(\d+)\s*bañ").astype("Int64")

data_analisis['distrito_categoria'] = data_analisis['zona'].astype('category')

# Se crean columnas categóricas para los rangos de precio y área, que se usarán en los filtros de las pestañas.
data_analisis['precio_pen'] = pd.to_numeric(data_analisis['precio_pen'], errors='coerce')
data_analisis['precio_usd'] = pd.to_numeric(data_analisis['precio_usd'], errors='coerce')
data_analisis['area'] = pd.to_numeric(data_analisis['area'], errors='coerce')

# Bins y labels para precio de venta (Soles)
bins_alquiler = [-1, 1500, 2500, 3500, 4500, float('inf')]
labels_alquiler = ["Hasta S/1.5k", "De S/1.5k a S/2.5k", "De S/2.5 a S/3.5k", "De S/3.5k a S/4.5k", "De S/4.5k a más"]
data_analisis['precio_alquiler_agp'] = pd.cut(data_analisis[data_analisis["operacion"]=="alquiler"]["precio_pen"], bins=bins_alquiler, labels=labels_alquiler, right=False)

# Bins y labels para precio de venta (Dólares)
bins_venta = [-1, 50000, 100000, 200000, 500000, float('inf')]
labels_venta = ["Hasta $ 50k", "De $ 50k a $ 100k", "De $ 100k a $ 200k", "De $ 200k a $ 500k", "De $ 500k a más"]
data_analisis['precio_venta_agp'] = pd.cut(data_analisis[data_analisis["operacion"]=="venta"]['precio_usd'], bins=bins_venta, labels=labels_venta, right=False)

# Bins y labels para área (m²)
bins_area = [-1, 50, 100, 200, 300, float('inf')]
labels_area = ["Hasta 50m2", "De 50m2 a 100m2", "De 100m2 a 200m2", "De 200m2 a 300m2", "De 300m2 a más"]
data_analisis['area_agp'] = pd.cut(data_analisis['area'], bins=bins_area, labels=labels_area, right=False)

## Estacionamiento
data_analisis["estacionamiento_gp"] = data_analisis["estacionamientos"].apply(lambda x: "Si" if x > 0 else "No")

# Orden final
cols_final = [
    'fuente','inmueble','operacion', 'distrito', 'zona','direccion',
    'precio','soles','dolares','precio_pen','precio_usd','variacion',
    'mantenimiento','tiene_mantenimiento','caracteristica',
    'area','area_min','area_max','area_promedio', 'area_agp', 'precio_m2_pen', 'precio_venta_agp', 'precio_alquiler_agp',
    'dormitorio','domitorio_min','domitorio_max','banios', 'estacionamientos','tiene_estacionamientos', 'estacionamiento_gp',
    'detalle','enlace','fecha'
]
data_analisis = data_analisis[cols_final].copy()

zonas_lima = {
        'Lima Top': ['Miraflores', 'San Isidro', 'La Molina', 'Santiago De Surco', 'San Borja', 'Barranco'],
        'Lima Moderna': ['Jesús María', 'Lince', 'Magdalena', 'San Miguel', 'Pueblo Libre', 'Surquillo'],
        'Lima Centro': ['Lima Cercado', 'Breña', 'La Victoria', 'Rimac', 'San Luis'],
        'Lima Este': ['Ate Vitarte', 'Cieneguilla', 'Chaclacayo', 'Chosica Lurigancho', 'Santa Anita', 'El Agustino', 'San Juan De Lurigancho'],
        'Lima Norte': ['Carabayllo', 'Comas', 'Independencia', 'Los Olivos', 'Puente Piedra', 'San Martin De Porres', 'Ancón', 'Santa Rosa'],
        'Lima Sur': ['Chorrillos', 'Lurín', 'Pachacamac', 'San Juan De Miraflores', 'Villa El Salvador', 'Villa Maria Del Triunfo', 'Pucusana', 'Punta Hermosa', 'Punta Negra', 'San Bartolo', 'Santa Maria Del Mar']
    }

distrito_a_zona = {distrito: zona for zona, distritos_en_zona in zonas_lima.items() for distrito in distritos_en_zona}

data_analisis["zona"] = data_analisis["distrito"].map(distrito_a_zona).fillna('Otra Zona')

data_analisis["dormitorios"] = pd.cut(data_analisis['domitorio_min'],
                                    bins=[1, 2, 3, 4, 5, float('inf')],
                                    labels=['1 Dormitorio', '2 Dormitorios', '3 Dormitorios', '4 Dormitorios', '5 o más Dormitorios'],
                                    right=False)


print("\nData Final creada satisfactoriamente!")

# Export
out_path = DATA_OUT / "data_dondevivir_analisis.csv"
data_analisis.to_csv(out_path, sep="|", index=False)
print("\nData Final creada satisfactoriamente ->", out_path)