from collections import Counter
import pandas as pd
import plotly.express as px


def empty_figure(message: str):
    fig = px.scatter(title=message)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig


def plot_publications_by_year(df: pd.DataFrame):
    if "Year" not in df.columns or df.empty:
        return empty_figure("No hay datos de año disponibles")

    data = (
        df.dropna(subset=["Year"])
        .groupby("Year")
        .size()
        .reset_index(name="Cantidad")
        .sort_values("Year")
    )
    data["Year"] = data["Year"].astype(int)

    fig = px.bar(
        data,
        x="Year",
        y="Cantidad",
        text="Cantidad",
        title="Publicaciones por año",
        labels={"Year": "Año", "Cantidad": "Cantidad de artículos"},
    )
    fig.update_traces(textposition="outside")
    return fig


def plot_top_cited_articles(df: pd.DataFrame, top_n: int = 10):
    if not {"Title", "Cited by"}.issubset(df.columns) or df.empty:
        return empty_figure("No hay datos de citas disponibles")

    data = df.sort_values("Cited by", ascending=False).head(top_n).copy()
    data["Titulo corto"] = data["Title"].str.slice(0, 70) + "..."

    fig = px.bar(
        data,
        x="Cited by",
        y="Titulo corto",
        orientation="h",
        title=f"Top {top_n} artículos más citados",
        labels={"Cited by": "Citas", "Titulo corto": "Artículo"},
        hover_data=["Title", "Authors", "Year"] if "Authors" in data.columns else ["Title", "Year"],
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    return fig


def plot_sources_distribution(df: pd.DataFrame, top_n: int = 8):
    if "Source title" not in df.columns or df.empty:
        return empty_figure("No hay fuentes disponibles")

    data = df["Source title"].value_counts().head(top_n).reset_index()
    data.columns = ["Fuente", "Cantidad"]

    fig = px.pie(
        data,
        names="Fuente",
        values="Cantidad",
        title="Fuentes o revistas más frecuentes",
        hole=0.35,
    )
    return fig


def plot_document_types(df: pd.DataFrame):
    if "Document Type" not in df.columns or df.empty:
        return empty_figure("No hay tipos de documento disponibles")

    data = df["Document Type"].value_counts().reset_index()
    data.columns = ["Tipo", "Cantidad"]

    fig = px.bar(
        data,
        x="Tipo",
        y="Cantidad",
        text="Cantidad",
        title="Tipos de documento",
    )
    fig.update_traces(textposition="outside")
    return fig


def plot_open_access(df: pd.DataFrame):
    if "Open Access" not in df.columns or df.empty:
        return empty_figure("No hay datos de acceso abierto disponibles")

    data = df["Open Access"].replace("", "No especificado").value_counts().reset_index()
    data.columns = ["Acceso", "Cantidad"]

    fig = px.bar(
        data,
        x="Acceso",
        y="Cantidad",
        text="Cantidad",
        title="Estado de acceso abierto",
    )
    fig.update_traces(textposition="outside")
    return fig


def plot_top_authors(df: pd.DataFrame, top_n: int = 10):
    if "Authors" not in df.columns or df.empty:
        return empty_figure("No hay datos de autores disponibles")

    authors = []
    for row in df["Authors"].dropna().astype(str):
        authors.extend([a.strip() for a in row.split(";") if a.strip()])

    data = pd.DataFrame(Counter(authors).most_common(top_n), columns=["Autor", "Publicaciones"])

    if data.empty:
        return empty_figure("No hay autores disponibles")

    fig = px.bar(
        data,
        x="Publicaciones",
        y="Autor",
        orientation="h",
        title=f"Top {top_n} autores por cantidad de publicaciones",
        text="Publicaciones",
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    return fig


def plot_keyword_frequency(df: pd.DataFrame, top_n: int = 15):
    keyword_cols = [c for c in ["Author Keywords", "Index Keywords"] if c in df.columns]
    if not keyword_cols or df.empty:
        return empty_figure("No hay keywords disponibles")

    keywords = []
    for col in keyword_cols:
        for row in df[col].dropna().astype(str):
            keywords.extend([k.strip().lower() for k in row.split(";") if k.strip()])

    data = pd.DataFrame(Counter(keywords).most_common(top_n), columns=["Keyword", "Frecuencia"])

    if data.empty:
        return empty_figure("No hay keywords disponibles")

    fig = px.bar(
        data,
        x="Frecuencia",
        y="Keyword",
        orientation="h",
        title=f"Top {top_n} keywords más frecuentes",
        text="Frecuencia",
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    return fig
