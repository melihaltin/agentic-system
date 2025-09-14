-- Create company_profiles table
CREATE TABLE IF NOT EXISTS public.company_profiles (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    company_name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(50),
    business_category VARCHAR(100),
    platform VARCHAR(100),
    api_key TEXT,
    api_secret TEXT,
    additional_config JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add RLS (Row Level Security) policies
ALTER TABLE public.company_profiles ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view their own company profile
CREATE POLICY "Users can view own company profile" ON public.company_profiles
    FOR SELECT USING (auth.uid() = user_id);

-- Policy: Users can insert their own company profile
CREATE POLICY "Users can insert own company profile" ON public.company_profiles
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Policy: Users can update their own company profile
CREATE POLICY "Users can update own company profile" ON public.company_profiles
    FOR UPDATE USING (auth.uid() = user_id);

-- Policy: Users can delete their own company profile
CREATE POLICY "Users can delete own company profile" ON public.company_profiles
    FOR DELETE USING (auth.uid() = user_id);

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER company_profiles_updated_at
    BEFORE UPDATE ON public.company_profiles
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON public.company_profiles TO authenticated;
