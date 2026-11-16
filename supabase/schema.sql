create table if not exists contatos (
  id bigint generated always as identity primary key,
  nome text not null,
  telefone text not null check (telefone ~ '^55[0-9]{10,11}$'),
  ativo boolean not null default true,
  criado_em timestamptz not null default now()
);

create table if not exists envios (
  id bigint generated always as identity primary key,
  contato_id bigint references contatos (id),
  telefone text not null,
  origem text not null check (origem in ('n8n-webhook', 'n8n-lote', 'python')),
  status text not null check (status in ('enviado', 'erro')),
  message_id text,
  criado_em timestamptz not null default now()
);

create table if not exists log_erros (
  id bigint generated always as identity primary key,
  origem text not null,
  etapa text,
  mensagem text not null,
  detalhes jsonb,
  criado_em timestamptz not null default now()
);

alter table contatos enable row level security;
alter table envios enable row level security;
alter table log_erros enable row level security;
