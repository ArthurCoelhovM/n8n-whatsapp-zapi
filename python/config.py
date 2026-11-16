import os
from dataclasses import dataclass

from dotenv import load_dotenv

OBRIGATORIAS = [
    "SUPABASE_URL",
    "SUPABASE_KEY",
    "ZAPI_INSTANCE_ID",
    "ZAPI_TOKEN",
    "ZAPI_CLIENT_TOKEN",
]

TEMPLATE_PADRAO = "Olá, {nome}! Tudo bem com você?"


class ConfigInvalida(Exception):
    pass


@dataclass
class Config:
    supabase_url: str
    supabase_key: str
    zapi_instance_id: str
    zapi_token: str
    zapi_client_token: str
    limite_contatos: int
    intervalo_segundos: float
    mensagem_template: str
    dry_run: bool


def _inteiro(nome, padrao):
    valor = os.getenv(nome, "").strip()
    if not valor:
        return padrao
    try:
        numero = int(valor)
    except ValueError:
        raise ConfigInvalida(f"{nome} precisa ser um número inteiro")
    if numero <= 0:
        raise ConfigInvalida(f"{nome} precisa ser maior que zero")
    return numero


def carregar_config():
    load_dotenv()

    faltando = [nome for nome in OBRIGATORIAS if not os.getenv(nome, "").strip()]
    if faltando:
        raise ConfigInvalida("Variáveis de ambiente faltando: " + ", ".join(faltando))

    return Config(
        supabase_url=os.environ["SUPABASE_URL"].strip(),
        supabase_key=os.environ["SUPABASE_KEY"].strip(),
        zapi_instance_id=os.environ["ZAPI_INSTANCE_ID"].strip(),
        zapi_token=os.environ["ZAPI_TOKEN"].strip(),
        zapi_client_token=os.environ["ZAPI_CLIENT_TOKEN"].strip(),
        limite_contatos=_inteiro("LIMITE_CONTATOS", 3),
        intervalo_segundos=_inteiro("INTERVALO_SEGUNDOS", 3),
        mensagem_template=os.getenv("MENSAGEM_TEMPLATE", "").strip() or TEMPLATE_PADRAO,
        dry_run=os.getenv("DRY_RUN", "false").strip().lower() in ("1", "true", "sim"),
    )
