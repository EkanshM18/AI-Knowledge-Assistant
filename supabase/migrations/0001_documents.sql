create table if not exists public.documents (
  id text primary key,
  filename text not null,
  storage_path text not null unique,
  file_type text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  upload_timestamp timestamptz not null default now(),
  ingestion_status text not null default 'queued',
  vector_collection text,
  vector_count integer not null default 0,
  chunk_count integer not null default 0,
  file_size bigint,
  mime_type text,
  error_message text,
  tags text[] not null default '{}'::text[],
  metadata jsonb not null default '{}'::jsonb
);

create index if not exists documents_ingestion_status_idx on public.documents (ingestion_status);
create index if not exists documents_created_at_idx on public.documents (created_at desc);
create index if not exists documents_vector_collection_idx on public.documents (vector_collection);
create index if not exists documents_tags_gin_idx on public.documents using gin (tags);
create index if not exists documents_metadata_gin_idx on public.documents using gin (metadata);

create or replace function public.set_documents_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists trigger_set_documents_updated_at on public.documents;
create trigger trigger_set_documents_updated_at
before update on public.documents
for each row
execute function public.set_documents_updated_at();
