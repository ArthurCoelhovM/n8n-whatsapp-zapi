import requests

URL_BASE = "https://api.omni.z-api.io/v1"


class ErroOmni(Exception):
    pass


def enviar_texto(config, telefone, mensagem):
    url = f"{URL_BASE}/channels/{config.omni_channel_id}/messages"
    cabecalhos = {
        "Authorization": f"Bearer {config.omni_secret_key}",
        "Content-Type": "application/json",
    }
    corpo = {
        "recipient": {"identifier": telefone},
        "content": {"type": "TEXT", "body": {"message": mensagem}},
    }
    try:
        resposta = requests.post(url, json=corpo, headers=cabecalhos, timeout=15)
        resposta.raise_for_status()
    except requests.HTTPError as erro:
        raise ErroOmni(f"Z-API Omni respondeu {erro.response.status_code}") from None
    except requests.RequestException as erro:
        raise ErroOmni(f"Falha de conexão com a Z-API Omni: {type(erro).__name__}") from None

    dados = resposta.json()
    if "messageId" not in dados:
        raise ErroOmni("Resposta da Z-API Omni sem messageId")
    return dados["messageId"]
