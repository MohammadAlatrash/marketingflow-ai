begin;

create extension if not exists vector with schema extensions;

create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  display_name text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.clients (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references auth.users(id) on delete cascade,
  name text not null check (char_length(name) between 1 and 200),
  brief jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (id, owner_id)
);

create table if not exists public.brand_documents (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references auth.users(id) on delete cascade,
  client_id uuid not null,
  file_name text not null,
  mime_type text not null,
  storage_path text not null,
  checksum_sha256 text not null check (char_length(checksum_sha256) = 64),
  extraction_status text not null default 'pending'
    check (extraction_status in ('pending', 'processing', 'ready', 'failed')),
  extracted_text text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (id, owner_id),
  unique (id, owner_id, client_id),
  unique (owner_id, client_id, checksum_sha256),
  foreign key (client_id, owner_id)
    references public.clients(id, owner_id) on delete cascade
);

create table if not exists public.brand_chunks (
  id bigint generated always as identity primary key,
  owner_id uuid not null references auth.users(id) on delete cascade,
  client_id uuid not null,
  document_id uuid not null,
  chunk_index integer not null check (chunk_index >= 0),
  content text not null,
  embedding extensions.vector(768),
  created_at timestamptz not null default now(),
  unique (document_id, chunk_index),
  foreign key (client_id, owner_id)
    references public.clients(id, owner_id) on delete cascade,
  foreign key (document_id, owner_id, client_id)
    references public.brand_documents(id, owner_id, client_id) on delete cascade
);

create table if not exists public.campaigns (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references auth.users(id) on delete cascade,
  client_id uuid not null,
  title text not null check (char_length(title) between 1 and 240),
  request text not null,
  route text check (route in ('knowledge_answer', 'content_only', 'strategy_only', 'full_campaign')),
  status text not null default 'draft'
    check (status in ('draft', 'running', 'completed', 'failed', 'archived')),
  current_stage text not null default 'created',
  progress smallint not null default 0 check (progress between 0 and 100),
  state jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (id, owner_id),
  unique (id, owner_id, client_id),
  foreign key (client_id, owner_id)
    references public.clients(id, owner_id) on delete cascade
);

create table if not exists public.content_items (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references auth.users(id) on delete cascade,
  client_id uuid not null,
  campaign_id uuid not null,
  platform text not null,
  format text not null,
  status text not null default 'generated'
    check (status in ('generated', 'approved', 'published', 'rejected')),
  content jsonb not null,
  normalized_hash text not null,
  embedding extensions.vector(768),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (id, owner_id),
  unique (id, owner_id, client_id),
  foreign key (client_id, owner_id)
    references public.clients(id, owner_id) on delete cascade,
  foreign key (campaign_id, owner_id, client_id)
    references public.campaigns(id, owner_id, client_id) on delete cascade
);

create table if not exists public.feedback (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references auth.users(id) on delete cascade,
  client_id uuid not null,
  campaign_id uuid,
  content_item_id uuid,
  feedback_text text not null,
  label text,
  rating smallint check (rating between 1 and 5),
  created_at timestamptz not null default now(),
  foreign key (client_id, owner_id)
    references public.clients(id, owner_id) on delete cascade,
  foreign key (campaign_id, owner_id, client_id)
    references public.campaigns(id, owner_id, client_id) on delete cascade,
  foreign key (content_item_id, owner_id, client_id)
    references public.content_items(id, owner_id, client_id) on delete cascade
);

create index if not exists clients_owner_idx on public.clients(owner_id);
create index if not exists brand_documents_owner_client_idx on public.brand_documents(owner_id, client_id);
create index if not exists brand_chunks_owner_client_idx on public.brand_chunks(owner_id, client_id);
create index if not exists campaigns_owner_client_updated_idx on public.campaigns(owner_id, client_id, updated_at desc);
create index if not exists content_items_owner_client_status_idx on public.content_items(owner_id, client_id, status);
create index if not exists feedback_owner_client_created_idx on public.feedback(owner_id, client_id, created_at desc);

alter table public.profiles enable row level security;
alter table public.clients enable row level security;
alter table public.brand_documents enable row level security;
alter table public.brand_chunks enable row level security;
alter table public.campaigns enable row level security;
alter table public.content_items enable row level security;
alter table public.feedback enable row level security;

grant select, insert, update, delete on public.profiles to authenticated;
grant select, insert, update, delete on public.clients to authenticated;
grant select, insert, update, delete on public.brand_documents to authenticated;
grant select, insert, update, delete on public.brand_chunks to authenticated;
grant select, insert, update, delete on public.campaigns to authenticated;
grant select, insert, update, delete on public.content_items to authenticated;
grant select, insert, update, delete on public.feedback to authenticated;
grant usage, select on all sequences in schema public to authenticated;

