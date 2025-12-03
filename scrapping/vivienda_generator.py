# vivienda_generator.py (reemplazar la función generar_paginas existente)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import datetime as dt
import time

def generar_paginas():
    # ---------- INPUTS ----------
    print("\nSeleccione las opciones para la extracción de datos de Vivienda:\n")

    # Preguntar portal
    while True:
        portal_numero = input("Seleccione portal (1=A Donde Vivir, 2=Urbania): ")
        if portal_numero == "1":
            portal = "adondevivir"
            print("Se usará datos de A Donde Vivir")
            break
        elif portal_numero == "2":
            portal = "urbania"
            print("Se usará datos de Urbania")
            break
        else:
            print("✖ Opción no válida. Intente nuevamente.")

    # Operación
    while True:
        operacion_num = input("Seleccione operación (1=Venta, 2=Alquiler): ")
        if operacion_num == "1":
            operacion = "venta"
            print("Se consultará propiedades en Venta")
            break
        elif operacion_num == "2":
            operacion = "alquiler"
            print("Se consultará propiedades en Alquiler")
            break
        else:
            print("✖ Opción no válida. Intente nuevamente.")

    # Inmueble
    while True:
        inmueble_num = input("Seleccione el tipo de inmueble (1=Departamento, 2=Casa, 3=Terrenos, 4=Local Comercial): ")
        if inmueble_num == "1":
            inmueble = "departamentos"
            print("Se consultará Departamentos")
            break
        elif inmueble_num == "2":
            inmueble = "casas"
            print("Se consultará Casas")
            break
        elif inmueble_num == "3":
            inmueble = "terrenos"
            print("Se consultará Terrenos")
            break
        elif inmueble_num == "4":
            inmueble = "locales-comerciales"
            print("Se consultará Locales Comerciales")
            break
        else:
            print("✖ Opción no válida. Intente nuevamente.")

    # Zona
    while True:
        lima_num = input("Seleccione Zona Lima (1 = Top, 2 = Moderna, 3 = Centro, 4 = Este, 5 = Norte, 6 = Sur):  ")
        if lima_num == "1":
            zona = "Lima Top"; break
        elif lima_num == "2":
            zona = "Lima Moderna"; break
        elif lima_num == "3":
            zona = "Lima Centro"; break
        elif lima_num == "4":
            zona = "Lima Este"; break
        elif lima_num == "5":
            zona = "Lima Norte"; break
        elif lima_num == "6":
            zona = "Lima Sur"; break
        else:
            print("✖ Opción no válida. Intente nuevamente.")        

    hoy = dt.date.today()

    # ---------- ZONAS (tu diccionario) ----------
    zonas_lima = {
        'Lima Top': ['Miraflores', 'San Isidro', 'La Molina', 'Santiago de Surco', 'San Borja', 'Barranco'],
        'Lima Moderna': ['Jesus Maria', 'Lince', 'Magdalena', 'San Miguel', 'Pueblo Libre', 'Surquillo'],
        'Lima Centro': ['Lima Cercado', 'Brena', 'La Victoria', 'Rimac', 'San Luis'],
        'Lima Este': ['Ate Vitarte', 'Cieneguilla', 'Chaclacayo', 'Chosica Lurigancho', 'Santa Anita', 'El Agustino', 'San Juan de Lurigancho'],
        'Lima Norte': ['Carabayllo', 'Comas', 'Independencia', 'Los Olivos', 'Puente Piedra', 'San Martin de Porres', 'Ancon', 'Santa Rosa'],
        'Lima Sur': ['Chorrillos', 'Lurin', 'Pachacamac', 'San Juan de Miraflores', 'Villa El Salvador', 'Villa Maria del Triunfo', 'Pucusana', 'Punta Hermosa', 'Punta Negra', 'San Bartolo', 'Santa Maria del Mar']
    }

    def distrito_procesado(distrito):
        return distrito.lower().replace(" ", "-")

    # ---------- CREAR web_distrito ----------
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

    # ---------- OJO: crear UN SOLO driver y reutilizarlo para los conteos ----------
    num_dep = []


    for web in web_distrito:
        enlace = web["web"]
        distrito = web["distrito"]
        inmueble_local = web["inmueble"]
        portal_local = web["portal"]
        zona_local = web["zona"]
        
        # configurar driver una vez
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("user-agent=Mozilla/5.0")

        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

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

    # ---------- Generación de paginas (como antes) ----------
    num = sum(i["numero_inmuebles"] for i in num_dep)
    print(f"\nTotal de {inmueble} en {operacion} en {zona} son: {num}")

    paginas = []
    
    for num_dep_i in num_dep:
        distrito = num_dep_i["distrito"]
        num_inmueble_i = num_dep_i["numero_inmuebles"]
        portal_local = num_dep_i["portal"]
        operacion_local = num_dep_i["operacion"]
        inmueble_local = num_dep_i["inmueble"]
        zona_local = num_dep_i["zona"]

        # asumiendo 30 inmuebles por página
        numero_pagina = (num_inmueble_i + 30) // 30

        if portal_local == "adondevivir":
            for pagina in range(1, numero_pagina + 1):
                web = f"https://www.adondevivir.com/{inmueble_local}-en-{operacion_local}-en-{distrito_procesado(distrito)}-pagina-{pagina}.html"
                paginas.append({
                    "distrito": distrito,
                    "zona": zona_local,
                    "web": web,
                    "portal": portal_local,
                    "operacion": operacion_local,
                    "inmueble": inmueble_local
                })
        else:
            for pagina in range(1, numero_pagina + 1):
                web = f"https://urbania.pe/buscar/{operacion_local}-de-{inmueble_local}-en-{distrito_procesado(distrito)}--lima--lima?page={pagina}"
                paginas.append({
                    "distrito": distrito,
                    "zona": zona_local,
                    "web": web,
                    "portal": portal_local,
                    "operacion": operacion_local,
                    "inmueble": inmueble_local
                })

    # devolver lo necesario para main_paralelo
    return paginas, num_dep, num, portal, operacion, inmueble, zona
