
## Proyecto A donde Vivir

## Librerias
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from tqdm import tqdm
import datetime as dt
import json

## Inputs
print("\nSeleccione las opciones para la extracción de datos de Vivienda:\n")

portales = ["adondevivir", "urbania"]

zonas = [
    # "Lima Top",
    "Lima Moderna",
    # "Lima Centro",
    # "Lima Este",
    # "Lima Norte",
    # "Lima Sur"
]

config_operacion = {
    "alquiler": ["departamentos"],
    "venta": ["departamentos", "casas"]
}


combinaciones = []

for portal in portales:
    for operacion, inmuebles in config_operacion.items():
        for inmueble in inmuebles:
            for zona in zonas:
                combinaciones.append({
                    "portal": portal,
                    "operacion": operacion,
                    "inmueble": inmueble,
                    "zona": zona
                })


def distrito_procesado(distrito):
    return distrito.lower().replace(" ", "-")


for cfg in combinaciones:

    portal = cfg["portal"]
    operacion = cfg["operacion"]
    inmueble = cfg["inmueble"]
    zona = cfg["zona"]

    hoy = dt.date.today()

    print("\n==========================================")
    print("Inicio de extracción")
    print(f"Portal: {portal}")
    print(f"Operación: {operacion}")
    print(f"Inmueble: {inmueble}")
    print(f"Zona: {zona}")
    print(f"Fecha: {hoy}")
    print("==========================================\n")

    # 👉 A PARTIR DE AQUÍ
    # reutilizas EXACTAMENTE tu código actual:
    # - zonas_lima
    # - web_distrito
    # - conteo
    # - paginado
    # - scraping
    # - guardado
    
    ### Distritos de Lima
    zonas_lima = {
        'Lima Top': ['Miraflores', 'San Isidro', 'La Molina', 'Santiago de Surco', 'San Borja', 'Barranco'],
        'Lima Moderna': ['Jesus Maria', 'Lince', 'Magdalena', 'San Miguel', 'Pueblo Libre', 'Surquillo'],
        'Lima Centro': ['Lima Cercado', 'Brena', 'La Victoria', 'Rimac', 'San Luis'],
        'Lima Este': ['Ate Vitarte', 'Cieneguilla', 'Chaclacayo', 'Chosica Lurigancho', 'Santa Anita', 'El Agustino', 'San Juan de Lurigancho'],
        'Lima Norte': ['Carabayllo', 'Comas', 'Independencia', 'Los Olivos', 'Puente Piedra', 'San Martin de Porres', 'Ancon', 'Santa Rosa'],
        'Lima Sur': ['Chorrillos', 'Lurin', 'Pachacamac', 'San Juan de Miraflores', 'Villa El Salvador', 'Villa Maria del Triunfo', 'Pucusana', 'Punta Hermosa', 'Punta Negra', 'San Bartolo', 'Santa Maria del Mar']
    }
    



    ## Creacion de Enlaces       
    web_distrito = []

    if portal == "adondevivir":

        for distrito in zonas_lima[zona]:
            web = f"https://www.adondevivir.com/{inmueble}-en-{operacion}-en-{distrito_procesado(distrito)}.html"
            web_distrito.append({
                "distrito": distrito,
                "web": web,
                "portal": portal,
                "operacion": operacion,
                "inmueble": inmueble,
                "zona": zona
            })

    else:

        for distrito in zonas_lima[zona]:
            web = f"https://urbania.pe/buscar/{operacion}-de-{inmueble}-en-{distrito_procesado(distrito)}--lima--lima"
            web_distrito.append({
                "distrito": distrito,
                "web": web,
                "portal": portal,
                "operacion": operacion,
                "inmueble": inmueble,
                "zona": zona
            })



    num_dep = []
    for web in web_distrito:

        enlace = web["web"]
        distrito = web["distrito"]
        inmueble = web["inmueble"]
        portal = web["portal"]
        zona = web["zona"]

        options = webdriver.ChromeOptions()
        options.add_argument("--headless")   # modo oculto
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options = options)
        driver.minimize_window()
        driver.get(enlace)

        elementos = driver.find_elements(By.CSS_SELECTOR, "h1.postingsTitle-module__title")

        if elementos:  # si encontró al menos uno
            texto = elementos[0].text  # Tomamos el primero
            total_inmuebles = int(''.join(filter(str.isdigit, texto)))
            # print(f"Total {inmueble} en {distrito}: {total_inmuebles}")
        else:
            total_inmuebles = 0 
            # print(f"Total {inmueble} en {distrito}: {total_inmuebles}")

        tqdm.write(f"Total {inmueble} en {distrito}: {total_inmuebles}")

        num_dep.append({
                "zona": zona,
                "distrito": distrito,
                "numero_inmuebles": total_inmuebles,
                "inmueble": inmueble,
                "operacion" : operacion,
                "portal" : portal
                })

        driver.quit()

    ##  Total de Departamentos
    num = sum(i["numero_inmuebles"] for i in num_dep)

    print(f"\nTotal de {inmueble} en {operacion} en {zona} son: {num}")

    ################################

    ## Creacion de Enlaces

    paginas = []
    for num_dep_i in num_dep:

        distrito = num_dep_i["distrito"]
        num_inmueble_i = num_dep_i["numero_inmuebles"]
        portal = num_dep_i["portal"]
        operacion = num_dep_i["operacion"]
        inmueble = num_dep_i["inmueble"]
        zona = num_dep_i["zona"]

        ## asumiendo que son 30 departamentos por pagina. 
        numero_pagina = (num_inmueble_i + 30 - 1) // 30


        if portal == "adondevivir":
            for pagina in range(1, numero_pagina+1):
                web = f"https://www.adondevivir.com/{inmueble}-en-{operacion}-en-{distrito_procesado(distrito)}-pagina-{pagina}.html" ## a donde vivir. 
                paginas.append({
                "distrito": distrito, 
                "zona": zona,
                "web": web,
                "portal": portal,
                "operacion":operacion, 
                "inmueble": inmueble
                })

        else:
            for pagina in range(1, numero_pagina+1):
                web = f"https://urbania.pe/buscar/{operacion}-de-{inmueble}-en-{distrito_procesado(distrito)}--lima--lima?page={pagina}"
                paginas.append({
                "distrito": distrito, 
                "zona": zona,
                "web": web,
                "portal": portal,
                "operacion":operacion, 
                "inmueble": inmueble
                })


    ##########################

    print("\nExtaccion De Datos - En Proceso...\n")

    data_final = []

    for pagina in tqdm(paginas, desc="Procesando Distritos", unit="distrito"):

        portal = pagina["portal"]
        operacion = pagina["operacion"]
        inmueble = pagina["inmueble"]
        distrito = pagina["distrito"]
        zona = pagina["zona"]

        options = webdriver.ChromeOptions()
        options.add_argument("--headless")   # modo oculto
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

        driver.get(pagina["web"])

        ## Capturando Informacion
        anuncios = driver.find_elements(By.CLASS_NAME, "postingsList-module__postings-container")

        data_vivienda = []

        for anuncio in anuncios:
            ## Identificacion de precio:
            precio = anuncio.find_elements(By.CLASS_NAME, "postingPrices-module__price-container")
            precio_ = []
            for p in precio:
                precio_.append(p.text)

            precio_f_ = []
            for p in precio_:
                monto = p.replace(",", "").strip()  # elimina comas y espacios
                partes = monto.split('·')  # divide soles y dólares
                partes_limpias = []
                for parte in partes:
                    subpartes = parte.strip().split('\n')  # divide por salto de línea
                    for sub in subpartes:
                        sub = sub.strip()
                        if sub:  # evitar vacíos
                            partes_limpias.append(sub)
                precio_f_.append(partes_limpias)

            soles = []
            dolares = []
            variacion = []

            for precios in precio_f_:  # precios = ['S/ 2200', 'USD 620', 'S/ 100 Mantenimiento']
                s = d = v = None
                for p in precios:
                    if p.startswith('S/'):
                        if "Mantenimiento" not in p:
                            s = p.replace('S/', '').strip()
                    elif p.startswith('USD'):
                        d = p.replace('USD', '').strip()
                    elif "%" in p:
                        v = p.strip()
                soles.append(s)
                dolares.append(d)
                variacion.append(v)

            ## Mantenimiento 
            mantenimiento = anuncio.find_elements(By.CLASS_NAME, "postingPrices-module__expenses-property-listing")    
            mantenimiento_ = []
            for m in mantenimiento:
                mantenimiento_i = m.text
                mantenimiento_f = mantenimiento_i.replace("S/", "").replace("Mantenimiento", "").strip()
                mantenimiento_.append(mantenimiento_f)

            ## Caracteristica
            caracteristicas = anuncio.find_elements(By.CLASS_NAME, "postingMainFeatures-module__posting-main-features-block")
            caracteristicas_ = []
            for c in caracteristicas:
                caracteristicas_.append(c.text)

            area_ = []
            dorm_ = []
            banio_ = []
            est_ = []
            for c in caracteristicas_:
                carac = c.split("\n")
                area = dorm = banio = est = None
                for c_i in carac:
                    if "m² tot." in c_i:
                        area = c_i.replace('m² tot.', '').strip()
                    elif "dorm." in c_i:
                        dorm = c_i.replace('dorm.', '').strip()
                    elif "baños" in c_i:
                        banio = c_i.replace('baños', '').strip()
                    elif "estac." in c_i:
                        est = c_i.replace('estac.', '').strip()

                area_.append(area)
                dorm_.append(dorm)
                banio_.append(banio)
                est_.append(est)

            ## Detalle
            detalle = anuncio.find_elements(By.CLASS_NAME, "postingCard-module__posting-description")
            detalle_ = []
            for d in detalle:
                # print(d.text)
                detalle_.append(d.text)    

            ## Direccion
            direccion = anuncio.find_elements(By.CLASS_NAME, "postingLocations-module__location-block")
            direccion_ = []
            for d in direccion:
                direccion_.append(d.text)

            ## Link del anuncio
            descripcion = anuncio.find_elements(By.CLASS_NAME, "postingCard-module__posting-description")
            enlace_ = []
            for descripcion_i in descripcion:
                enlace = descripcion_i.find_element(By.TAG_NAME, "a").get_attribute("href")
                enlace_.append(enlace)

            data_vivienda_sub = []   
            for precio_i, soles_i, dolares_i, variacion_i, mantenimiento_i, direccion_i, caracteristica_i, area_i, dorm_i, banio_i, est_i, enlace_i, detalle_i in zip(precio_, soles, dolares, variacion, mantenimiento_, direccion_, caracteristicas_, area_, dorm_, banio_, est_, enlace_, detalle_):
                data_vivienda_sub.append({
                    "fuente": portal,
                    "inmueble": inmueble, 
                    "operacion": operacion, 
                    "zona": zona,
                    "distrito": distrito,
                    "direccion": direccion_i,
                    "precio": precio_i,
                    "soles": soles_i,
                    "dolares": dolares_i,
                    "variacion": variacion_i,
                    "mantenimiento": mantenimiento_i,
                    "caracteristica": caracteristica_i,
                    "area": area_i,
                    "dormitorio": dorm_i,
                    "baños": banio_i,
                    "estacionamientos": est_i,
                    "detalle": detalle_i,
                    "enlace": enlace_i,
                    "fecha": hoy 
                })

            data_vivienda.extend(data_vivienda_sub)

            driver.quit() 

        data_final.extend(data_vivienda)

    print("\nValidacion de Datos Descargados:\n")
    num = sum(i["numero_inmuebles"] for i in num_dep)
    print(f"Total de {inmueble} en {operacion} esperado: {num}")
    print(f"Total de {inmueble} en {operacion} decargado: {len(data_final)}")
    print(f"Porcentaje decargado: {round(len(data_final)/num*100, 2)} %")
    
    ## Guardando Data Final
    print("\nGuardando Data Final...\n")
    
    carpeta = rf"C:\Users\PC\Desktop\Proyectos\Proyectos_Py\1.Analisis Vivienda\Analisis_Vivienda\data\raw"
    ruta_csv = rf"{carpeta}\data_{operacion}_{inmueble}_{portal}_{zona}.csv"
    ruta_json = rf"{carpeta}\data_{operacion}_{inmueble}_{portal}_{zona}.json"
    
    with open(ruta_json, "w", encoding="utf-8") as f:
        json.dump(data_final, f, indent=4, ensure_ascii=False, default=str)
        
    data_final_df = pd.DataFrame(data_final)
    data_final_df.to_csv(ruta_csv, sep = "|",index=False)


    # portal = cfg["portal"]
    # operacion = cfg["operacion"]
    # inmueble = cfg["inmueble"]
    # zona = cfg["zona"]