# Análisis del mercado de Alquiler y Venta en Lima Metropolitana
Proyecto de **análisis inmobiliario end-to-end** que estudia los precios de **alquiler y venta de inmuebles en Lima Metropolitana**, combinando **web scraping, limpieza de datos, análisis exploratorio, modelado y visualización interactiva**.

El objetivo es proporcionar una herramienta útil para potenciales compradores e inquilinos, ayudándoles a tomar decisiones informadas basadas en datos reales del mercado.

Proyecto profesional de scraping, análisis y visualización de los diferentes tipos de inmuebles disponibles en Lima usando:
- **Python**
- **Selenium** (Web Scraping)
- **Pandas / NumPy** (Limpieza y análisis de datos)
- **Streamlit** (Dashboard interactivo)
- **Plotly / Matplotlib** (Visualización)


## Características principales
- Scraping automatizado de los portales **Urbania** y **Adondevivir**
- Filtros dinámicos por:
  - Tipo de operación (alquiler / venta)
  - Precio
  - Área
  - Distrito
  - Características del inmueble
- Mapa interactivo con ubicaciones geográficas reales
- Análisis comparativo por zonas y distritos
- **Modelo ML** para estimar el precio de mercado de un departamento
- Dashboard rápido, intuitivo y orientado a análisis


## 🗺️ Demo del Dashboard

👉 **Aplicación en producción:**  
https://vivienda.streamlit.app/



![Análisis Descriptivo](dashboard/vivienda1.gif)

![Alquiler - Venta](dashboard/vivienda2.gif)



git clone https://github.com/tu_usuario/Analisis_Vivienda.git
cd Analisis_Vivienda
pip install -r requirements.txt
streamlit run app.py






