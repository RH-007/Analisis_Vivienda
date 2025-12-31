
## Proyecto a Donde Vivir
## ==========================

## Liberias
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from urllib.parse import quote
import plotly.express as px


## Titulo

st.set_page_config(layout="wide")
st.title("Análisis del mercado de Alquiler y Venta en Lima")

"""
Bienvenido a la plataforma interactiva de análisis inmobiliario de Lima.  

Aquí podrás explorar **departamentos, casas y terrenos** en venta y alquiler, con datos reales y actualizados. 
Esta es una herramienta diseñada para ayudarte a entender **cómo se mueve el mercado inmobiliario en Lima**, detectar oportunidades y tomar mejores decisiones.  

Las principales fuentes fueron: 
- [Urbania](https://urbania.pe) y [Adondevivir](https://www.adondevivir.com)

La aplicación te permite:

- Visualizar la distribución de propiedades en los distintos distritos.  
- Comparar precios en **soles** (alquiler) y **dólares** (venta), con métricas como precio por m² y variación entre distritos (visualizaciones interactivas incluidas). 
- Filtrar fácilmente por área, dormitorios, baños, estacionamientos y mantenimiento si fuera el caso. 
- Acceder directamente al anuncio original de cada propiedad.  

"""

## ==================##
## Lecturas de data  ##
## ==================##

@st.cache_data # Decorador mágico de Streamlit
def load_data(path):
    """
    Carga los datos desde un archivo CSV.
    Gracias a @st.cache_data, esta función solo se ejecutará una vez
    y el resultado (el DataFrame) se guardará en memoria caché.
    Las siguientes veces que se necesiten los datos, se leerán directamente
    de la caché, haciendo la app mucho más rápida.
    """
    df = pd.read_csv(path, sep="|", encoding="utf-8")
    
    subset_cols = ['distrito', 'direccion']
    
    # Eliminamos los duplicados basándonos en las columnas clave.
    # `inplace=True` modifica el DataFrame directamente.
    df.drop_duplicates(subset=subset_cols, keep='first', inplace=True)

    return df


# Cargamos los datos usando nuestra función cacheada

# Cargamos los datos usando nuestra función cacheada
data = load_data("./data/processed/data_dondevivir_analisis.csv")


## Variables
distritos = data["distrito"].unique()
inmueble = data["inmueble"].unique()
operacion = data["operacion"].unique()
estacionamientos = data["tiene_estacionamientos"].unique()


## ==================##
##    Funciones      ##
## ==================##

def display_kpis(df: pd.DataFrame, operation: str, distrito: str, inmueble: str):
    """Calcula y muestra los KPIs de precios para una operación específica."""
    
    if operation == "alquiler":
        price_col = "precio_pen"
        symbol = "S/"
        title = f"KPIs de precios en Alquiler ({symbol}) en {distrito}"
    else:  # venta
        price_col = "precio_usd"
        symbol = "$"
        title = f"KPIs de precios en Venta ({symbol}) en {distrito}"

    df_kpi = df.copy()
    df_kpi[price_col] = pd.to_numeric(df_kpi[price_col], errors="coerce")
    df_kpi.dropna(subset=[price_col], inplace=True)

    st.subheader(title, divider="blue")

    if df_kpi.empty:
        st.info("No hay datos de precios para mostrar KPIs.")
        return

    # --- MEJORA: Calcular métricas globales para comparación ---
    df_global = data[
        (data["inmueble"] == inmueble) &
        (data["operacion"] == operation)
    ].copy()
    
    
    df_global[price_col] = pd.to_numeric(df_global[price_col], errors="coerce")
    global_avg = df_global[price_col].mean()
    global_md = df_global[price_col].median()

    # --- Cálculo de métricas locales ---
    
    fmt = lambda x: f"{symbol} {x:,.0f}"
    
    district_avg = df_kpi[price_col].mean()
    delta_avg = district_avg - global_avg

    district_md = df_kpi[price_col].median()
    delta_md = district_md - global_md
    
    c1, c2, c3 = st.columns(3)
    with c1: st.metric(f"🚪 Total {inmueble}", len(df_kpi))
    with c2: st.metric("Mínimo", fmt(df_kpi[price_col].min()))
    with c3: st.metric("Máximo", fmt(df_kpi[price_col].max()))
    
    c4, c5 = st.columns(2)
    with c4: 
        st.metric(
            label="Promedio", 
            value=fmt(district_avg), 
            delta=f"{delta_avg:,.0f} vs. promedio general",
        )
    with c5: 
        st.metric(
            label="Mediana", 
            value=fmt(district_md), 
            delta=f"{delta_md:,.0f} vs. mediana general",
        )

