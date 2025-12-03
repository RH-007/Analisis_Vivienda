# vivienda_generator.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

import datetime as dt
import time

def generar_paginas():
    print("\nSeleccione las opciones para la extracción de datos de Vivienda:\n")

    # ----------- INPUTS -----------
    while True:
        portal_numero = input("Seleccione portal (1=A Donde Vivir, 2=Urbania): ")
        if portal_numero == "1":
            portal = "adondevivir"
            break
        elif portal_numero == "2":
            portal = "urbania"
            break
        else:
            print("✖ Opción no válida.")

    while True:
        operacion_num = input("Seleccione operación (1=Venta, 2=Alquiler): ")
        if operacion_num == "1":
            operacion = "venta"
            break
        elif operacion_num == "2":
            operacion = "alquiler"
            break
        else:
            print("✖ Opción no válida.")

    while True:
        inmueble_num = input("Tipo de inmueble (1=Departamento, 2=Casa, 3=Terrenos, 4=Local Comercial): ")
        if inmueble_num == "1":
            inmueble = "departamentos"
            break
        elif inmueble_num == "2":
            inmueble = "casas"
            break
        elif inmueble_num == "3":
            inmueble = "terrenos"
            break
        elif inmueble_num == "4":
            inmueble = "locales-comerciales"
            break
        else:
            print("✖ Opción no válida.")

    while True:
        lima_num = input("Seleccione Zona (1 Top, 2 Moderna, 3 Centro, 4 Este, 5 Norte, 6 Sur): ")
        zonas_map = {
            "1": "Lima Top", "2": "Lima Moderna", "3": "Lima Centro",
            "4": "Lima Este", "5": "Lima Norte", "6": "Lima Sur"
        }
        if lima_num in zonas_map:
            zona = zonas_map[lima_num]
            break
        else:
            print("✖ Opción no válida.")

    hoy = dt.date.today()

    # ----------- ZONAS -----------
    zonas_lima = {
        'Lima Top': ['Miraflores', 'San Isidro', 'La Molina', 'Santiago de Surco', 'San Borja', 'Barranco'],
        'Lima Moderna': ['Jesus Maria', 'Lince', 'Magdalena', 'San Miguel', 'Pueblo Libre', 'Surquillo'],
        'Lima Centro': ['Lima Cercado', 'Brena', 'La Victoria', 'Rimac', 'San Luis'],
        'Lima Este': ['Ate Vitarte', 'Cieneguilla', 'Chaclacayo', 'Chosica Lurigancho', 'Santa Anita', 'El Agustino', 'San Juan de Lurigancho'],
        'Lima Norte': ['Carabayllo', 'Comas', 'Independencia', 'Los Olivos', 'Puente Piedra', 'San Martin de Porres', 'Ancon', 'Santa Rosa'],
        'Lima Sur': ['Chorrillos', 'Lurin', 'Pachacamac', 'San Juan de Miraflores', 'Villa El Salvador', 'Villa Maria del Triunfo', 'Pucusana', 'Punta Hermosa', 'Punta Negra', 'San Bartolo', 'Santa Maria del Mar']
    }

    # Función procesar distritos
    def distrito_slug(x):
        return x.lower().replace(" ", "-")

    # ----------- CREAR ENLACES DE DISTRITOS -----------
    web_distrito = []

    for distrito in zonas_lima[zona]:
        if portal == "adondevivir":
            web = f"https://www.adondevivir.com/{inmueble}-en-{operacion}-en-{distrito_slug(distrito)}.html"
        else:
            web = f"https://urbania.pe/buscar/{operacion}-de-{inmueble}-en-{distrito_slug(distrito)}--lima--lima"

        web_distrito.append({
            "distrito": distrito,
            "web": web,
            "portal": portal,
            "operacion": operacion,
            "inmueble": inmueble,
            "zona": zona
        })

    # ----------- SCRAPING LIGERO: UN SOLO DRIVER -----------
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0")

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    num_dep = []

    for web in web_distrito:
        enlace = web["web"]
        distrito = web["distrito"]
        inmueble_local = web["inmueble"]
        portal_local = web["portal"]
        zona_local = web["zona"]

        try:
            driver.get(enlace)
            time.sleep(1.2)  # pequeño wait para que cargue
            elementos = driver.find_elements(By.CSS_SELECTOR, "h1.postingsTitle-module__title")
            if elementos:
                texto = elementos[0].text
                total_inmuebles = int(''.join(filter(str.isdigit, texto))) if any(ch.isdigit() for ch in texto) else 0
            else:
                total_inmuebles = 0

        except Exception as e:
            # si falla, no crasheamos: ponemos 0 y seguimos
            print(f"Error contando inmuebles en {distrito}: {e}")
            total_inmuebles = 0

        # log simple (no tqdm)
        print(f"Total {inmueble_local} en {distrito}: {total_inmuebles}")

        num_dep.append({
            "zona": zona_local,
            "distrito": distrito,
            "numero_inmuebles": total_inmuebles,
            "inmueble": inmueble_local,
            "operacion": operacion,
            "portal": portal_local
        })

    # cerrar driver de conteo
    driver.quit()


    # ----------- GENERAR LISTA DE PÁGINAS -----------
    paginas = []

    for info in num_dep:
        total = info["numero_inmuebles"]
        max_pag = (total + 29) // 30

        for p in range(1, max_pag + 1):
            if portal == "adondevivir":
                url = f"https://www.adondevivir.com/{inmueble}-en-{operacion}-en-{distrito_slug(info['distrito'])}-pagina-{p}.html"
            else:
                url = f"https://urbania.pe/buscar/{operacion}-de-{inmueble}-en-{distrito_slug(info['distrito'])}--lima--lima?page={p}"

            paginas.append({
                "distrito": info["distrito"],
                "portal": portal,
                "operacion": operacion,
                "inmueble": inmueble,
                "zona": zona,
                "web": url
            })

    return paginas, num_dep, portal, operacion, inmueble, zona
