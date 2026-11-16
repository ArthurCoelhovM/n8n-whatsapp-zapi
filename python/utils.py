import re

PADRAO_TELEFONE = re.compile(r"^55\d{10,11}$")
TAMANHO_MAXIMO_NOME = 40


def normalizar_telefone(telefone):
    if telefone is None:
        return None
    digitos = re.sub(r"\D", "", str(telefone))
    if not PADRAO_TELEFONE.match(digitos):
        return None
    return digitos


def mascarar_telefone(telefone):
    digitos = re.sub(r"\D", "", str(telefone or ""))
    if len(digitos) < 8:
        return "*" * len(digitos)
    return digitos[:4] + "*" * (len(digitos) - 8) + digitos[-4:]


def sanitizar_nome(nome):
    if not nome:
        return None
    limpo = re.sub(r"[^A-Za-zÀ-ÖØ-öø-ÿ' -]", "", str(nome))
    limpo = re.sub(r"\s+", " ", limpo).strip(" -'")
    limpo = limpo[:TAMANHO_MAXIMO_NOME].strip()
    if not limpo:
        return None
    return " ".join(parte.capitalize() for parte in limpo.split(" "))


def montar_mensagem(nome, template):
    if nome:
        return template.replace("{nome}", nome)
    return re.sub(r",?\s*\{nome\}", "", template)
