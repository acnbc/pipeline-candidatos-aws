import pandas as pd

from src.limpeza import (
    classificar_plataforma,
    faixa_etaria,
    parse_data_br,
    parse_real_ponto,
    parse_real_br
)

RENOMEAR_CAND = {
    "SQ_CANDIDATO": "sq_candidato",
    "NR_CANDIDATO": "numero_urna",
    "NM_CANDIDATO": "nome_civil",
    "NM_URNA_CANDIDATO": "nome_urna",
    "NM_SOCIAL_CANDIDATO": "nome_social",
    "CD_CARGO": "codigo_cargo",
    "DS_CARGO": "cargo",
    "SG_PARTIDO": "sigla_partido",
    "NM_PARTIDO": "nome_partido",
    "TP_AGREMIACAO": "tipo_agremiacao",
    "DS_COMPOSICAO_COLIGACAO": "composicao_coligacao",  # no lugar de SQ_COLIGACAO
    "SG_UF_NASCIMENTO": "uf_nascimento",
    "DT_NASCIMENTO": "data_nascimento",  # parseia e pode dropar o original
    "DS_GENERO": "genero",
    "DS_COR_RACA": "cor_raca",
    "DS_GRAU_INSTRUCAO": "escolaridade",
    "DS_ESTADO_CIVIL": "estado_civil",
    "DS_OCUPACAO": "ocupacao",
    "DS_SITUACAO_CANDIDATURA": "situacao_candidatura",
    "DS_SIT_TOT_TURNO": "resultado_turno",
}

COLUNAS_CAND = list(RENOMEAR_CAND.keys())

COLUNAS_COMP = [
    "SQ_CANDIDATO",
    "DS_NACIONALIDADE",
    "NM_MUNICIPIO_NASCIMENTO",
    "NR_IDADE_DATA_POSSE",
    "ST_QUILOMBOLA",
    "VR_DESPESA_MAX_CAMPANHA",
    "ST_DECLARAR_BENS",
    "DS_SITUACAO_JULGAMENTO",
    "ST_CANDIDATO_INSERIDO_URNA",
    "ST_SUBSTITUIDO",
]

RENOMEAR_BENS = {
    "SQ_CANDIDATO": "sq_candidato",
    "NR_ORDEM_BEM_CANDIDATO": "ordem_bem",
    "DS_TIPO_BEM_CANDIDATO": "tipo_bem",
    "DS_BEM_CANDIDATO": "descricao_bem",
    "VR_BEM_CANDIDATO": "valor_bem_texto",
}

COLUNAS_BENS = list(RENOMEAR_BENS.keys())

RENOMEAR_REDES = {
    "SQ_CANDIDATO": "sq_candidato",
    "NR_ORDEM_REDE_SOCIAL": "ordem_rede",
    "DS_URL": "url",
}

COLUNAS_REDES = list(RENOMEAR_REDES.keys())

RENOMEAR_VAGAS = {
    "CD_CARGO": "codigo_cargo",
    "QT_VAGA": "qtd_vagas_texto",
    "DT_POSSE": "data_posse_texto",
}

COLUNAS_VAGAS = list(RENOMEAR_VAGAS.keys())

def montar_dim_candidato(cand: pd.DataFrame, comp: pd.DataFrame) -> pd.DataFrame:
    """Junta candidatos + complementar em 1 linha por SQ_CANDIDATO."""
    esquerda = cand[COLUNAS_CAND].copy()
    direita = comp[COLUNAS_COMP].copy()

    tabela = pd.merge(
        esquerda,
        direita,
        on="SQ_CANDIDATO",
        how="inner",
        validate="one_to_one",
    )

    tabela["data_de_nascimento"] = parse_data_br(tabela["DT_NASCIMENTO"])
    tabela["idade_data_de_posse"] = parse_real_ponto(tabela["NR_IDADE_DATA_POSSE"])
    tabela["faixa"] = tabela["idade_data_de_posse"].map(faixa_etaria)
    tabela["valor_de_despesa_max"] = parse_real_ponto(tabela["VR_DESPESA_MAX_CAMPANHA"])

    tabela = tabela.drop(
        columns=["DT_NASCIMENTO", "NR_IDADE_DATA_POSSE", "VR_DESPESA_MAX_CAMPANHA"]
    )

    tabela = tabela.rename(columns=RENOMEAR_CAND)
    return tabela.reset_index(drop=True)

def montar_fato_bens(bens: pd.DataFrame) -> pd.DataFrame:
    """1 linha por bem declarado. Vários bens podem ter o mesmo que sq_candidato."""
    tabela = bens[COLUNAS_BENS].copy()
    tabela = tabela.rename(columns=RENOMEAR_BENS)

    tabela["valor_bem"] = parse_real_br(tabela["valor_bem_texto"])
    tabela = tabela.drop(columns=["valor_bem_texto"])

    tabela["ordem_bem"] = parse_real_ponto(tabela["ordem_bem"])
    return tabela.reset_index(drop=True)

def montar_fato_redes(redes: pd.DataFrame) -> pd.DataFrame:
    """1 linha por URL. Várias URLs podem ter o mesmo sq_candidato."""
    tabela = redes[COLUNAS_REDES].copy()
    tabela = tabela.rename(columns=RENOMEAR_REDES)

    tabela["plataforma"] = tabela["url"].map(classificar_plataforma)
    tabela["ordem_rede"] = parse_real_ponto(tabela["ordem_rede"])
    return tabela.reset_index(drop=True)

def montar_dim_vagas(vagas: pd.DataFrame) -> pd.DataFrame:
    """1 linha por cargo. QT_VAGA vira número; posse vira data."""
    tabela = vagas[COLUNAS_VAGAS].copy()
    tabela = tabela.rename(columns=RENOMEAR_VAGAS)

    tabela["qtd_vagas"] = parse_real_ponto(tabela["qtd_vagas_texto"])
    tabela["data_posse"] = parse_data_br(tabela["data_posse_texto"])
    tabela = tabela.drop(columns=["qtd_vagas_texto", "data_posse_texto"])
    return tabela.reset_index(drop=True)