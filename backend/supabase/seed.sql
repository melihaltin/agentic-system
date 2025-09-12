-- Seed data for local development

-- Insert some test users (they will need to be created via Supabase Auth first)
-- This is just example data structure

-- Example profiles that could be inserted after user creation
INSERT INTO public.profiles (id, email, username, full_name, bio, is_active, is_superuser) VALUES
    ('550e8400-e29b-41d4-a716-446655440000', 'admin@teamai.local', 'admin', 'System Administrator', 'Local development admin user', true, true),
    ('550e8400-e29b-41d4-a716-446655440001', 'user1@teamai.local', 'testuser1', 'Test User One', 'First test user for development', true, false),
    ('550e8400-e29b-41d4-a716-446655440002', 'user2@teamai.local', 'testuser2', 'Test User Two', 'Second test user for development', true, false)
ON CONFLICT (id) DO NOTHING;

-- Note: In real usage, these users should be created through Supabase Auth
-- The trigger will automatically create profiles when users sign up