def display_details_table(df: pd.DataFrame, operation: str):
    """Muestra la tabla de detalles de propiedades para una operación específica."""
    
    df_display = df.copy()
    
    df_display["detalle"] = df_display["detalle"].fillna("")
    df_display["caracteristica"] = df_display["caracteristica"].fillna("")

    # Truncar texto visible
    df_display["detalle_short"] = (
        df_display["detalle"].str.slice(0, 35) + "..."
    )

    # Configuración base común para ambas operaciones
    config = {
        "fuente": st.column_config.TextColumn("Fuente", disabled=True),
        "direccion": st.column_config.TextColumn("Dirección", disabled=True),
        "area": st.column_config.NumberColumn("Área", format="%d m²", width="small", disabled=True),
        "dormitorio": st.column_config.NumberColumn("Dorm.", width="small", disabled=True),
        "banios": st.column_config.NumberColumn("Baños", width="small", disabled=True),
        "estacionamientos": st.column_config.NumberColumn("Estac.", width="small", disabled=True),
        "caracteristica": st.column_config.TextColumn("Características", disabled=True),
        "detalle": st.column_config.TextColumn("Detalle", disabled=True),
        "enlace": st.column_config.LinkColumn("Anuncio", display_text= "Abrir", validate=r"^https?://.*$"),
    }

    if operation == "alquiler":
        price_col = "precio_pen"
        cols_to_show = ["enlace", "fuente", "direccion", "precio_pen", "area", "dormitorio", "banios", "estacionamientos", "mantenimiento", "caracteristica", "detalle"]
        config.update({
            "precio_pen": st.column_config.NumberColumn("Precio (S/.)", format="S/. %d", disabled=True),
            "mantenimiento": st.column_config.NumberColumn("Mant. (S/.)", format="S/. %d", disabled=True),
            "detalle_short": st.column_config.TextColumn(
        "Detalle",
        help="Pasa el mouse para ver el detalle completo",
        disabled=True
    )
        })
    else:  # venta
        price_col = "precio_usd"
        cols_to_show = ["enlace", "fuente", "direccion", "precio_usd", "area", "dormitorio", "banios", "estacionamientos", "caracteristica", "detalle"]
        config.update({
            "precio_usd": st.column_config.NumberColumn("Precio ($)", format="$ %d", disabled=True),
        })

    existing_cols = [col for col in cols_to_show if col in df_display.columns]
    
    st.data_editor(
        df_display[existing_cols].sort_values(price_col, ascending=True),
        hide_index=True, use_container_width=True, column_config=config, disabled=True
    )

## ==================##
##      Pestañas     ##
## ==================##

tab1, tab2, tab3 = st.tabs(["Análisis Descriptivo por Distrito", "Alquiler", "Venta"])


## ===========================##
##      Analisis Distrito     ##
## ===========================##

