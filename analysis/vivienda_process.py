

## Vivienda Processamiento de datos - unión y limpieza
## =====================================================:

## Librerias
import pandas as pd
import numpy as np
import os
from pathlib import Path
import re, unicodedata
import warnings
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


## 1. Proceso de Limpieza de Datos. 

data_dup = raw_all["enlace"].duplicated(keep=False)
raw_all_nd = raw_all.drop_duplicates(subset = ["enlace"], keep="first")

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

raw_all_nd["distrito"] = s.replace(valores)   # crea la nueva columna

raw_all_nd["distrito_norm"] = raw_all_nd["distrito"].str.lower().str.strip()
raw_all_nd["direccion_norm"] = raw_all_nd["direccion"].str.lower().str.strip()

raw_all_nd["distrito_en_direccion"] = raw_all_nd.apply(
    lambda row: row["distrito_norm"] in row["direccion_norm"],
    axis=1
)

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

raw_all_nd2 = raw_all_nd[(raw_all_nd["distrito_candidato"].notnull()) & 
                        (raw_all_nd["distrito_candidato"] != "Ventanilla") 
                        ].copy() ## no van distritos de callao ni distritos candidatos qu eno pertenezcan a lima

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


### Asignacion de Zona

zonas_lima = {
        'Lima Top': ['Miraflores', 'San Isidro', 'La Molina', 'Santiago De Surco', 'San Borja', 'Barranco'],
        'Lima Moderna': ['Jesús María', 'Lince', 'Magdalena', 'San Miguel', 'Pueblo Libre', 'Surquillo'],
        'Lima Centro': ['Lima Cercado', 'Breña', 'La Victoria', 'Rimac', 'San Luis'],
        'Lima Este': ['Ate Vitarte', 'Cieneguilla', 'Chaclacayo', 'Chosica Lurigancho', 'Santa Anita', 'El Agustino', 'San Juan De Lurigancho'],
        'Lima Norte': ['Carabayllo', 'Comas', 'Independencia', 'Los Olivos', 'Puente Piedra', 'San Martin De Porres', 'Ancón', 'Santa Rosa'],
        'Lima Sur': ['Chorrillos', 'Lurín', 'Pachacamac', 'San Juan De Miraflores', 'Villa El Salvador', 'Villa Maria Del Triunfo', 'Pucusana', 'Punta Hermosa', 'Punta Negra', 'San Bartolo', 'Santa Maria Del Mar']
    }

distrito_a_zona = {distrito: zona for zona, distritos_en_zona in zonas_lima.items() for distrito in distritos_en_zona}
data_analisis["zona"] = data_analisis["distrito_oficial"].map(distrito_a_zona).fillna('Otra Zona')

## Creacion de Variables Auxiliares 

# Normalizaciones básicas
data_analisis["fuente"] = data_analisis["fuente"].astype(str).str.strip().str.lower()
data_analisis["distrito"] = data_analisis["distrito_oficial"].astype(str).str.strip().str.title()
data_analisis["inmueble"] = data_analisis["inmueble"].astype(str).str.strip().str.lower()
data_analisis["operacion"] = data_analisis["operacion"].astype(str).str.strip().str.lower()
data_analisis["precio_pen"] = data_analisis["soles"]
data_analisis["precio_usd"] = np.where(data_analisis["dolares"].isnull(), round(data_analisis["precio_pen"]/3.40,0), data_analisis["dolares"])

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

# Flags
data_analisis["tiene_mantenimiento"] = data_analisis["mantenimiento"].notna().astype(int)
data_analisis["tiene_estacionamientos"] = data_analisis["estacionamientos"].notna().astype(int)
data_analisis["banios"] = data_analisis["caracteristica"].str.extract(r"(\d+)\s*bañ").astype("Int64")


### Análisis del Precio de Alquiler y Venta

#### Alquiler 

