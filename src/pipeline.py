from pathlib import Path
import tempfile

import pandas as pd

import os

from src.caminhos import BRONZE
from src.gold import (
    agregar_competitividade,
    agregar_cruzamento_genero_raca,
    agregar_patrimonio_candidato,
    agregar_patrimonio_cargo,
    agregar_patrimonio_por,
    agregar_representatividade_cargo,
    agregar_representatividade_partido,
)
from src.leitura import ler_tse
from src.s3_io import baixar_csv, enviar_csv
from src.silver import (
    montar_dim_candidato,
    montar_dim_vagas,
    montar_fato_bens,
    montar_fato_redes,
)

def carregar_bronze() -> dict[str, pd.DataFrame]:
    """Lê o bronze no s3"""
    return {
        nome: ler_tse(baixar_csv(chave))
        for nome, chave in BRONZE.items()
    }

def montar_silver(bronze: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Transforma bronze em tabelas de grão certo."""
    return {
        "dim_candidato": montar_dim_candidato(bronze["cand"], bronze["comp"]),
        "dim_vagas": montar_dim_vagas(bronze["vagas"]),
        "fato_bens": montar_fato_bens(bronze["bens"]),
        "fato_redes": montar_fato_redes(bronze["redes"]),
    }

def montar_gold(silver: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    dim = silver["dim_candidato"]
    por_pessoa = agregar_patrimonio_candidato(dim, silver["fato_bens"])
    return {
        "competitividade": agregar_competitividade(dim, silver["dim_vagas"]),
        "patrimonio_candidato": por_pessoa,
        "patrimonio_cargo": agregar_patrimonio_cargo(por_pessoa),
        "patrimonio_genero": agregar_patrimonio_por(por_pessoa, "genero"),
        "patrimonio_raca": agregar_patrimonio_por(por_pessoa, "cor_raca"),
        "representatividade_cargo": agregar_representatividade_cargo(dim),
        "representatividade_partido": agregar_representatividade_partido(dim),
        "cruzamento_genero_raca": agregar_cruzamento_genero_raca(dim),
    }

def gravar_tabelas(tabelas: dict[str, pd.DataFrame], prefixo: str) -> None:
    """Grava cada DataFrame em s3://bucket/prefixo/nome.csv"""
    for nome, tabela in tabelas.items():
        fd, caminho = tempfile.mkstemp(suffix=".csv")
        os.close(fd)
        local = Path(caminho)
        tabela.to_csv(local, index=False)
        enviar_csv(local, f"{prefixo}/{nome}.csv")
        local.unlink(missing_ok=True)

def imprimir_resumo(
        silver: dict[str, pd.DataFrame],
        gold: dict[str, pd.DataFrame],
) -> None:
    """Imprimir resumo das transformações."""
    dim = silver["dim_candidato"]
    bens = silver["fato_bens"]
    redes = silver["fato_redes"]
    por_pessoa = gold["patrimonio_candidato"]

    print("silver dim_candidato:", dim.shape)
    print("cpf vazou?", any("cpf" in c for c in dim.columns))
    print("sq duplicado no dim?", dim["sq_candidato"].duplicated().any())
    print("fato_bens:", len(bens), "linhas |", bens["sq_candidato"].nunique(), "sq")
    print("redes órfãs:", (~redes["sq_candidato"].isin(dim["sq_candidato"])).sum())
    print("vagas (cadeiras):", silver["dim_vagas"]["qtd_vagas"].sum())
    print()
    print(gold["competitividade"].to_string(index=False))
    print()
    print(gold["representatividade_cargo"].to_string(index=False))
    print()
    print(gold["patrimonio_genero"].to_string(index=False))
    print()
    print(gold["patrimonio_cargo"].to_string(index=False))
    print()
    print("patrimonio NaN:", por_pessoa["patrimonio_total"].isna().sum())
    print("silver em s3://bucket/silver/")
    print("gold em s3://bucket/gold/")

def executar() -> None:
    bronze = carregar_bronze()
    silver = montar_silver(bronze)
    gold = montar_gold(silver)
    gravar_tabelas(silver, "silver")
    gravar_tabelas(gold, "gold")
    imprimir_resumo(silver, gold)

