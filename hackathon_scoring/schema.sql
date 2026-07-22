-- Supabase SQL Editor에서 전체를 한 번에 실행하세요.
-- 이 구조는 평가 문항 5개를 사용합니다.

create extension if not exists pgcrypto;

create table if not exists public.users (
    id uuid primary key default gen_random_uuid(),
    username text not null,
    user_type text not null
        check (user_type in ('team', 'judge')),
    team_name text,
    access_code_hash text not null,
    is_active boolean not null default true,
    created_at timestamptz not null default now(),

    constraint users_username_type_unique
        unique (username, user_type),

    constraint users_team_name_rule
        check (
            (user_type = 'team' and team_name is not null)
            or
            (user_type = 'judge' and team_name is null)
        )
);

create table if not exists public.evaluations (
    id uuid primary key default gen_random_uuid(),

    evaluator_id uuid not null
        references public.users(id)
        on update cascade
        on delete restrict,

    evaluator_name text not null,
    evaluator_type text not null
        check (evaluator_type in ('team', 'judge')),
    evaluator_team text,
    target_team text not null,

    question_1 smallint not null check (question_1 between 1 and 5),
    question_2 smallint not null check (question_2 between 1 and 5),
    question_3 smallint not null check (question_3 between 1 and 5),
    question_4 smallint not null check (question_4 between 1 and 5),
    question_5 smallint not null check (question_5 between 1 and 5),

    total_score smallint generated always as (
        question_1
        + question_2
        + question_3
        + question_4
        + question_5
    ) stored,

    submitted_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),

    constraint evaluations_evaluator_target_unique
        unique (evaluator_id, target_team),

    constraint evaluations_self_evaluation_check
        check (
            evaluator_type <> 'team'
            or evaluator_team is distinct from target_team
        )
);

create index if not exists evaluations_target_team_index
    on public.evaluations(target_team);

create index if not exists evaluations_evaluator_type_index
    on public.evaluations(evaluator_type);

create index if not exists evaluations_submitted_at_index
    on public.evaluations(submitted_at desc);

create or replace function public.set_updated_at()
returns trigger
language plpgsql
security invoker
set search_path = public
as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

drop trigger if exists evaluations_set_updated_at
    on public.evaluations;

create trigger evaluations_set_updated_at
before update on public.evaluations
for each row
execute function public.set_updated_at();

-- 브라우저의 anon/authenticated 키로 테이블을 직접 읽거나 쓰지 못하게 합니다.
-- Streamlit 서버에만 보관한 service_role 또는 secret 키로 접근합니다.
alter table public.users enable row level security;
alter table public.evaluations enable row level security;

revoke all on table public.users from anon, authenticated;
revoke all on table public.evaluations from anon, authenticated;

-- service_role/secret 키는 RLS를 우회하므로 절대로 브라우저 코드나
-- 공개 GitHub 저장소에 노출하면 안 됩니다.
