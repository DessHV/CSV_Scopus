import streamlit as st
import pandas as pd

from src.config import APP_TITLE, DEFAULT_CSV_PATH, RESEARCH_QUESTION, KEYWORDS
from src.data_loader import load_csv, validate_scopus_columns
from src.preprocessing import prepare_dataframe, get_summary_metrics
from src.visualizations import (
    plot_publications_by_year,
    plot_top_cited_articles,
    plot_sources_distribution,
    plot_document_types,
    plot_open_access,
    plot_top_authors,
    plot_keyword_frequency,
)
from src.text_analysis import get_top_words_from_abstracts


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title(APP_TITLE)
st.caption("Dashboard interactivo para analizar artículos científicos exportados desde Scopus.")

with st.expander("📌 Pregunta de investigación y keywords", expanded=True):
    st.markdown(f"**Pregunta de investigación:** {RESEARCH_QUESTION}")
    st.markdown("**Keywords usadas:** " + " · ".join([f"`{k}`" for k in KEYWORDS]))
    st.info(
        "Puedes cargar un CSV local desde la barra lateral o usar el dataset incluido en el proyecto. "
        "El dashboard detecta automáticamente columnas clave como autores, título, año, citas, abstract y keywords."
    )

st.sidebar.header("📁 Fuente de datos")
data_source = st.sidebar.radio(
    "Selecciona cómo cargar el CSV:",
    ["Usar CSV incluido", "Subir CSV local", "Leer CSV desde URL de GitHub"],
)

uploaded_file = None
github_url = ""

if data_source == "Subir CSV local":
    uploaded_file = st.sidebar.file_uploader("Sube tu archivo CSV de Scopus", type=["csv"])
    csv_source = uploaded_file
elif data_source == "Leer CSV desde URL de GitHub":
    github_url = st.sidebar.text_input(
        "Pega el enlace RAW del CSV en GitHub",
        placeholder="https://raw.githubusercontent.com/usuario/repositorio/main/data/scopus.csv",
    )
    csv_source = github_url.strip() if github_url.strip() else None
else:
    csv_source = DEFAULT_CSV_PATH

if csv_source is None:
    st.warning("Carga un archivo CSV o pega una URL RAW de GitHub para iniciar.")
    st.stop()

try:
    raw_df = load_csv(csv_source)
except Exception as exc:
    st.error(f"No se pudo leer el archivo CSV. Detalle: {exc}")
    st.stop()

missing = validate_scopus_columns(raw_df)
df = prepare_dataframe(raw_df)

if missing:
    st.warning(
        "El archivo fue cargado, pero faltan algunas columnas recomendadas para Scopus: "
        + ", ".join(missing)
    )
else:
    st.success("CSV cargado correctamente con las columnas principales de Scopus.")

st.sidebar.header("🔎 Filtros")
years = sorted(df["Year"].dropna().astype(int).unique().tolist()) if "Year" in df.columns else []

if years:
    min_year, max_year = min(years), max(years)
    selected_years = st.sidebar.slider(
        "Rango de años",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
    )
    df = df[(df["Year"] >= selected_years[0]) & (df["Year"] <= selected_years[1])]

doc_types = sorted(df["Document Type"].dropna().unique().tolist()) if "Document Type" in df.columns else []
if doc_types:
    selected_doc_types = st.sidebar.multiselect(
        "Tipo de documento",
        options=doc_types,
        default=doc_types,
    )
    df = df[df["Document Type"].isin(selected_doc_types)]

search_text = st.sidebar.text_input("Buscar por título, autor o keyword")
if search_text:
    search_cols = [c for c in ["Title", "Authors", "Author Keywords", "Index Keywords", "Abstract"] if c in df.columns]
    mask = pd.Series(False, index=df.index)
    for col in search_cols:
        mask = mask | df[col].astype(str).str.contains(search_text, case=False, na=False)
    df = df[mask]

metrics = get_summary_metrics(df)

st.subheader("📊 Métricas generales")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Artículos", metrics["articles"])
m2.metric("Años analizados", metrics["years"])
m3.metric("Citas totales", metrics["citations"])
m4.metric("Promedio de citas", metrics["avg_citations"])

st.divider()

tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Producción científica",
    "🏆 Impacto y autores",
    "🔤 Keywords y abstracts",
    "📄 Dataset",
])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        fig = plot_publications_by_year(df)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = plot_sources_distribution(df)
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        fig = plot_document_types(df)
        st.plotly_chart(fig, use_container_width=True)
    with c4:
        fig = plot_open_access(df)
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    c1, c2 = st.columns([1.3, 1])
    with c1:
        fig = plot_top_cited_articles(df)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = plot_top_authors(df)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        "Los artículos con más citas ayudan a identificar investigaciones influyentes dentro del tema seleccionado."
    )

with tab3:
    c1, c2 = st.columns(2)
    with c1:
        fig = plot_keyword_frequency(df)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        top_words = get_top_words_from_abstracts(df, top_n=20)
        st.dataframe(top_words, use_container_width=True, hide_index=True)

    st.markdown(
        "El análisis de palabras en abstracts y keywords permite identificar conceptos recurrentes asociados al tema."
    )

with tab4:
    st.subheader("Tabla de artículos")
    preferred_cols = [
        "Authors", "Title", "Year", "Source title", "Cited by", "DOI",
        "Author Keywords", "Index Keywords", "Abstract"
    ]
    visible_cols = [c for c in preferred_cols if c in df.columns]
    st.dataframe(df[visible_cols], use_container_width=True, hide_index=True)

    csv_download = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Descargar dataset filtrado",
        data=csv_download,
        file_name="scopus_filtrado.csv",
        mime="text/csv",
    )

st.divider()
st.markdown(
    """
    **Conclusión orientativa:** este dashboard permite observar la evolución de publicaciones, 
    fuentes principales, artículos más citados y términos frecuentes relacionados con la pregunta de investigación.
    """
)
