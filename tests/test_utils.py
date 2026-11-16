from utils import mascarar_telefone, montar_mensagem, normalizar_telefone, sanitizar_nome


def test_mascara_mantem_ddi_ddd_e_final():
    assert mascarar_telefone("5551987654321") == "5551*****4321"


def test_mascara_telefone_fixo():
    assert mascarar_telefone("555133334444") == "5551****4444"


def test_mascara_valor_curto_nao_vaza_digitos():
    assert mascarar_telefone("123") == "***"
    assert mascarar_telefone(None) == ""


def test_normaliza_telefone_com_formatacao():
    assert normalizar_telefone("+55 (51) 98765-4321") == "5551987654321"


def test_telefone_invalido():
    assert normalizar_telefone("51995334321") is None
    assert normalizar_telefone("55519876543219999") is None
    assert normalizar_telefone("") is None
    assert normalizar_telefone(None) is None


def test_nome_com_acentos_e_espacos():
    assert sanitizar_nome("  joão   da   silva ") == "João Da Silva"


def test_nome_remove_emoji_e_simbolos():
    assert sanitizar_nome("Maria 😀!!") == "Maria"


def test_nome_remove_html():
    assert sanitizar_nome("<script>alert(1)</script>Ana") == "Scriptalertscriptana"


def test_nome_mantem_hifen_e_apostrofo():
    assert sanitizar_nome("ana-luiza d'avila") == "Ana-luiza D'avila"


def test_nome_vazio_ou_so_simbolos():
    assert sanitizar_nome("") is None
    assert sanitizar_nome(None) is None
    assert sanitizar_nome("123 !!!") is None


def test_nome_cortado_em_40():
    assert len(sanitizar_nome("a" * 100)) == 40


def test_mensagem_com_nome():
    assert montar_mensagem("Ana", "Olá, {nome}! Tudo bem com você?") == "Olá, Ana! Tudo bem com você?"


def test_mensagem_sem_nome():
    assert montar_mensagem(None, "Olá, {nome}! Tudo bem com você?") == "Olá! Tudo bem com você?"
