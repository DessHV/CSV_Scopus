import pandas as pd


def clean_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    text_cols = df.select_dtypes(include=["object"]).columns
    for col in text_cols:
        df[col] = df[col].fillna("").astype(str).str.strip()
    return df


def prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza columnas importantes para análisis y gráficos."""
    df = df.copy()
    df.columns = df.columns.str.strip()
    df = clean_text_columns(df)

    if "Year" in df.columns:
        df["Year"] = pd.to_numeric(df["Year"], errors="coerce")

    if "Cited by" in df.columns:
        df["Cited by"] = pd.to_numeric(df["Cited by"], errors="coerce").fillna(0).astype(int)

    if "Document Type" in df.columns:
        df["Document Type"] = df["Document Type"].replace("", "No especificado")

    if "Open Access" in df.columns:
        df["Open Access"] = df["Open Access"].replace("", "No especificado")

    return df


def get_summary_metrics(df: pd.DataFrame) -> dict:
    articles = len(df)
    years = int(df["Year"].nunique()) if "Year" in df.columns and not df.empty else 0
    citations = int(df["Cited by"].sum()) if "Cited by" in df.columns and not df.empty else 0
    avg_citations = round(citations / articles, 2) if articles > 0 else 0

    return {
        "articles": articles,
        "years": years,
        "citations": citations,
        "avg_citations": avg_citations,
    }
