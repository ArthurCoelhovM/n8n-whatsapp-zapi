from supabase import create_client


class Banco:
    def __init__(self, config):
        self.cliente = create_client(config.supabase_url, config.supabase_key)

    def buscar_contatos(self, limite):
        resposta = (
            self.cliente.table("contatos")
            .select("id, nome, telefone")
            .eq("ativo", True)
            .order("id")
            .limit(limite)
            .execute()
        )
        return resposta.data

    def registrar_envio(self, contato_id, telefone_mascarado, status, message_id=None):
        self.cliente.table("envios").insert({
            "contato_id": contato_id,
            "telefone": telefone_mascarado,
            "origem": "python",
            "status": status,
            "message_id": message_id,
        }).execute()

    def registrar_erro(self, etapa, mensagem, detalhes=None):
        self.cliente.table("log_erros").insert({
            "origem": "python",
            "etapa": etapa,
            "mensagem": mensagem,
            "detalhes": detalhes or {},
        }).execute()
