# scraper_worker.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

import datetime as dt
import time
import os
from tqdm import tqdm


def iniciar_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")

    return webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=options
    )


def scrape_lote(paginas_lote):
    print(f"🔵 Worker iniciado → PID {os.getpid()} | {len(paginas_lote)} páginas")

    data_lote = []
    hoy = dt.date.today()

    driver = iniciar_driver()

    for pagina in tqdm(paginas_lote, desc=f"Worker {os.getpid()}", unit="pag"):

        try:
            driver.get(pagina["web"])
            time.sleep(1.5)
        except:
            continue

        anuncios = driver.find_elements(By.CLASS_NAME, "postingCard-module__posting-description")

        for a in anuncios:
            try:
                enlace = a.find_element(By.TAG_NAME, "a").get_attribute("href")
            except:
                enlace = None

            data_lote.append({
                "fuente": pagina["portal"],
                "inmueble": pagina["inmueble"],
                "operacion": pagina["operacion"],
                "zona": pagina["zona"],
                "distrito": pagina["distrito"],
                "enlace": enlace,
                "fecha": hoy
            })

        driver.quit()
    return data_lote
