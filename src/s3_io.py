import os
import tempfile
from pathlib import Path

import boto3
from dotenv import load_dotenv

load_dotenv()

def _bucket() -> str:
    nome = os.getenv("S3_BUCKET")
    if not nome:
        raise ValueError("Defina S3_BUCKET no .env.")
    return nome

def cliente_s3():
    """Cliente s3 usando o perfil do .env"""
    perfil = os.getenv("AWS_PROFILE")
    if not perfil:
        raise ValueError("Defina AWS_PROFILE no .env.")
    regiao = os.getenv("AWS_REGION", "us-east-1")
    if not regiao:
        raise ValueError("Defina AWS_REGION no .env.")
    session = boto3.Session(profile_name=perfil, region_name=regiao)
    return session.client("s3")

def baixar_csv(chave: str) -> Path:
    """Baixa s3://bucket/chave para um CSV temprário e devolve o Path"""
    fd, caminho = tempfile.mkstemp(suffix=".csv")
    os.close(fd)
    destino = Path(caminho)
    cliente_s3().download_file(_bucket(), chave, str(destino))
    return destino

def enviar_csv(origem: Path, chave: str) -> None:
    """Sobe um arquivo local para s3://bucket/chave."""
    cliente_s3().upload_file(str(origem), _bucket(), chave)