import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


st.title("Demo con pestañas (20 registros)")

# --------- DATASET DEMO (>=15 registros) ----------
np.random.seed(42)
n = 20
base_lat, base_lon = -12.121, -77.033
df_demo = pd.DataFrame({
    "fuente": np.where(np.arange(n) % 2 == 0, "adondevivir", "urbania"),
    "direccion": [f"Av. Ejemplo {i+1}, Miraflores" for i in range(n)],
    "precio_pen": np.random.randint(120_000, 500_000, size=n),
    "precio_usd": np.random.randint(30_000, 150_000, size=n),
    "lat": base_lat + np.random.uniform(-0.01, 0.01, size=n),
    "lon": base_lon + np.random.uniform(-0.01, 0.01, size=n),
    "enlace": [f"https://example.com/anuncio/{i+1}" for i in range(n)],
})

# Usa tu data real aquí si quieres:
df = df_demo.copy()
# df = df_result.copy()  # <- descomenta para usar tu DataFrame filtrado

# Normaliza URLs por si acaso
if "enlace" in df.columns:
    df["enlace"] = df["enlace"].apply(
        lambda s: s if pd.isna(s) or str(s).startswith(("http://", "https://")) else f"https://{s}"
    )

# --------- PESTAÑAS ----------
tab1, tab2, tab3 = st.tabs(["🔎 Datos", "📦 Métricas", "📊 Gráfico"])

with tab1:
    st.subheader("Tabla con enlace")
    st.data_editor(
        df[["fuente", "direccion", "precio_pen", "precio_usd", "enlace"]],
        hide_index=True,
        use_container_width=True,
        column_config={
            "fuente": st.column_config.TextColumn("Fuente", disabled=True),
            "direccion": st.column_config.TextColumn("Dirección", disabled=True),
            "precio_pen": st.column_config.NumberColumn("Precio (S/.)", format="S/. %d", disabled=True),
            "precio_usd": st.column_config.NumberColumn("Precio (US$)", format="US$ %d", disabled=True),
            "enlace": st.column_config.LinkColumn("Abrir", display_text="Abrir anuncio", validate=r"^https?://.*$"),
        },
        disabled=["fuente", "direccion", "precio_pen", "precio_usd"],
        key="tabla_con_link",
    )

with tab2:
    st.subheader("KPIs de precios (S/.)")
    # Asegura numérico
    df["precio_pen"] = pd.to_numeric(df["precio_pen"], errors="coerce")
    df_kpi = df.dropna(subset=["precio_pen"])
    # Formato helper
    fmt = lambda x: f"S/. {x:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Total propiedades", len(df_kpi))
    with c2: st.metric("Mínimo", fmt(df_kpi["precio_pen"].min()))
    with c3: st.metric("Máximo", fmt(df_kpi["precio_pen"].max()))
    c4, c5 = st.columns(2)
    with c4: st.metric("Promedio", fmt(df_kpi["precio_pen"].mean()))
    with c5: st.metric("Mediana", fmt(df_kpi["precio_pen"].median()))

with tab3:
    st.subheader("Histograma precios (S/.)")
    df_plot = df.dropna(subset=["precio_pen"])
    if df_plot.empty:
        st.info("No hay datos de precio válidos.")
    else:
        fig = px.histogram(df_plot, x="precio_pen", nbins=20, labels={"precio_pen": "Precio (S/.)"})
        fig.update_xaxes(rangeslider_visible=True)
        fig.update_layout(bargap=0.02)
        st.plotly_chart(fig, use_container_width=True)

        # (Opcional) Mapa rápido si hay lat/lon
        if {"lat", "lon"}.issubset(df.columns):
            st.subheader("Mapa (vista rápida)")
            st.map(df[["lat", "lon"]])
