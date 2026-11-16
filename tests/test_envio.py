from config import Config
import main
from zapi import ErroZapi


class BancoFalso:
    def __init__(self):
        self.envios = []
        self.erros = []

    def registrar_envio(self, contato_id, telefone, status, message_id=None):
        self.envios.append((contato_id, telefone, status, message_id))

    def registrar_erro(self, etapa, mensagem, detalhes=None):
        self.erros.append((etapa, mensagem))


def criar_config(dry_run=False):
    return Config("url", "chave", "inst", "tok", "client", 3, 0, "Olá, {nome}!", dry_run)


def test_envio_com_sucesso_grava_telefone_mascarado(monkeypatch):
    monkeypatch.setattr(main, "enviar_texto", lambda cfg, tel, msg: "id-123")
    banco = BancoFalso()
    ok = main.processar_contato(banco, criar_config(), {"id": 1, "nome": "ana", "telefone": "5551987654321"})
    assert ok
    assert banco.envios == [(1, "5551*****4321", "enviado", "id-123")]


def test_erro_da_zapi_nao_interrompe_e_vai_para_log(monkeypatch):
    def falhar(cfg, tel, msg):
        raise ErroZapi("Z-API respondeu 401")

    monkeypatch.setattr(main, "enviar_texto", falhar)
    banco = BancoFalso()
    ok = main.processar_contato(banco, criar_config(), {"id": 2, "nome": "Bruno", "telefone": "5551987654321"})
    assert not ok
    assert banco.envios[0][2] == "erro"
    assert banco.erros == [("envio", "Z-API respondeu 401")]


def test_dry_run_nao_envia(monkeypatch, caplog):
    def nao_chamar(*args):
        raise AssertionError("não deveria enviar")

    monkeypatch.setattr(main, "enviar_texto", nao_chamar)
    banco = BancoFalso()
    caplog.set_level("INFO")
    ok = main.processar_contato(banco, criar_config(dry_run=True), {"id": 3, "nome": "Carla", "telefone": "5551987654321"})
    assert ok
    assert banco.envios == []
    assert "5551987654321" not in caplog.text
    assert "5551*****4321" in caplog.text


def test_telefone_invalido_registra_erro():
    banco = BancoFalso()
    ok = main.processar_contato(banco, criar_config(), {"id": 4, "nome": "Davi", "telefone": "123"})
    assert not ok
    assert banco.erros[0][0] == "validacao"
