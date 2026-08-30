from pathlib import Path

import pandas as pd

SENTINELAS_TSE = [
    "#NULO",
    "#NE",
    "#NULO#",
    "-1",
    "-3",
    "NÃO DIVULGÁVEL",
]

def ler_tse(caminho: Path) -> pd.DataFrame:
    """Lê um CSV do TSE (separador ; encoding Latin-1)
        e devolve um dataframe com os dados do TSE"""
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    tabela = pd.read_csv(
        caminho,
        sep=';',
        encoding="latin-1",
        dtype=str,
        na_values=SENTINELAS_TSE,
        keep_default_na=True,
    )
    return tabela