with tab1:

    c1, c2, c3 = st.columns(3, gap="small")
    with c1:
        st.markdown("**Inmueble**")
        input_inmueble = st.selectbox(
            "Inmueble", inmueble, key="f_inm",
            label_visibility="collapsed"
        )
        
    with c2:
        st.markdown("**Operación**")
        input_operacion = st.selectbox(
            "Operación", operacion, key="f_ope",
            label_visibility="collapsed"
        )
        
    with c3:
        st.markdown("**Zona de Lima**")
        # Usamos la nueva columna 'distrito_categoria' para el filtro
        zonas = ['Todos','Lima Top', 'Lima Moderna', 'Lima Centro',  'Lima Este', 'Lima Norte',  'Lima Sur']
        input_zona = st.selectbox(
            "zona"
            , zonas
            , key="f_zona"
            , label_visibility="collapsed"
            , index=0
        )

    col_precio = "precio_usd" if input_operacion == "venta" else "precio_pen"
    simbolo   = "US$" if input_operacion == "venta" else "S/"
    
    
    ## Filtrado de Alquiler
    if input_zona == "Todos":
        df_filtrado = data[
            (data["inmueble"] == input_inmueble) &
            (data["operacion"] == input_operacion) 
        ].copy()
        
    else:
        df_filtrado = data[
            (data["inmueble"] == input_inmueble) &
            (data["operacion"] == input_operacion) &
            (data["zona"] == input_zona) # Filtro por la nueva zona
        ].copy()

    data_agrupada = df_filtrado.groupby("distrito")
    data_agrupada_df = data_agrupada[col_precio].agg(
        n="count",
        min="min", max="max",
        p05=lambda s: s.quantile(0.05),
        q1=lambda s: s.quantile(0.25),
        median="median",
        q3=lambda s: s.quantile(0.75).round(2),
        p95=lambda s: s.quantile(0.95).round(2)
    )

    cols_precios = [c for c in data_agrupada_df.columns if c != "n"]
    data_agrupada_df_fmt = data_agrupada_df.copy()
    data_agrupada_df_fmt[cols_precios] = data_agrupada_df_fmt[cols_precios]\
        .applymap(lambda x: f"{simbolo} {x:,.0f}")
    
    st.subheader(f"Resumen de {input_inmueble} en {input_operacion} para **{input_zona}**")
    
    st.data_editor(
        data_agrupada_df_fmt.sort_values("n", ascending=False),
        use_container_width=True,
        column_config={
            "distrito": st.column_config.TextColumn("Distrito", disabled=True)
        },
        disabled=True,
        key="data_agrupada_fmt"
    )
    
    
    st.subheader(f"Gráficos Interactivos para {input_inmueble} en {input_operacion} en {input_zona}", divider="blue")

    if df_filtrado.empty:
        st.warning("No hay datos suficientes para generar gráficos con los filtros seleccionados.")
    else:
        # Gráfico 1: Distribución de Precios por Distrito (Box Plot)
        # Este gráfico es ideal para comparar la dispersión de precios entre distritos.
        st.markdown(f"##### Distribución de Precios de {input_inmueble} en {input_operacion}")
        fig1 = px.box(df_filtrado, 
                    x="distrito", 
                    y=col_precio,
                    color="distrito",
                    points="all",
                    labels={"distrito": "Distrito", col_precio: f"Precio ({simbolo})"})
        fig1.update_layout(showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)

        # --- Columnas para los siguientes gráficos ---
        g1, g2 = st.columns(2)

        with g1:
            # Gráfico 2: Número de Propiedades por Distrito (Bar Chart)
            st.markdown("##### Cantidad de Propiedades por Distrito")
            prop_por_distrito = df_filtrado['distrito'].value_counts().sort_values(ascending=True) 
            prop_por_distrito_df = pd.DataFrame(prop_por_distrito)
            st.bar_chart(prop_por_distrito_df, horizontal=True)

        with g2:
            # Gráfico 3: Precio Promedio por m² por Distrito (Bar Chart)
            st.markdown(f"##### Precio Promedio por m² ({simbolo})")
            df_plot = df_filtrado[(df_filtrado['area_promedio'] > 0) & (df_filtrado[col_precio] > 0)].copy()
            if not df_plot.empty:
                df_plot['precio_m2'] = round(df_plot[col_precio] / df_plot['area_promedio'],2)
                precio_m2_distrito = df_plot.groupby('distrito')['precio_m2'].mean().round(2).sort_values(ascending=False)
                st.bar_chart(precio_m2_distrito, horizontal=True)
            else:
                st.info("No hay datos de área o precio para calcular el precio por m².")

        # Gráfico 4: Relación Área vs. Precio (Scatter Plot)
        st.markdown(f"##### Relación Área vs. Precio para {input_inmueble}")
        # Filtrar outliers para una mejor visualización, mostrando el 95% de los datos
        area_limite = df_filtrado['area_promedio'].quantile(0.95)
        precio_limite = df_filtrado[col_precio].quantile(0.95)
        
        df_scatter = df_filtrado[
            (df_filtrado['area_promedio'] > 0) & (df_filtrado[col_precio] > 0) &
            (df_filtrado['area_promedio'] <= area_limite) & 
            (df_filtrado[col_precio] <= precio_limite)
        ].copy()

        if not df_scatter.empty:
            fig4 = px.scatter(df_scatter, x="area_promedio", y=col_precio, color="distrito",
                            hover_data=['direccion'], title=f"Precio vs. Área (mostrando el 95% de los datos)",
                            labels={"area_promedio": "Área (m²)", col_precio: f"Precio ({simbolo})"})
            st.plotly_chart(fig4, use_container_width=True)
    
## =================================##
## PESTAÑA de ALquiler por Distrito ##
## =================================##

