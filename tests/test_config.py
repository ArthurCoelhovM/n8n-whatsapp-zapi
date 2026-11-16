import pytest

import config
from config import ConfigInvalida, carregar_config

VALIDAS = {
    "SUPABASE_URL": "https://exemplo.supabase.co",
    "SUPABASE_KEY": "chave-teste",
    "ZAPI_INSTANCE_ID": "instancia-teste",
    "ZAPI_TOKEN": "token-teste",
    "ZAPI_CLIENT_TOKEN": "client-teste",
}


@pytest.fixture(autouse=True)
def ambiente_limpo(monkeypatch):
    monkeypatch.setattr(config, "load_dotenv", lambda: None)
    for nome in list(VALIDAS) + ["LIMITE_CONTATOS", "INTERVALO_SEGUNDOS", "MENSAGEM_TEMPLATE", "DRY_RUN"]:
        monkeypatch.delenv(nome, raising=False)


def definir(monkeypatch, **valores):
    for nome, valor in valores.items():
        monkeypatch.setenv(nome, valor)


def test_config_completa_usa_padroes(monkeypatch):
    definir(monkeypatch, **VALIDAS)
    cfg = carregar_config()
    assert cfg.limite_contatos == 3
    assert cfg.intervalo_segundos == 3
    assert cfg.dry_run is False
    assert "{nome}" in cfg.mensagem_template


def test_variavel_faltando_lista_os_nomes_sem_valores(monkeypatch):
    definir(monkeypatch, SUPABASE_URL="https://exemplo.supabase.co", SUPABASE_KEY="segredo-123")
    with pytest.raises(ConfigInvalida) as erro:
        carregar_config()
    texto = str(erro.value)
    assert "ZAPI_INSTANCE_ID" in texto
    assert "ZAPI_CLIENT_TOKEN" in texto
    assert "SUPABASE_URL" not in texto
    assert "segredo-123" not in texto


def test_variavel_so_com_espacos_conta_como_faltando(monkeypatch):
    definir(monkeypatch, **{**VALIDAS, "ZAPI_TOKEN": "   "})
    with pytest.raises(ConfigInvalida, match="ZAPI_TOKEN"):
        carregar_config()


def test_limite_invalido(monkeypatch):
    definir(monkeypatch, **VALIDAS, LIMITE_CONTATOS="abc")
    with pytest.raises(ConfigInvalida, match="LIMITE_CONTATOS"):
        carregar_config()


def test_dry_run_e_template(monkeypatch):
    definir(monkeypatch, **VALIDAS, DRY_RUN="true", MENSAGEM_TEMPLATE="Oi {nome}")
    cfg = carregar_config()
    assert cfg.dry_run is True
    assert cfg.mensagem_template == "Oi {nome}"