def detected_atipic_price_alquiler(distrito):
    
    data_distrito = data_analisis[(data_analisis["distrito"] == distrito) & 
                            (data_analisis["operacion"]== "alquiler")
                            ] 
    
    metrica = data_distrito["precio_pen"].median()
    q75 = data_distrito["precio_pen"].quantile(0.75)
    q25 = data_distrito["precio_pen"].quantile(0.25)
    iqr = q75 - q25
    umbral_superior = q75 + 1.5 * iqr
    umbral_inferior = q25 - 1.5 * iqr
    
    data_filtrada = data_distrito[(data_distrito["precio_pen"]<=umbral_inferior) | (data_distrito["precio_pen"]>=umbral_superior)].copy()
    
    data_filtrada["Atipico_Flag"] = np.where(data_filtrada["precio_pen"]<=umbral_inferior, "Precio Muy Bajo", "Precio Muy Alto").copy()
    
    # data_filtrada["Flag_Operacion"] = data_filtrada["detalle"].str.contains(r"\b(venta|vendo|se vende|en venta)\b", case = False, na=False).astype(int)
    
    data_filtrada["umbral_superior"] = umbral_superior
    data_filtrada["umbral_inferior"] = umbral_inferior
    data_filtrada["mediana"] = metrica
    
    condiciones = [
        (data_filtrada["zona"] == "Lima Top") &
        ((data_filtrada["precio_pen"] - data_filtrada["umbral_superior"]) < 20000),
    
        (data_filtrada["zona"].isin(["Lima Moderna", "Lima Centro"])) &
        ((data_filtrada["precio_pen"] - data_filtrada["umbral_superior"]) < 2000),
    
        (data_filtrada["zona"].isin(["Lima Este", "Lima Norte", "Lima Sur"])) &
        ((data_filtrada["precio_pen"] - data_filtrada["umbral_superior"]) < 1000),
    ]
    
    etiquetas = ["alquiler", "alquiler", "alquiler"]
    
    data_filtrada["casos"] = np.select(condiciones, etiquetas, default="quitar")
    
    return data_filtrada[["operacion", "precio_pen", "precio_usd", "mediana", "umbral_superior", "umbral_inferior", "Atipico_Flag", "casos", "direccion","detalle", "enlace"]]

distritos = data_analisis["distrito"].unique()

data_quitar = pd.DataFrame()
for distrito in distritos:
    
    datos_atipicos = detected_atipic_price_alquiler(distrito)
    datos_atipicos = datos_atipicos[datos_atipicos["casos"] == "quitar"].copy()
    # if not datos_atipicos.empty:
        # print(f"\nDistrito: {distrito} - Registros Atípicos: {len(datos_atipicos)}")
    data_quitar = pd.concat([data_quitar, datos_atipicos], ignore_index=True) 
    
    
data_analisis_temp = data_analisis.merge(
    data_quitar[["enlace", "casos"]],
    on = "enlace",
    how = "left"
    
)

data_analisis_limpia = data_analisis_temp[data_analisis_temp["casos"] != "quitar"]


#### Venta
data_analisis_venta = data_analisis_limpia[data_analisis_limpia["operacion"] == "venta"].copy()

def detected_atipic_price_venta(distrito):
    
    data_filtrada = data_analisis_venta[(data_analisis_venta["distrito"]==distrito) &
                                        (data_analisis_venta["operacion"]=="venta")].copy()
    
    condiciones = [
        data_filtrada["precio_pen"] - data_filtrada["precio_usd"]*4.8 > 100000,
        data_filtrada["precio_pen"] - data_filtrada["precio_usd"]*4.8 > 100000,
    ]
    
    etiquetas = ["precio_venta_mal", "precio_venta_bien"]
    
    data_filtrada["precio_venta"] = np.select(condiciones, etiquetas, "normal")
    p5 = data_filtrada["precio_usd"].quantile(0.005)
    
    data_filtrada["menores"] = np.where(data_filtrada["precio_usd"] < 10000, "quitar", "")
    
    return data_filtrada[["distrito", "precio", "precio_pen", "precio_usd", "precio_venta", "menores", "enlace"]]
    
    