with tab2:
    
    st.subheader("Propiedades en Alquiler", divider="blue")
    st.write("Seleccione el Distrito de interes y el tipo de inmueble que desea ver")
    
    c1, c2 = st.columns([2, 2], gap="small")
    with c1:
        st.markdown("**Distrito**")
        input_distrito = st.selectbox(
            "Distrito", distritos, key="alquiler_distrito" ,
            label_visibility="collapsed"
        )
    with c2:
        st.markdown("**Inmueble**")
        inmueble_alquiler_ = ["departamentos"]
        input_inmueble = st.selectbox(
            "Inmueble", inmueble_alquiler_, key="alquiler_inmueble" ,
            label_visibility="collapsed"
        )
    
    ## Filtrado de Alquiler
    df_filtrado_aquiler = data[
        (data["inmueble"] == input_inmueble) &
        (data["distrito"] == input_distrito) &
        (data["operacion"] == "alquiler")
    ].copy()
    
    
    ## =============================##
    ## KPI de ALquiler por Distrito ##
    ## =============================##
    
    display_kpis(df_filtrado_aquiler, "alquiler", input_distrito, input_inmueble)
    
    ## =======================================##
    ## TABLA Detalle de ALquiler por Distrito ##
    ## =======================================##
    
    st.subheader(f"Lista de {input_inmueble} en Alquiler en {input_distrito}", divider="blue")
        
    d1, d2, d3, d4 = st.columns(4, gap="small")
    with d1:
        st.markdown("**Precio**")
        labels_alquiler_precio = ["Todos" , "Hasta S/1.5k", "De S/1.5k a S/2.5k", "De S/2.5 a S/3.5k", "De S/3.5k a S/4.5k", "De S/4.5k a más"]
        input_rango_precio_aquiler = st.selectbox(
            "seleccione el precio:"
            , options=labels_alquiler_precio
            , key="rango_precio_alquiler" # <- Clave única para el widget
            , index=0
        )
        
    with d2:
        st.markdown("**Área**")       
        labels_area = ["Todos", "Hasta 50m2", "De 50m2 a 100m2", "De 100m2 a 200m2", "De 200m2 a 300m2", "De 300m2 a más"]
        input_rango_area_alquiler = st.selectbox(
            "seleccione el area:"
            , options=labels_area
            , key="rango_area_alquiler" # <- Clave única para el widget
            , index=0 
            
        )
        
    with d3:
        st.markdown("**Dormitorios**")       
        labels_dorm = ["Todos", "1 Dormitorio", "2 Dormitorios", "3 Dormitorios", "4 Dormitorios", "5 o más Dormitorios"]
        input_dormitorio_alquiler = st.selectbox(
            "seleccione el número de dormitorios:"
            , options=labels_dorm
            , key="dormitorio_alquiler" # <- Clave única para el widget
            , index=0 
            
        )
        
    with d4:
        st.markdown("**Estacionamiento**")       
        labels_est = ["Todos", "Si", "No"]
        input_estacionamiento_alquiler = st.selectbox(
            "Le interesa es estacionamiento:"
            , options=labels_est
            , key="estacionamiento_alquiler" # <- Clave única para el widget
            , index=0 
            
        )
        
    # Se crea una copia del DataFrame filtrado por distrito para aplicar los filtros de rango.
    df_tabla_alquiler = df_filtrado_aquiler.copy()

    # Se aplica el filtro de rango de precio si no es "Todos".
    if input_rango_precio_aquiler != "Todos":
        df_tabla_alquiler = df_tabla_alquiler[df_tabla_alquiler["precio_alquiler_agp"] == input_rango_precio_aquiler]

    # Se aplica el filtro de rango de área si no es "Todos".
    if input_rango_area_alquiler != "Todos":
        df_tabla_alquiler = df_tabla_alquiler[df_tabla_alquiler["area_agp"] == input_rango_area_alquiler]
    
    # Se aplica el filtro de numero de habitaciones si no es "Todos".
    if input_dormitorio_alquiler != "Todos":
        df_tabla_alquiler = df_tabla_alquiler[df_tabla_alquiler["dormitorios"] == input_dormitorio_alquiler]
        
    # Se aplica el filtro de estacionamientos si no es "Todos".
    if input_estacionamiento_alquiler != "Todos":
        df_tabla_alquiler = df_tabla_alquiler[df_tabla_alquiler["estacionamiento_gp"] == input_estacionamiento_alquiler]

    # Usamos la función refactorizada para mostrar la tabla
    display_details_table(df_tabla_alquiler, "alquiler")
    
    
