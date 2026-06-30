-- =============================================================
-- Tabela: contatos
-- Guarda a lista de destinatários das mensagens WhatsApp
-- =============================================================
CREATE TABLE contatos (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  nome             TEXT NOT NULL,
  phone            TEXT NOT NULL,                      -- formato: 5551999999999
  mensagem_personalizada TEXT,                         -- se NULL, usa mensagem padrão
  ativo            BOOLEAN NOT NULL DEFAULT true,      -- false = não envia pra esse contato
  notificado       BOOLEAN NOT NULL DEFAULT false,     -- false = ainda não foi notificado
  notificado_em    TIMESTAMPTZ,                        -- preenchido pelo n8n após envio
  criado_em        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================
-- Tabela: log_envios
-- Registra erros de envio para auditoria
-- =============================================================
CREATE TABLE log_envios (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  contato_id      UUID REFERENCES contatos(id),
  phone           TEXT NOT NULL,
  status          TEXT NOT NULL DEFAULT 'erro',        -- 'erro' por enquanto; expansível
  erro_detalhes   TEXT,
  tentativa_em    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================
-- Dados de exemplo para testar o fluxo
-- =============================================================
INSERT INTO contatos (nome, phone, mensagem_personalizada) VALUES
  ('Arthur',    '5551999990001', 'Olá, Arthur! Novidade especial pra você.'),
  ('Maria',     '5551999990002', NULL),
  ('João',      '5551999990003', 'João, seu acesso foi liberado!'),
  ('Fernanda',  '5551999990004', NULL);

-- =============================================================
-- Resetar notificações (útil durante testes)
-- Execute isso pra mandar de novo pra todos
-- =============================================================
-- UPDATE contatos SET notificado = false, notificado_em = NULL;
