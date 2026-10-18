-- ============================================================
-- Courier & Logistics Tracking System — Phase 1 schema
-- Run this in the Supabase SQL Editor
-- ============================================================

create extension if not exists pgcrypto;

-- ------------------------------------------------------------
-- profiles: one table for all four roles.
-- Admin/Dispatcher -> email + auth_user_id (Supabase Auth)
-- Rider/Customer   -> phone + pin_hash (handled entirely by our FastAPI backend)
-- ------------------------------------------------------------
create table if not exists profiles (
  id uuid primary key default gen_random_uuid(),
  role text not null check (role in ('Admin', 'Dispatcher', 'Rider', 'Customer')),
  full_name text not null default '',

  -- Admin / Dispatcher login (Supabase Auth)
  email text unique,
  auth_user_id uuid unique,

  -- Customer / Rider login (custom PIN auth, handled in app/security.py)
  phone text unique,
  pin_hash text,

  created_at timestamptz not null default now(),

  -- a staff profile must have an email; a customer/rider profile must have a phone
  constraint profiles_identity_check check (
    (role in ('Admin', 'Dispatcher') and email is not null)
    or
    (role in ('Rider', 'Customer') and phone is not null)
  )
);

create index if not exists idx_profiles_phone on profiles (phone);
create index if not exists idx_profiles_email on profiles (email);

-- ------------------------------------------------------------
-- packages: Phase 1 core fields only
-- ------------------------------------------------------------
create table if not exists packages (
  id uuid primary key default gen_random_uuid(),
  tracking_id text unique not null,

  sender_name text not null,
  receiver_name text not null,
  receiver_phone text not null,

  origin_hub text not null check (origin_hub in ('BWP', 'Multan', 'Lahore', 'Lodhran', 'RYK')),
  destination_hub text not null check (destination_hub in ('BWP', 'Multan', 'Lahore', 'Lodhran', 'RYK')),

  status text not null default 'Booked'
    check (status in ('Booked', 'In Transit', 'Reached Hub - Ready for Delivery', 'Delivered', 'Cancelled')),

  created_by uuid references profiles(id),
  created_at timestamptz not null default now()
);

create index if not exists idx_packages_receiver_phone on packages (receiver_phone);
create index if not exists idx_packages_tracking_id on packages (tracking_id);

-- ------------------------------------------------------------
-- Row Level Security
-- The FastAPI backend connects with the service_role key, which bypasses
-- RLS entirely — access control is enforced in the backend's own route
-- logic (session role + phone number), not at the database level.
-- RLS is still enabled here as a safety net in case a key is ever
-- misconfigured or a different (non-service-role) key is used later.
-- ------------------------------------------------------------
alter table profiles enable row level security;
alter table packages enable row level security;

-- No policies are created for the anon/authenticated roles on purpose:
-- this means the tables are fully locked down to anyone except the
-- service_role key. Add scoped policies later only if you introduce
-- direct browser-to-Supabase access (this Phase 1 design does not).

-- ------------------------------------------------------------
-- Example: manually linking an Admin/Dispatcher after creating
-- their login in Authentication -> Users:
--
-- insert into profiles (role, full_name, email, auth_user_id)
-- values ('Admin', 'Your Name', 'admin@example.com', '<paste auth user id here>');
-- ------------------------------------------------------------
