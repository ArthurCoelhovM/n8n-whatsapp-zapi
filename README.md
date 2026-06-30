# n8n + WhatsApp via Z-API

Dois fluxos de automação para envio de mensagens WhatsApp usando [n8n](https://n8n.io/) e [Z-API](https://www.z-api.io/), com contatos gerenciados no [Supabase](https://supabase.com/).

---

## Fluxos disponíveis

### 1. Webhook — disparo pontual
`flows/whatsapp-zapi-flow.json`

Expõe um endpoint HTTP. Qualquer sistema externo chama o endpoint e a mensagem é enviada imediatamente.

```
POST /webhook/send-whatsapp
  { "phone": "5551999999999", "message": "Olá!" }
```

### 2. Envio em lote — lista de contatos
`flows/whatsapp-lote-supabase.json`

Roda automaticamente de segunda a sexta às 9h. Busca no Supabase todos os contatos com `notificado = false` e `ativo = true`, envia a mensagem pra cada um com intervalo de 3 segundos, e marca como notificado ao final.

```
Schedule (9h, seg–sex)
  → Supabase: busca contatos pendentes
      → lista vazia → encerra
      → tem contatos → para cada um:
            aguarda 3s
            → Z-API: envia mensagem
                → sucesso → marca notificado = true
                → erro    → registra em log_envios
```

---

## Pré-requisitos

- Docker + Docker Compose
- Conta na [Z-API](https://app.z-api.io/) com instância conectada (WhatsApp escaneado)
- Projeto no [Supabase](https://supabase.com/) (gratuito)

---

## Setup

### 1. Variáveis de ambiente

```bash
cp .env.example .env
```

Edite `.env` com suas credenciais:

| Variável              | Onde encontrar                                        |
|-----------------------|-------------------------------------------------------|
| `ZAPI_INSTANCE_ID`    | Painel Z-API → sua instância → ID                     |
| `ZAPI_TOKEN`          | Painel Z-API → sua instância → Token                  |
| `ZAPI_CLIENT_TOKEN`   | Painel Z-API → Conta → Security → Client Token        |
| `SUPABASE_URL`        | Painel Supabase → Settings → API → Project URL        |
| `SUPABASE_ANON_KEY`   | Painel Supabase → Settings → API → anon public key    |

### 2. Banco de dados

No Supabase, abra o **SQL Editor** e execute o arquivo `docs/supabase-setup.sql`. Isso cria as tabelas `contatos` e `log_envios` e insere 4 contatos de exemplo.

### 3. Subir o n8n

```bash
docker compose up -d
```

Acesse `http://localhost:5678`.

### 4. Importar os fluxos

No n8n: **Workflows → Import from file**

Importe os dois arquivos da pasta `flows/`. Ative cada workflow com o toggle no canto superior direito.

---

## Uso

### Fluxo 1 — disparo manual

```bash
curl -X POST http://localhost:5678/webhook/send-whatsapp \
  -H "Content-Type: application/json" \
  -d '{"phone": "5551999999999", "message": "Olá!"}'
```

**Resposta 200:**
```json
{ "success": true, "phone": "5551999999999", "messageId": "...", "timestamp": "..." }
```

**Resposta 400** — campo faltando:
```json
{ "success": false, "error": "Os campos 'phone' e 'message' são obrigatórios." }
```

### Fluxo 2 — gerenciar contatos

Adicione contatos direto no Supabase:

```sql
INSERT INTO contatos (nome, phone, mensagem_personalizada)
VALUES ('Carlos', '5551988887777', 'Carlos, seu pedido foi aprovado!');
```

Se `mensagem_personalizada` for `NULL`, o fluxo usa uma mensagem padrão com o nome do contato.

Para reenviar pra todos:
```sql
UPDATE contatos SET notificado = false, notificado_em = NULL;
```

Para desativar um contato sem deletar:
```sql
UPDATE contatos SET ativo = false WHERE phone = '5551988887777';
```

---

## Estrutura do repositório

```
.
├── docker-compose.yml
├── .env.example
├── .gitignore
├── docs/
│   └── supabase-setup.sql        ← cria as tabelas e dados de exemplo
└── flows/
    ├── whatsapp-zapi-flow.json   ← Fluxo 1: webhook pontual
    └── whatsapp-lote-supabase.json ← Fluxo 2: envio em lote
```

---

## Formato do número de telefone

A Z-API exige: `DDI + DDD + número`, sem espaços ou caracteres especiais.

| País   | Formato          | Exemplo         |
|--------|------------------|-----------------|
| Brasil | `55` + DDD + num | `5551999999999` |

---

## Tecnologias

- [n8n](https://n8n.io/) — automação de fluxos
- [Z-API](https://www.z-api.io/) — gateway WhatsApp
- [Supabase](https://supabase.com/) — banco de dados PostgreSQL
- Docker Compose