## ===============================##
## PESTAÑA de Ventas por Distrito ##
## ===============================##

with tab3:
    
    st.subheader("Propiedades en Venta", divider="blue")
    
    c1, c2 = st.columns([2, 2], gap="small")
    with c1:
        st.markdown("**Distrito**")
        input_distrito = st.selectbox(
            "Distrito", distritos,key="venta_distrito" ,     # <- clave única
            label_visibility="collapsed"
        )
    with c2:
        st.markdown("**Inmueble**")
        inmueble_venta_ = ["departamentos", "casas"]
        input_inmueble = st.selectbox(
            "Inmueble", inmueble_venta_, key="venta_inmueble"  ,     # <- clave única
            label_visibility="collapsed"
        )

    
    ## Filtrado de Alquiler
    df_filtrado_venta = data[
        (data["inmueble"] == input_inmueble) &
        (data["distrito"] == input_distrito) &
        (data["operacion"] == "venta")
    ].copy()
    
    ## ==========================##
    ## KPI de Venta por Distrito ##
    ## ==========================##
    
    display_kpis(df_filtrado_venta, "venta", input_distrito, input_inmueble)

    ## ====================================##
    ## TABLA Detalle de Venta por Distrito ##
    ## ====================================##
    
    st.subheader(f"Lista de {input_inmueble} en Venta en {input_distrito}", divider="blue")
    
    e1, e2, e3, e4 = st.columns(4, gap="small")
    with e1:
        st.markdown("**Precio**")
        # Se corrigen las etiquetas para que los rangos no se superpongan.
        labels_venta_precio = ["Todos", "Hasta $ 50k", "De $ 50k a $ 100k", "De $ 100k a $ 200k", "De $ 200k a $ 500k", "De $ 500k a más"]
        input_rango_precio_venta = st.selectbox(
            "seleccione el precio:"
            , options=labels_venta_precio
            , index=0
            , key="rango_precio_venta"
        )
    with e2:
        st.markdown("**Área**")       
        labels_area_venta = ["Todos", "Hasta 50m2", "De 50m2 a 100m2", "De 100m2 a 200m2", "De 200m2 a 300m2", "De 300m2 a más"]
        input_rango_area_venta = st.selectbox(
            "seleccione el area:"
            , options=labels_area_venta
            , index=0 
            , key="rango_area_venta"
        )
        
    with e3:
        st.markdown("**Dormitorios**")       
        labels_dorm = ["Todos", "1 Dormitorio", "2 Dormitorios", "3 Dormitorios", "4 Dormitorios", "5 o más Dormitorios"]
        input_dormitorio_venta = st.selectbox(
            "seleccione el número de dormitorios:"
            , options=labels_dorm
            , key="dormitorio_venta" # <- Clave única para el widget
            , index=0 
            
        )
        
    with e4:
        st.markdown("**Estacionamiento**")       
        labels_est = ["Todos", "Si", "No"]
        input_estacionamiento_venta = st.selectbox(
            "Le interesa es estacionamiento:"
            , options=labels_est
            , key="estacionamiento_venta" # <- Clave única para el widget
            , index=0 
            
        )    
        
    # Se crea una copia del DataFrame filtrado por distrito para aplicar los filtros de rango.
    df_tabla_venta = df_filtrado_venta.copy()

    # Se aplica el filtro de rango de precio si no es "Todos".
    if input_rango_precio_venta != "Todos":
        df_tabla_venta = df_tabla_venta[df_tabla_venta["precio_venta_agp"] == input_rango_precio_venta]

    # Se aplica el filtro de rango de área si no es "Todos".
    if input_rango_area_venta != "Todos":
        df_tabla_venta = df_tabla_venta[df_tabla_venta["area_agp"] == input_rango_area_venta]
        
    # Se aplica el filtro de numero de habitaciones si no es "Todos".
    if input_dormitorio_venta != "Todos":
        df_tabla_venta = df_tabla_venta[df_tabla_venta["dormitorios"] == input_dormitorio_venta]
        
    # Se aplica el filtro de estacionamientos si no es "Todos".
    if input_estacionamiento_venta != "Todos":
        df_tabla_venta = df_tabla_venta[df_tabla_venta["estacionamiento_gp"] == input_estacionamiento_venta]
    
    # Usamos la función refactorizada para mostrar la tabla
    display_details_table(df_tabla_venta, "venta")
