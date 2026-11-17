import pytest
import requests

import omni
from config import Config
from omni import ErroOmni, enviar_texto


class RespostaFalsa:
    def __init__(self, status, dados):
        self.status_code = status
        self.dados = dados

    def raise_for_status(self):
        if self.status_code >= 400:
            erro = requests.HTTPError()
            erro.response = self
            raise erro

    def json(self):
        return self.dados


def criar_config():
    return Config("url", "chave", "segredo-123", "canal-abc", 3, 0, "Olá, {nome}!", False)


def test_monta_chamada_do_omni(monkeypatch):
    chamada = {}

    def post_falso(url, json, headers, timeout):
        chamada.update(url=url, json=json, headers=headers)
        return RespostaFalsa(200, {"messageId": "ABC123"})

    monkeypatch.setattr(omni.requests, "post", post_falso)
    assert enviar_texto(criar_config(), "5551987654321", "Oi") == "ABC123"
    assert chamada["url"] == "https://api.omni.z-api.io/v1/channels/canal-abc/messages"
    assert chamada["headers"]["Authorization"] == "Bearer segredo-123"
    assert chamada["json"] == {
        "recipient": {"identifier": "5551987654321"},
        "content": {"type": "TEXT", "body": {"message": "Oi"}},
    }


def test_erro_http_nao_vaza_chave(monkeypatch):
    monkeypatch.setattr(omni.requests, "post", lambda *a, **k: RespostaFalsa(401, {}))
    with pytest.raises(ErroOmni) as erro:
        enviar_texto(criar_config(), "5551987654321", "Oi")
    assert "401" in str(erro.value)
    assert "segredo-123" not in str(erro.value)
