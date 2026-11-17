import logging
import sys
import time

from banco import Banco
from config import ConfigInvalida, carregar_config
from utils import mascarar_telefone, montar_mensagem, normalizar_telefone, sanitizar_nome
from omni import ErroOmni, enviar_texto

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("envio")


def registrar_erro_seguro(banco, etapa, mensagem, detalhes):
    try:
        banco.registrar_erro(etapa, mensagem, detalhes)
    except Exception as erro:
        log.error("Não foi possível gravar em log_erros: %s", type(erro).__name__)


def processar_contato(banco, config, contato):
    telefone = normalizar_telefone(contato.get("telefone"))
    if not telefone:
        mascarado = mascarar_telefone(contato.get("telefone"))
        log.warning("Contato %s com telefone inválido (%s), pulando", contato.get("id"), mascarado)
        registrar_erro_seguro(banco, "validacao", "Telefone inválido", {"contato_id": contato.get("id")})
        return False

    mascarado = mascarar_telefone(telefone)
    nome = sanitizar_nome(contato.get("nome"))
    mensagem = montar_mensagem(nome, config.mensagem_template)

    if config.dry_run:
        log.info("[DRY_RUN] Mensagem para %s: %s", mascarado, mensagem)
        return True

    try:
        message_id = enviar_texto(config, telefone, mensagem)
    except ErroOmni as erro:
        log.error("Falha ao enviar para %s: %s", mascarado, erro)
        banco.registrar_envio(contato.get("id"), mascarado, "erro")
        registrar_erro_seguro(banco, "envio", str(erro), {"contato_id": contato.get("id")})
        return False

    banco.registrar_envio(contato.get("id"), mascarado, "enviado", message_id)
    log.info("Mensagem enviada para %s", mascarado)
    return True


def main():
    try:
        config = carregar_config()
    except ConfigInvalida as erro:
        log.error(str(erro))
        return 1

    banco = Banco(config)
    try:
        contatos = banco.buscar_contatos(config.limite_contatos)
    except Exception as erro:
        log.error("Erro ao buscar contatos no Supabase: %s", type(erro).__name__)
        return 1

    if not contatos:
        log.info("Nenhum contato ativo encontrado")
        return 0

    log.info("%d contato(s) para processar", len(contatos))
    enviados = 0
    erros = 0
    for posicao, contato in enumerate(contatos):
        if processar_contato(banco, config, contato):
            enviados += 1
        else:
            erros += 1
        if posicao < len(contatos) - 1 and not config.dry_run:
            time.sleep(config.intervalo_segundos)

    log.info("%d enviados, %d erros", enviados, erros)
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
