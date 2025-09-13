-- First, create services table if it doesn't exist
create table if not exists public.services (
    name text primary key,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Insert default services
insert into public.services (name) values 
    ('restaurant'), 
    ('car_rental'), 
    ('shopify'),
    ('ecommerce'),
    ('retail'),
    ('consulting'),
    ('other')
on conflict (name) do nothing;

-- Create businesses table for business authentication
create table if not exists public.businesses (
    id uuid default gen_random_uuid() primary key,
    email text unique not null,
    business_type text not null references public.services(name) on update cascade on delete restrict,
    business_name text not null,
    business_website text,
    business_phone_number text,
    auth_user_id uuid references auth.users on delete cascade not null unique,
    is_active boolean default true not null,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null,
    
    constraint business_name_length check (char_length(business_name) >= 1 and char_length(business_name) <= 100),
    constraint business_email_format check (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Create trigger for updated_at on businesses
drop trigger if exists handle_updated_at_businesses on public.businesses;
create trigger handle_updated_at_businesses
    before update on public.businesses
    for each row execute procedure public.handle_updated_at();

-- Create RLS (Row Level Security) policies for businesses
alter table public.businesses enable row level security;

-- Drop existing policies if they exist
drop policy if exists "Businesses are viewable by authenticated users" on public.businesses;
drop policy if exists "Business owners can view their own business" on public.businesses;
drop policy if exists "Business owners can update their own business" on public.businesses;
drop policy if exists "Service role can manage all businesses" on public.businesses;

-- Policy: Authenticated users can view active businesses (for public access)
create policy "Businesses are viewable by authenticated users" 
    on public.businesses for select 
    to authenticated
    using (is_active = true);

-- Policy: Business owners can view their own business
create policy "Business owners can view their own business" 
    on public.businesses for select 
    using (auth.uid() = auth_user_id);

-- Policy: Business owners can update their own business
create policy "Business owners can update their own business" 
    on public.businesses for update 
    using (auth.uid() = auth_user_id);

-- Policy: Service role can do everything
create policy "Service role can manage all businesses" 
    on public.businesses for all 
    to service_role
    using (true);

-- Create indexes for better performance
create index if not exists businesses_email_idx on public.businesses(email);
create index if not exists businesses_auth_user_id_idx on public.businesses(auth_user_id);
create index if not exists businesses_business_type_idx on public.businesses(business_type);
create index if not exists businesses_is_active_idx on public.businesses(is_active);
create index if not exists businesses_created_at_idx on public.businesses(created_at);

-- Create function to handle business signup
create or replace function public.handle_new_business()
returns trigger as $$
begin
    -- This function can be used if needed for additional business logic
    -- Currently, businesses are created manually via API
    return new;
end;
$$ language plpgsql security definer;