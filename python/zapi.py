import requests

URL_BASE = "https://api.z-api.io/instances/{instancia}/token/{token}"


class ErroZapi(Exception):
    pass


def enviar_texto(config, telefone, mensagem):
    url = URL_BASE.format(instancia=config.zapi_instance_id, token=config.zapi_token) + "/send-text"
    cabecalhos = {
        "Client-Token": config.zapi_client_token,
        "Content-Type": "application/json",
    }
    try:
        resposta = requests.post(
            url,
            json={"phone": telefone, "message": mensagem},
            headers=cabecalhos,
            timeout=15,
        )
        resposta.raise_for_status()
    except requests.HTTPError as erro:
        raise ErroZapi(f"Z-API respondeu {erro.response.status_code}") from None
    except requests.RequestException as erro:
        raise ErroZapi(f"Falha de conexão com a Z-API: {type(erro).__name__}") from None

    dados = resposta.json()
    if "messageId" not in dados:
        raise ErroZapi("Resposta da Z-API sem messageId")
    return dados["messageId"]
