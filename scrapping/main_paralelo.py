from vivienda_generator import generar_paginas
from vivienda_worker import scrape_lote

import pandas as pd
import json
from multiprocessing import Pool, cpu_count
import math
import os

def dividir_lotes(paginas, n_lotes=3):
    """Divide la lista de páginas en n lotes equilibrados."""
    tamaño = math.ceil(len(paginas) / n_lotes)
    return [paginas[i:i + tamaño] for i in range(0, len(paginas), tamaño)]

def main():
    print("\nGenerando páginas desde vivienda_generador...\n")

    paginas, num_dep, portal, operacion, inmueble, zona = generar_paginas()

    print(f"Total de páginas generadas: {len(paginas)}")
    print(f"Portal: {portal}, Operación: {operacion}, Inmueble: {inmueble}, Zona: {zona}")
    print("\nIniciando scraping paralelo...\n")


    # ----------------------------------------------------
    # 1. DIVIDIR LOTES (3 procesos por defecto)
    # ----------------------------------------------------
    lotes = dividir_lotes(paginas, n_lotes=3)

    print(f"Total de lotes: {len(lotes)}")
    for i, lote in enumerate(lotes):
        print(f" - Lote {i+1}: {len(lote)} páginas")


    # ----------------------------------------------------
    # 2. EJECUTAR MULTIPROCESSING
    # ----------------------------------------------------
    with Pool(processes=3) as pool:
        resultados = pool.map(scrape_lote, lotes)


    # ----------------------------------------------------
    # 3. UNIR RESULTADOS
    # ----------------------------------------------------
    data_final = []
    for lote_data in resultados:
        data_final.extend(lote_data)

    print("\nScraping finalizado.")
    print(f"Registros descargados: {len(data_final)}")


    # ----------------------------------------------------
    # 4. GUARDAR DATA (CSV + JSON)
    # ----------------------------------------------------
    carpeta = rf"C:\Users\PC\Desktop\Proyectos\Proyectos_Py\1.Analisis Vivienda\Analisis_Vivienda\data\raw"
    ruta_csv = rf"{carpeta}\data_{operacion}_{inmueble}_{portal}_{zona}.csv"
    ruta_json = rf"{carpeta}\data_{operacion}_{inmueble}_{portal}_{zona}.json"

    df = pd.DataFrame(data_final)
    df.to_csv(ruta_csv, sep="|", index=False)

    with open(ruta_json, "w", encoding="utf-8") as f:
        json.dump(data_final, f, indent=4, ensure_ascii=False)

    print("\nArchivos guardados correctamente!!:")
    print(f" - CSV  → {ruta_csv}")
    print(f" - JSON → {ruta_json}")



if __name__ == "__main__":
    main()