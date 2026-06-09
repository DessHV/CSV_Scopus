import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter
import re

# --- CONFIGURACIÓN DE DATOS ---
GITHUB_CSV_URL = "data/scopus_instagram_social_development.csv"

# --- PALETA DE COLORES (Inspiración Instagram / Autoestima) ---
C_PURPLE = "#833AB4" 
C_PINK = "#C13584" 
C_ORANGE = "#F56040" 
C_YELLOW = "#FFDC80" 
BG_GRAY = "#F9FAFB"

st.set_page_config(
    page_title="Informe: Instagram y Autoestima",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- ESTILOS CSS INYECTADOS ---
st.markdown(f"""
    <style>
    .hero-banner {{
        background: linear-gradient(135deg, {C_PURPLE} 0%, {C_PINK} 50%, {C_ORANGE} 100%);
        padding: 40px 30px; border-radius: 12px; color: white; margin-bottom: 30px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }}
    .hero-title {{ font-size: 2.6rem; font-weight: 800; margin-bottom: 10px; line-height: 1.2; }}
    .hero-subtitle {{ font-size: 1.2rem; font-weight: 400; opacity: 0.95; }}
    .section-title {{
        font-size: 1.6rem; font-weight: 700; color: #1F2937; margin-top: 35px; 
        border-bottom: 2px solid {C_PINK}; padding-bottom: 8px; margin-bottom: 20px;
    }}
    .metric-card {{
        background-color: {BG_GRAY}; padding: 15px; border-radius: 8px; 
        border-left: 4px solid {C_PURPLE}; margin-bottom: 15px;
    }}
    </style>
""", unsafe_allow_html=True)

# --- CARGA Y LIMPIEZA DE DATOS ---
@st.cache_data(show_spinner=False)
def load_data(source):
    return pd.read_csv(source)

def prepare_data(df):
    df_clean = df.copy()
    if "Year" in df_clean.columns: 
        df_clean["Year"] = pd.to_numeric(df_clean["Year"], errors="coerce").fillna(0).astype(int)
    if "Cited by" in df_clean.columns: 
        df_clean["Cited by"] = pd.to_numeric(df_clean["Cited by"], errors="coerce").fillna(0).astype(int)
    return df_clean

def get_terms(df_col, is_abstract=False):
    text = " ".join(df_col.dropna().astype(str).tolist()).lower()
    if is_abstract:
        words = re.findall(r'\b[a-z]{4,}\b', text)
        stops = {"this", "that", "with", "from", "study", "results", "paper", "research", "were", "have", "data", "analysis", "using", "associated", "participants", "findings", "among", "between", "social", "media", "instagram", "adolescents", "students", "youth", "their", "also", "showed", "levels", "used", "which"}
        filtered = [w for w in words if w not in stops]
    else:
        filtered = [w.strip() for w in text.split(";") if w.strip()]
    return pd.DataFrame(Counter(filtered).most_common(12), columns=["Término", "Frecuencia"])

# --- BANNER PRINCIPAL ---
st.markdown(f"""
    <div class="hero-banner">
        <div class="hero-title">El Espejo Digital: Instagram y la Autoestima Adolescente</div>
        <div class="hero-subtitle">Mapeo bibliométrico interactivo de la evidencia científica.</div>
    </div>
""", unsafe_allow_html=True)

# --- MENU LATERAL: FUENTE DE DATOS (3 OPCIONES) ---
st.sidebar.markdown("### 📁 Fuente de Datos")
data_source = st.sidebar.radio(
    "Selecciona el método de carga:",
    ["Dataset Incluido", "Enlace Externo (URL)", "Subir archivo (Local)"]
)

raw_data = None

if data_source == "Dataset Incluido":
    st.sidebar.success("Usando el dataset oficial de la investigación.")
    raw_data = GITHUB_CSV_URL

elif data_source == "Enlace Externo (URL)":
    github_input = st.sidebar.text_input("Ingresa la URL RAW del CSV:")
    if github_input:
        raw_data = github_input

elif data_source == "Subir archivo (Local)":
    # El parámetro type=["csv"] restringe estrictamente los formatos permitidos en el explorador de archivos del usuario
    uploaded_file = st.sidebar.file_uploader("Sube tu archivo exportado de Scopus", type=["csv"])
    if uploaded_file is not None:
        raw_data = uploaded_file

# --- VALIDACIÓN DE CARGA ---
if raw_data is None or raw_data == "https://raw.githubusercontent.com/usuario/repositorio/main/scopus_export.csv":
    st.info("👈 Por favor, carga un archivo local o configura la URL en el panel lateral para iniciar el informe.")
    st.stop()

try:
    df = prepare_data(load_data(raw_data))
except Exception as e:
    st.error(f"Error al procesar los datos. Asegúrate de que el formato sea un CSV válido. Detalle técnico: {e}")
    st.stop()

# --- PANEL INTERACTIVO: FILTROS ---
st.sidebar.markdown("### ⚙️ Parámetros del Dashboard")
if "Year" in df.columns:
    years = [y for y in df["Year"].unique() if y > 0]
    if len(years) > 1:
        min_y, max_y = min(years), max(years)
        selected_years = st.sidebar.slider("Ventana Temporal", min_y, max_y, (min_y, max_y))
        df = df[(df["Year"] >= selected_years[0]) & (df["Year"] <= selected_years[1])]

search_term = st.sidebar.text_input("Buscador Libre (Conceptos/Autores)")
if search_term:
    cols = [c for c in ["Title", "Abstract", "Author Keywords", "Authors"] if c in df.columns]
    mask = pd.Series(False, index=df.index)
    for c in cols: 
        mask = mask | df[c].astype(str).str.contains(search_term, case=False, na=False)
    df = df[mask]

# --- SECCIÓN: KPIs GLOBALES ---
st.markdown('<div class="metric-card">', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
c1.metric("📚 Estudios Evaluados", len(df))
c2.metric("⏱️ Años de Actividad", df["Year"][df["Year"] > 0].nunique() if "Year" in df.columns else 0)
c3.metric("🎯 Total de Citas", f"{int(df['Cited by'].sum()) if 'Cited by' in df.columns else 0:,}")
c4.metric("👥 Autores Únicos", len(set(df["Authors"].dropna().str.split(";").explode().str.strip())) if "Authors" in df.columns else 0)
st.markdown('</div>', unsafe_allow_html=True)

# --- SECCIÓN 1: DISTRIBUCIÓN POR AÑO ---
st.markdown('<div class="section-title">1. Crecimiento de la Investigación (Interés Académico)</div>', unsafe_allow_html=True)
if "Year" in df.columns:
    data_year = df[df["Year"] > 0]["Year"].value_counts().reset_index().sort_values("Year")
    data_year.columns = ["Año", "Publicaciones"]
    fig1 = px.area(data_year, x="Año", y="Publicaciones", template="plotly_white", markers=True)
    fig1.update_traces(line_color=C_PINK, fillcolor='rgba(193, 53, 132, 0.15)', marker=dict(color=C_PURPLE, size=8))
    fig1.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0), xaxis_title="Año de Publicación", yaxis_title="Volumen de Artículos")
    st.plotly_chart(fig1, use_container_width=True)

