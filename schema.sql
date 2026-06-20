-- À copier-coller dans Supabase : Dashboard > SQL Editor > New query > Run
-- Crée les deux tables du MVP : categorie et transaction.
-- (Le compte n'est pas inclus ici pour rester simple en v1 - un seul "compte implicite".
--  Tu pourras ajouter une table compte plus tard sans casser l'existant.)

create table if not exists categorie (
    id uuid primary key default gen_random_uuid(),
    nom text not null,
    icone text,
    type text not null check (type in ('depense', 'revenu'))
);

create table if not exists transaction (
    id uuid primary key default gen_random_uuid(),
    categorie_id uuid references categorie(id) on delete set null,
    montant numeric(12, 2) not null check (montant > 0),
    type text not null check (type in ('depense', 'revenu')),
    date date not null default current_date,
    note text,
    cree_le timestamptz not null default now()
);

-- Index pour accélérer les requêtes filtrées par date (utilisées dans les stats)
create index if not exists idx_transaction_date on transaction(date);

-- IMPORTANT : Row Level Security (RLS)
-- RLS activé : la base refuse tout accès tant qu'une policy ne l'autorise pas
-- explicitement, même si quelqu'un obtient ton URL + clé anon. C'est la base
-- elle-même qui se protège, indépendamment du mot de passe de l'app.
--
-- Comme tu es seul utilisateur (pas de système de comptes), les policies
-- ci-dessous autorisent simplement tout, pour la clé "anon" que ton app utilise.
-- Ça peut sembler équivalent à "RLS désactivé", mais ce n'est pas le cas :
-- RLS activé sans aucune policy = accès bloqué par défaut (sécurisé par défaut).
-- RLS désactivé = accès ouvert par défaut, point de départ moins sûr si tu
-- oublies une étape plus tard (ajout d'une table, etc).

alter table categorie enable row level security;
alter table transaction enable row level security;

create policy "Lecture libre categorie" on categorie
    for select using (true);
create policy "Ecriture libre categorie" on categorie
    for insert with check (true);
create policy "Modification libre categorie" on categorie
    for update using (true);
create policy "Suppression libre categorie" on categorie
    for delete using (true);

create policy "Lecture libre transaction" on transaction
    for select using (true);
create policy "Ecriture libre transaction" on transaction
    for insert with check (true);
create policy "Modification libre transaction" on transaction
    for update using (true);
create policy "Suppression libre transaction" on transaction
    for delete using (true);
