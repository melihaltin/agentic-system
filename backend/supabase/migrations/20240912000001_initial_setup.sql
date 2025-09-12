-- Enable necessary extensions
create extension if not exists "uuid-ossp";
create extension if not exists "pgcrypto";

-- Create profiles table
create table if not exists public.profiles (
    id uuid references auth.users on delete cascade not null primary key,
    email text unique not null,
    username text unique not null,
    full_name text,
    bio text,
    avatar_url text,
    is_active boolean default true not null,
    is_superuser boolean default false not null,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null,
    
    constraint username_length check (char_length(username) >= 3 and char_length(username) <= 50),
    constraint username_format check (username ~ '^[a-zA-Z0-9_]+$')
);

-- Create updated_at trigger function
create or replace function public.handle_updated_at()
returns trigger as $$
begin
    new.updated_at = now();
    return new;
end;
$$ language plpgsql;

-- Create trigger for updated_at
drop trigger if exists handle_updated_at_profiles on public.profiles;
create trigger handle_updated_at_profiles
    before update on public.profiles
    for each row execute procedure public.handle_updated_at();

-- Create RLS (Row Level Security) policies
alter table public.profiles enable row level security;

-- Drop existing policies if they exist
drop policy if exists "Profiles are viewable by everyone" on public.profiles;
drop policy if exists "Users can insert their own profile" on public.profiles;
drop policy if exists "Users can update their own profile" on public.profiles;
drop policy if exists "Service role can manage all profiles" on public.profiles;

-- Policy: Users can view all active profiles (for public access)
create policy "Profiles are viewable by everyone" 
    on public.profiles for select 
    using (is_active = true);

-- Policy: Users can insert their own profile
create policy "Users can insert their own profile" 
    on public.profiles for insert 
    with check (auth.uid() = id);

-- Policy: Users can update their own profile
create policy "Users can update their own profile" 
    on public.profiles for update 
    using (auth.uid() = id);

-- Policy: Service role can do everything
create policy "Service role can manage all profiles" 
    on public.profiles for all 
    to service_role
    using (true);

-- Create indexes for better performance
create index if not exists profiles_username_idx on public.profiles(username);
create index if not exists profiles_email_idx on public.profiles(email);
create index if not exists profiles_is_active_idx on public.profiles(is_active);
create index if not exists profiles_created_at_idx on public.profiles(created_at);

-- Create function to handle user signup
create or replace function public.handle_new_user()
returns trigger as $$
begin
    insert into public.profiles (id, email, username, full_name)
    values (
        new.id,
        new.email,
        coalesce(new.raw_user_meta_data->>'username', split_part(new.email, '@', 1)),
        coalesce(new.raw_user_meta_data->>'full_name', new.email)
    );
    return new;
exception
    when others then
        -- Log error but don't fail the user creation
        raise warning 'Failed to create profile for user %: %', new.id, sqlerrm;
        return new;
end;
$$ language plpgsql security definer;

-- Create trigger for new user signup
drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
    after insert on auth.users
    for each row execute procedure public.handle_new_user();

-- Create function to search users
create or replace function public.search_profiles(search_term text, result_limit int default 20)
returns setof public.profiles as $$
begin
    return query
    select *
    from public.profiles
    where 
        is_active = true
        and (
            username ilike '%' || search_term || '%' 
            or full_name ilike '%' || search_term || '%'
            or email ilike '%' || search_term || '%'
        )
    order by 
        case 
            when username ilike search_term || '%' then 1
            when full_name ilike search_term || '%' then 2
            else 3
        end,
        username
    limit result_limit;
end;
$$ language plpgsql security definer;

-- Grant necessary permissions
grant usage on schema public to postgres, anon, authenticated, service_role;
grant all on table public.profiles to postgres, service_role;
grant select on table public.profiles to anon, authenticated;
grant insert, update on table public.profiles to authenticated;

-- Grant permissions for the search function
grant execute on function public.search_profiles(text, int) to anon, authenticated, service_role;

-- Create a view for public profile information
drop view if exists public.public_profiles;
create view public.public_profiles as
select 
    id,
    username,
    full_name,
    bio,
    avatar_url,
    created_at
from public.profiles
where is_active = true;

-- Grant select on the public view
grant select on public.public_profiles to anon, authenticated, service_role;
