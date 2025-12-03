from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from tqdm import tqdm
import datetime as dt
import time

import os
print(f"🔵 Worker iniciado → PID {os.getpid()}")



def iniciar_driver():
    """Configura y devuelve un WebDriver para este proceso."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("user-agent=Mozilla/5.0")

    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=options
    )
    return driver



def scrape_lote(paginas_lote):
    """
    Procesa un lote de páginas y devuelve la data completa de ese lote.
    Cada proceso ejecutará esta función en paralelo.
    """
    data_lote = []
    hoy = dt.date.today()

    driver = iniciar_driver()

    # tqdm solo para ver progreso en cada proceso
    for pagina in tqdm(paginas_lote, desc="Scraper Worker", unit="pag"):

        driver.get(pagina["web"])
        time.sleep(1.5)

        # AQUI VAS A PEGAR TU LOGICA DE SCRAPING
        # --------------------------------------------------
        anuncios = driver.find_elements(By.CLASS_NAME, "postingsList-module__postings-container")

        for anuncio in anuncios:

            # ******** EXTRACCIÓN DE PRECIO ********
            precios = anuncio.find_elements(By.CLASS_NAME, "postingPrices-module__price-container")
            precios_txt = [p.text for p in precios]

            # Limpieza igual a tu script original
            soles = dolares = variacion = None
            for ptxt in precios_txt:
                if ptxt.startswith("S/"):
                    soles = ptxt.replace("S/", "").strip()
                elif ptxt.startswith("USD"):
                    dolares = ptxt.replace("USD", "").strip()
                elif "%" in ptxt:
                    variacion = ptxt

            # ******** MANTENIMIENTO ********
            try:
                mantenimiento = anuncio.find_element(
                    By.CLASS_NAME,
                    "postingPrices-module__expenses-property-listing"
                ).text.replace("S/", "").replace("Mantenimiento", "").strip()
            except:
                mantenimiento = None

            # ******** CARACTERISTICAS ********
            try:
                caracteristicas = anuncio.find_element(
                    By.CLASS_NAME,
                    "postingMainFeatures-module__posting-main-features-block"
                ).text.split("\n")
            except:
                caracteristicas = []

            area = dorm = banios = estac = None
            for c in caracteristicas:
                if "m² tot." in c:
                    area = c.replace("m² tot.", "").strip()
                elif "dorm." in c:
                    dorm = c.replace("dorm.", "").strip()
                elif "baños" in c:
                    banios = c.replace("baños", "").strip()
                elif "estac." in c:
                    estac = c.replace("estac.", "").strip()

            # ******** DESCRIPCION ********
            try:
                detalle = anuncio.find_element(
                    By.CLASS_NAME,
                    "postingCard-module__posting-description"
                ).text
            except:
                detalle = None

            # ******** DIRECCIÓN ********
            try:
                direccion = anuncio.find_element(
                    By.CLASS_NAME,
                    "postingLocations-module__location-block"
                ).text
            except:
                direccion = None

            # ******** ENLACE ********
            try:
                enlace = anuncio.find_element(
                    By.TAG_NAME, "a"
                ).get_attribute("href")
            except:
                enlace = None

            # Agregar registro
            data_lote.append({
                "fuente": pagina["portal"],
                "inmueble": pagina["inmueble"],
                "operacion": pagina["operacion"],
                "zona": pagina["zona"],
                "distrito": pagina["distrito"],
                "direccion": direccion,
                "soles": soles,
                "dolares": dolares,
                "variacion": variacion,
                "mantenimiento": mantenimiento,
                "area": area,
                "dormitorio": dorm,
                "baños": banios,
                "estacionamientos": estac,
                "detalle": detalle,
                "enlace": enlace,
                "fecha": hoy,
            })

    driver.quit()
    return data_lote