data_quitar_venta = pd.DataFrame()
for distrito in distritos:
    
    datos_atipicos_venta = detected_atipic_price_venta(distrito)
    datos_atipicos = datos_atipicos_venta[datos_atipicos_venta["menores"] == "quitar"].copy()
    data_quitar_venta = pd.concat([data_quitar_venta, datos_atipicos], ignore_index=True) 
    
data_quitar_venta
    
data_analisis_temp2 = data_analisis_limpia.merge(
    data_quitar_venta[["enlace", "menores"]],
    on = "enlace",
    how = "left"

)

data_analisis_limpia2 = data_analisis_temp2[data_analisis_temp2["menores"] != "quitar"]


### Creacion de Variales Auxiliares

print("\nCreación de Variables Auxiliares")

data_analisis_limpia2['precio_pen'] = pd.to_numeric(data_analisis_limpia2['precio_pen'], errors='coerce')
data_analisis_limpia2['precio_usd'] = pd.to_numeric(data_analisis_limpia2['precio_usd'], errors='coerce')
data_analisis_limpia2['area'] = pd.to_numeric(data_analisis_limpia2['area'], errors='coerce')

# Bins y labels para precio de venta (Soles)
bins_alquiler = [-1, 1500, 2500, 3500, 4500, float('inf')]
labels_alquiler = ["Hasta S/1.5k", "De S/1.5k a S/2.5k", "De S/2.5 a S/3.5k", "De S/3.5k a S/4.5k", "De S/4.5k a más"]
data_analisis_limpia2['precio_alquiler_agp'] = pd.cut(data_analisis_limpia2[data_analisis_limpia2["operacion"]=="alquiler"]["precio_pen"], bins=bins_alquiler, labels=labels_alquiler, right=False)

# Bins y labels para precio de venta (Dólares)
bins_venta = [-1, 50000, 100000, 200000, 500000, float('inf')]
labels_venta = ["Hasta $ 50k", "De $ 50k a $ 100k", "De $ 100k a $ 200k", "De $ 200k a $ 500k", "De $ 500k a más"]
data_analisis_limpia2['precio_venta_agp'] = pd.cut(data_analisis_limpia2[data_analisis_limpia2["operacion"]=="venta"]['precio_usd'], bins=bins_venta, labels=labels_venta, right=False)

# Bins y labels para área (m²)
bins_area = [-1, 50, 100, 200, 300, float('inf')]
labels_area = ["Hasta 50m2", "De 50m2 a 100m2", "De 100m2 a 200m2", "De 200m2 a 300m2", "De 300m2 a más"]
data_analisis_limpia2['area_agp'] = pd.cut(data_analisis_limpia2['area'], bins=bins_area, labels=labels_area, right=False)

## Estacionamiento
data_analisis_limpia2["estacionamiento_gp"] = data_analisis_limpia2["estacionamientos"].apply(lambda x: "Si" if x > 0 else "No")

data_analisis_limpia2["dormitorios"] = pd.cut(data_analisis_limpia2['domitorio_min'],
                                    bins=[1, 2, 3, 4, 5, float('inf')],
                                    labels=['1 Dormitorio', '2 Dormitorios', '3 Dormitorios', '4 Dormitorios', '5 o más Dormitorios'],
                                    right=False)

### Creación de Data Final 

cols_final = [
    'fuente','inmueble','operacion', 'distrito', 'zona','direccion',
    'precio','soles','dolares','precio_pen','precio_usd','variacion',
    'mantenimiento','tiene_mantenimiento','caracteristica',
    'area','area_min','area_max','area_promedio', 'area_agp', 'precio_m2_pen', 'precio_venta_agp', 'precio_alquiler_agp',
    'dormitorio','domitorio_min','domitorio_max','banios', 'estacionamientos','tiene_estacionamientos', 'estacionamiento_gp',
    'detalle','enlace','fecha'
]

data_analisis_final = data_analisis_limpia2[cols_final].copy()

print("\nData Final creada satisfactoriamente!")

# Export
out_path = DATA_OUT / "data_dondevivir_analisis.csv"
data_analisis_final.to_csv(out_path, sep="|", index=False)
print("\nData Final creada satisfactoriamente ->", out_path)