create policy "profiles_select_own" on public.profiles for select to authenticated
  using ((select auth.uid()) = id);
create policy "profiles_insert_own" on public.profiles for insert to authenticated
  with check ((select auth.uid()) = id);
create policy "profiles_update_own" on public.profiles for update to authenticated
  using ((select auth.uid()) = id) with check ((select auth.uid()) = id);
create policy "profiles_delete_own" on public.profiles for delete to authenticated
  using ((select auth.uid()) = id);

create policy "clients_select_own" on public.clients for select to authenticated using ((select auth.uid()) = owner_id);
create policy "clients_insert_own" on public.clients for insert to authenticated with check ((select auth.uid()) = owner_id);
create policy "clients_update_own" on public.clients for update to authenticated using ((select auth.uid()) = owner_id) with check ((select auth.uid()) = owner_id);
create policy "clients_delete_own" on public.clients for delete to authenticated using ((select auth.uid()) = owner_id);

create policy "brand_documents_select_own" on public.brand_documents for select to authenticated using ((select auth.uid()) = owner_id);
create policy "brand_documents_insert_own" on public.brand_documents for insert to authenticated with check ((select auth.uid()) = owner_id);
create policy "brand_documents_update_own" on public.brand_documents for update to authenticated using ((select auth.uid()) = owner_id) with check ((select auth.uid()) = owner_id);
create policy "brand_documents_delete_own" on public.brand_documents for delete to authenticated using ((select auth.uid()) = owner_id);

create policy "brand_chunks_select_own" on public.brand_chunks for select to authenticated using ((select auth.uid()) = owner_id);
create policy "brand_chunks_insert_own" on public.brand_chunks for insert to authenticated with check ((select auth.uid()) = owner_id);
create policy "brand_chunks_update_own" on public.brand_chunks for update to authenticated using ((select auth.uid()) = owner_id) with check ((select auth.uid()) = owner_id);
create policy "brand_chunks_delete_own" on public.brand_chunks for delete to authenticated using ((select auth.uid()) = owner_id);

create policy "campaigns_select_own" on public.campaigns for select to authenticated using ((select auth.uid()) = owner_id);
create policy "campaigns_insert_own" on public.campaigns for insert to authenticated with check ((select auth.uid()) = owner_id);
create policy "campaigns_update_own" on public.campaigns for update to authenticated using ((select auth.uid()) = owner_id) with check ((select auth.uid()) = owner_id);
create policy "campaigns_delete_own" on public.campaigns for delete to authenticated using ((select auth.uid()) = owner_id);

create policy "content_items_select_own" on public.content_items for select to authenticated using ((select auth.uid()) = owner_id);
create policy "content_items_insert_own" on public.content_items for insert to authenticated with check ((select auth.uid()) = owner_id);
create policy "content_items_update_own" on public.content_items for update to authenticated using ((select auth.uid()) = owner_id) with check ((select auth.uid()) = owner_id);
create policy "content_items_delete_own" on public.content_items for delete to authenticated using ((select auth.uid()) = owner_id);

create policy "feedback_select_own" on public.feedback for select to authenticated using ((select auth.uid()) = owner_id);
create policy "feedback_insert_own" on public.feedback for insert to authenticated with check ((select auth.uid()) = owner_id);
create policy "feedback_update_own" on public.feedback for update to authenticated using ((select auth.uid()) = owner_id) with check ((select auth.uid()) = owner_id);
create policy "feedback_delete_own" on public.feedback for delete to authenticated using ((select auth.uid()) = owner_id);

insert into storage.buckets (id, name, public, file_size_limit)
values ('brand-assets', 'brand-assets', false, 20971520)
on conflict (id) do update set public = false, file_size_limit = excluded.file_size_limit;

create policy "brand_assets_select_own" on storage.objects for select to authenticated
  using (bucket_id = 'brand-assets' and owner_id = (select auth.uid()::text));
create policy "brand_assets_insert_own" on storage.objects for insert to authenticated
  with check (bucket_id = 'brand-assets' and (storage.foldername(name))[1] = (select auth.uid()::text));
create policy "brand_assets_update_own" on storage.objects for update to authenticated
  using (bucket_id = 'brand-assets' and owner_id = (select auth.uid()::text))
  with check (bucket_id = 'brand-assets' and (storage.foldername(name))[1] = (select auth.uid()::text));
create policy "brand_assets_delete_own" on storage.objects for delete to authenticated
  using (bucket_id = 'brand-assets' and owner_id = (select auth.uid()::text));

commit;
