import pandas as pd

def agregar_competitividade(
        dim_candidato: pd.DataFrame,
        dim_vagas: pd.DataFrame,
) -> pd.DataFrame:
    """Candidatos por cargo ÷ vagas oficiais. 1 linha por codigo_cargo."""
    por_cargo = (
        dim_candidato.groupby("codigo_cargo", as_index=False)
        .agg(
            cargo=("cargo", "first"),
            qtd_candidatos=("sq_candidato", "nunique"),
        )
    )

    tabela = pd.merge(
        por_cargo,
        dim_vagas,
        on="codigo_cargo",
        how="inner",
        validate="one_to_one",
    )

    tabela["candidatos_por_vaga"] = (
        tabela["qtd_candidatos"] / tabela["qtd_vagas"]
    ).round(1)

    return tabela.sort_values("qtd_candidatos", ascending=False).reset_index(drop=True)

def agregar_patrimonio_candidato(
        dim_candidato: pd.DataFrame,
        fato_bens: pd.DataFrame,
) -> pd.DataFrame:
    """1 linha por candidato. Patrimônio ausente fica NaN, não zero."""
    por_pessoa = (
        fato_bens.groupby("sq_candidato", as_index=False)
        .agg(
            qtd_bens=("valor_bem", "count"),
            patrimonio_total=("valor_bem", "sum"),
        )
    )

    colunas_dim = [
        "sq_candidato",
        "nome_civil",
        "nome_urna",
        "codigo_cargo",
        "cargo",
        "sigla_partido",
        "genero",
        "cor_raca",
        "escolaridade",
        "ocupacao",
        "faixa",
        "idade_data_de_posse",
        "uf_nascimento",
        "ST_QUILOMBOLA",
        "ST_DECLARAR_BENS",
    ]
    ficha = dim_candidato[colunas_dim].copy()

    tabela = pd.merge(
        ficha,
        por_pessoa,
        on="sq_candidato",
        how="left",
        validate="one_to_one",
    )

    tabela["qtd_bens"] = tabela["qtd_bens"].fillna(0)
    tabela = tabela.rename(
        columns={
            "ST_DECLARAR_BENS": "declarou_bens",
            "ST_QUILOMBOLA": "quilombola",
        }
    )
    return tabela.reset_index(drop=True)

def agregar_patrimonio_por(
    patrimonio_candidato: pd.DataFrame,
    coluna: str,
) -> pd.DataFrame:
    """Mediana e cobertura da declaração, agrupadas por uma coluna do dim."""
    tabela = (
        patrimonio_candidato.groupby(coluna, as_index=False)
        .agg(
            qtd_candidatos=("sq_candidato", "nunique"),
            qtd_com_patrimonio=("patrimonio_total", "count"),
            mediana_patrimonio=("patrimonio_total", "median"),
        )
    )
    tabela["pct_com_patrimonio"] = (
        tabela["qtd_com_patrimonio"] / tabela["qtd_candidatos"] * 100
    ).round(1)
    tabela["mediana_patrimonio"] = tabela["mediana_patrimonio"].round(2)
    return tabela.sort_values("mediana_patrimonio", ascending=False).reset_index(drop=True)


def agregar_patrimonio_cargo(
    patrimonio_candidato: pd.DataFrame,
) -> pd.DataFrame:
    """Atalho: o mesmo recorte da aula 7, agora via agregar_patrimonio_por."""
    return agregar_patrimonio_por(patrimonio_candidato, "cargo")

def agregar_representatividade_cargo(
    dim_candidato: pd.DataFrame,
) -> pd.DataFrame:
    """1 linha por cargo: gênero, raça, idade, escolaridade, origem."""
    base = dim_candidato.copy()
    base["eh_mulher"] = base["genero"].eq("FEMININO")
    base["eh_preta"] = base["cor_raca"].eq("PRETA")
    base["eh_parda"] = base["cor_raca"].eq("PARDA")
    base["eh_branca"] = base["cor_raca"].eq("BRANCA")
    base["eh_jovem"] = base["faixa"].eq("18-29")
    base["eh_superior"] = base["escolaridade"].eq("SUPERIOR COMPLETO")
    base["nasceu_rj"] = base["uf_nascimento"].eq("RJ")
    base["eh_quilombola"] = base["ST_QUILOMBOLA"].eq("S")
    base["lista_proporcional"] = base["cargo"].isin(
        ["DEPUTADO FEDERAL", "DEPUTADO ESTADUAL"]
    )

    tabela = (
        base.groupby(["codigo_cargo", "cargo"], as_index=False)
        .agg(
            qtd_candidatos=("sq_candidato", "nunique"),
            pct_mulheres=("eh_mulher", "mean"),
            pct_preta=("eh_preta", "mean"),
            pct_parda=("eh_parda", "mean"),
            pct_branca=("eh_branca", "mean"),
            pct_18_29=("eh_jovem", "mean"),
            pct_superior=("eh_superior", "mean"),
            pct_nascidos_rj=("nasceu_rj", "mean"),
            qtd_quilombola=("eh_quilombola", "sum"),
            mediana_idade=("idade_data_de_posse", "median"),
            lista_proporcional=("lista_proporcional", "first"),
        )
    )

    colunas_pct = [
        "pct_mulheres",
        "pct_preta",
        "pct_parda",
        "pct_branca",
        "pct_18_29",
        "pct_superior",
        "pct_nascidos_rj",
    ]
    tabela[colunas_pct] = (tabela[colunas_pct] * 100).round(1)
    tabela["mediana_idade"] = tabela["mediana_idade"].round(1)
    return tabela.sort_values("qtd_candidatos", ascending=False).reset_index(drop=True)

def agregar_representatividade_partido(
    dim_candidato: pd.DataFrame,
) -> pd.DataFrame:
    """1 linha por partido: gênero e raça nas legendas."""
    base = dim_candidato.copy()
    base["eh_mulher"] = base["genero"].eq("FEMININO")
    base["eh_preta"] = base["cor_raca"].eq("PRETA")
    base["eh_parda"] = base["cor_raca"].eq("PARDA")
    base["eh_branca"] = base["cor_raca"].eq("BRANCA")

    tabela = (
        base.groupby("sigla_partido", as_index=False)
        .agg(
            qtd_candidatos=("sq_candidato", "nunique"),
            pct_mulheres=("eh_mulher", "mean"),
            pct_preta=("eh_preta", "mean"),
            pct_parda=("eh_parda", "mean"),
            pct_branca=("eh_branca", "mean"),
        )
    )
    colunas_pct = ["pct_mulheres", "pct_preta", "pct_parda", "pct_branca"]
    tabela[colunas_pct] = (tabela[colunas_pct] * 100).round(1)
    return tabela.sort_values("qtd_candidatos", ascending=False).reset_index(drop=True)


def agregar_cruzamento_genero_raca(
    dim_candidato: pd.DataFrame,
) -> pd.DataFrame:
    """1 linha por par genero × cor_raca."""
    total = dim_candidato["sq_candidato"].nunique()
    tabela = (
        dim_candidato.groupby(["genero", "cor_raca"], as_index=False)
        .agg(qtd=("sq_candidato", "nunique"))
    )
    tabela["pct_do_total"] = (tabela["qtd"] / total * 100).round(1)
    return tabela.sort_values("qtd", ascending=False).reset_index(drop=True)