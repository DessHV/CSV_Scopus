import re
from collections import Counter
import pandas as pd


STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "were", "their", "have",
    "has", "are", "was", "using", "use", "used", "between", "among", "into",
    "study", "results", "research", "article", "paper", "based", "data", "more",
    "social", "media", "instagram",
    "de", "la", "el", "en", "y", "los", "las", "del", "con", "por", "para",
    "una", "uno", "que", "como", "sobre", "entre",
}


def tokenize_text(text: str) -> list[str]:
    text = text.lower()
    text = re.sub(r"[^a-záéíóúñü\s]", " ", text)
    words = text.split()
    return [w for w in words if len(w) > 3 and w not in STOPWORDS]


def get_top_words_from_abstracts(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    if "Abstract" not in df.columns or df.empty:
        return pd.DataFrame(columns=["Palabra", "Frecuencia"])

    all_words = []
    for abstract in df["Abstract"].dropna().astype(str):
        all_words.extend(tokenize_text(abstract))

    return pd.DataFrame(Counter(all_words).most_common(top_n), columns=["Palabra", "Frecuencia"])
