import pandas as pd

import re

from typing import Optional

EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def parse_real_br(serie: pd.Series) -> pd.Series:
    """Converte texto no formato brasileiro (1.234,56) em número."""
    texto = serie.astype("string")
    sem_milhar = texto.str.replace(".", "", regex=False)
    com_ponto = sem_milhar.str.replace(",", ".", regex=False)

    numerico = pd.to_numeric(com_ponto, errors="coerce")
    if not isinstance(numerico, pd.Series):
        raise TypeError("esperado panda.Series")
    return numerico

def parse_real_ponto(serie: pd.Series) -> pd.Series:
    """Converte texto com ponto decimal (1270629.01) e número."""
    numerico = pd.to_numeric(serie, errors="coerce")
    if not isinstance(numerico, pd.Series):
        raise TypeError("esperado panda.Series")
    return numerico

def parse_data_br(serie: pd.Series) -> pd.Series:
    """Converte texto dd/mm/aaaa em data"""
    numerico = pd.to_datetime(serie, format="%d/%m/%Y", errors="coerce")
    if not isinstance(numerico, pd.Series):
        raise TypeError("esperado panda.Series")
    return numerico

def classificar_plataforma(url) -> str:
    """Devolve um nome curto de rede social a partir de uma URL (ou texto)"""
    if pd.isna(url):
        return "sem_url"

    texto = str(url).strip().lower()
    if texto == "":
        return "sem_url"

    if "instagram.com" in texto or texto.startswith("@"):
        return "instagram"
    if "facebook.com" in texto or "fb.com" in texto:
        return "facebook"
    if "tiktok.com" in texto:
        return "tiktok"
    if "youtube.com" in texto or "youtu.be" in texto:
        return "youtube"
    if "twitter.com" in texto or "x.com" in texto:
        return "x"
    if "threads.net" in texto:
        return "threads"
    if "kwai.com" in texto:
        return "kwai"
    if "linkedin.com" in texto:
        return "linkedin"
    if "whatsapp" in texto or "wa.me" in texto:
        return "whatsapp"
    if "telegram" in texto or "t.me" in texto:
        return "telegram"
    if EMAIL.match(texto):
        return "email"
    return "outro"

def faixa_etaria(idade) -> Optional[str]:
    """Agrupa uma idade em faixas de 10 anos"""
    if pd.isna(idade):
        return None

    anos = int(float(idade))
    if anos < 18:
        return "abaixo_de_18"
    if anos <= 29:
        return "18-29"
    if anos <= 39:
        return "30-39"
    if anos <= 49:
        return "40-49"
    if anos <= 59:
        return "50-59"
    if anos <= 69:
        return "60-69"
    return "70+"