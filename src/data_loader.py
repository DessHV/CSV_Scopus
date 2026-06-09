from typing import Union
import pandas as pd
from pathlib import Path


REQUIRED_RECOMMENDED_COLUMNS = [
    "Authors",
    "Title",
    "Year",
    "Source title",
    "Cited by",
    "DOI",
    "Abstract",
    "Author Keywords",
]


def load_csv(source: Union[str, object]) -> pd.DataFrame:
    """Carga un CSV desde ruta local, URL RAW de GitHub o archivo subido en Streamlit."""
    if isinstance(source, str):
        if source.startswith("http"):
            return pd.read_csv(source)
        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"No existe el archivo: {source}")
        return pd.read_csv(path)

    return pd.read_csv(source)


def validate_scopus_columns(df: pd.DataFrame) -> list[str]:
    """Devuelve columnas recomendadas faltantes."""
    cols = set(df.columns)
    return [col for col in REQUIRED_RECOMMENDED_COLUMNS if col not in cols]