# --- SECCIÓN 2: ANÁLISIS DE PALABRAS ---
st.markdown('<div class="section-title">2. Anatomía del Impacto: Análisis Semántico</div>', unsafe_allow_html=True)
st.markdown("La extracción de términos clínicos en los resúmenes y palabras clave responde directamente a nuestra pregunta de investigación, visibilizando los efectos medidos por los científicos.")

col_abs, col_kw = st.columns(2)
with col_abs:
    if "Abstract" in df.columns:
        fig_abs = px.bar(get_terms(df["Abstract"], True), x="Frecuencia", y="Término", orientation="h", template="plotly_white", color="Frecuencia", color_continuous_scale=[C_YELLOW, C_ORANGE])
        fig_abs.update_layout(title="Diagnósticos frecuentes en Abstracts", yaxis={'categoryorder':'total ascending'}, showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig_abs, use_container_width=True)

with col_kw:
    if "Author Keywords" in df.columns:
        fig_kw = px.bar(get_terms(df["Author Keywords"]), x="Frecuencia", y="Término", orientation="h", template="plotly_white", color="Frecuencia", color_continuous_scale=["#E5E7EB", C_PURPLE])
        fig_kw.update_layout(title="Keywords Oficiales de los Autores", yaxis={'categoryorder':'total ascending'}, showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig_kw, use_container_width=True)

# --- SECCIÓN 3: AUTORES Y LITERATURA CLAVE ---
st.markdown('<div class="section-title">3. Consenso Empírico: Autores e Investigaciones Relevantes</div>', unsafe_allow_html=True)
col_auth, col_papers = st.columns([1, 1.2])

with col_auth:
    if "Authors" in df.columns:
        authors = df["Authors"].dropna().str.split(";").explode().str.strip()
        data_auth = authors.value_counts().head(10).reset_index()
        data_auth.columns = ["Autor", "Artículos"]
        fig_auth = px.bar(data_auth, x="Artículos", y="Autor", orientation="h", template="plotly_white")
        fig_auth.update_traces(marker_color=C_PINK)
        fig_auth.update_layout(title="Top 10 Autores más Productivos", yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_auth, use_container_width=True)

with col_papers:
    st.markdown("**Top 5 Artículos con Mayor Impacto (Citas)**")
    if "Title" in df.columns and "Cited by" in df.columns:
        top_papers = df.nlargest(5, "Cited by")[["Title", "Year", "Cited by"]]
        for _, r in top_papers.iterrows():
            st.markdown(f"""
            <div style="background:white; padding:10px; border-left:3px solid {C_ORANGE}; margin-bottom:8px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
                <div style="font-weight:600; font-size:0.95rem; color:#1F2937;">{r['Title']}</div>
                <div style="font-size:0.8rem; color:#6B7280; margin-top:4px;">Citas: <b>{r['Cited by']}</b> | Año: {r['Year']}</div>
            </div>
            """, unsafe_allow_html=True)

# --- SECCIÓN 4: EXPLORADOR DE DATOS ---
st.markdown('<div class="section-title">4. Auditoría del Dataset</div>', unsafe_allow_html=True)
with st.expander("Inspeccionar y exportar la matriz de datos de Scopus"):
    st.dataframe(df, use_container_width=True)
    st.download_button("⬇️ Descargar CSV Filtrado", data=df.to_csv(index=False).encode("utf-8"), file_name="analisis_instagram_autoestima.csv", mime="text/csv")
