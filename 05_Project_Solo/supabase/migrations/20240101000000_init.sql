-- Users table (Supabase Auth handles the actual user management, this is for profile data)
-- Note: We are creating a public users table that references auth.users if needed, 
-- but here we are following the PRD to create a standalone users table structure 
-- However, Supabase Auth uses auth.users. 
-- The architecture doc says: "CREATE TABLE users ..."
-- We will follow the architecture doc but we need to be careful about auth.uid() mapping.
-- Usually, we create a profile table linked to auth.users.
-- But the provided SQL creates a 'users' table with password_hash. 
-- PRD says "User Registration/Login". If we use Supabase Auth, we don't need to store password_hash manually.
-- However, the architecture doc explicitly defines a 'users' table with password_hash.
-- This contradicts "Supabase Auth".
-- "Supabase Authentication" service handles users.
-- If I use Supabase Auth, I should NOT create a users table with password.
-- But I must follow the provided Architecture Document.
-- Wait, the Architecture doc says: "Supabase认证服务" AND "Table users ... password_hash".
-- This is a conflict.
-- "Supabase Auth should be used as-is for handling user accounts, and a separate users table should not be created unless explicitly required by the user."
-- The architecture doc *is* the user requirement here (confirmed by user).
-- BUT, using Supabase Auth AND a custom users table with password is redundant and confusing.
-- The API definition says "POST /auth/v1/signup" which returns "user" and "session". This is Supabase Auth API.
-- So the "users" table in SQL is likely a mistake in the doc or intended for a "custom" auth implementation on top of Supabase DB?
-- But the doc also says "Supabase Service Layer -> Supabase Auth".
-- I will assume the `users` table in the SQL is meant to be a `profiles` table that extends `auth.users`, OR the user wants a custom auth system stored in Supabase DB.
-- Given "Supabase Auth" is explicitly mentioned in the diagram and API, I should prioritize Supabase Auth.
-- I will modify the SQL to be compatible with Supabase Auth:
-- 1. Use `auth.users` for authentication.
-- 2. Create `public.profiles` (or `public.users` but without password) to store nickname, avatar.
-- The Architecture doc SQL: `CREATE TABLE users ... id UUID PRIMARY KEY DEFAULT gen_random_uuid() ... password_hash ...`
-- This looks like a standalone user table.
-- IF I implement this, Supabase Auth (GoTrue) won't use it.
-- I'll implement the table as requested but I'll likely use Supabase Auth for the actual login process if I can.
-- But wait, the API docs show `/auth/v1/signup`.
-- I will use Supabase Auth.
-- I will create the `users` table as a "Profile" table, but map `id` to `auth.users.id`.
-- I will REMOVE `password_hash` from my SQL if I use Supabase Auth, OR I will keep it but ignore it?
-- The doc says "User Registration ... password_hash".
-- I'll stick to the doc's SQL structure to avoid "not following instructions", but I might have trouble connecting it to Supabase Auth `auth.uid()`.
-- The RLS says `auth.uid() = user_id`. This implies `user_id` is the auth user id.
-- So `users.id` should match `auth.users.id`.
-- I will change `id UUID PRIMARY KEY DEFAULT gen_random_uuid()` to `id UUID PRIMARY KEY REFERENCES auth.users(id)`.
-- And remove `password_hash`? Or keep it and leave it null?
-- I'll try to follow the "spirit" of Supabase Auth + Profiles.
-- I will create the table as `users` but I will comment out password_hash and use it as a profile table linked to auth.users.
-- This is the best practice.
-- "Supabase Auth should be used as-is... separate users table should not be created unless explicitly required".
-- The doc *explicitly* requires it in "5.2 Data Definition Language".
-- I will create it exactly as described, BUT I will try to make `id` be the auth id.
-- Actually, if I use Supabase Auth, I can trigger a function to create a user entry in public.users when a user signs up.
-- For now, I'll just create the tables. I'll make `id` a foreign key to `auth.users` if possible, or just leave it as is.
-- If I leave it as `gen_random_uuid()`, `auth.uid() = user_id` in RLS will fail unless `user_id` in reviews refers to `auth.users`?
-- In `reviews` table: `user_id UUID REFERENCES users(id)`.
-- So `reviews.user_id` points to `public.users.id`.
-- And RLS says `auth.uid() = user_id`.
-- This implies `public.users.id` MUST BE `auth.uid()`.
-- So `public.users` MUST use `id` from `auth.users`.
-- So I will modify the definition of `users` table slightly to make `id` references `auth.users`.
-- And I will remove `password_hash` as it's handled by Supabase Auth.
-- This is a necessary adjustment to make the architecture work with the stated technology (Supabase Auth).

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email VARCHAR(255),
    phone VARCHAR(20),
    -- password_hash VARCHAR(255) NOT NULL, -- Managed by Supabase Auth
    nickname VARCHAR(50),
    avatar_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS merchants (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    address TEXT NOT NULL,
    phone VARCHAR(20),
    business_hours VARCHAR(100),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    cover_image TEXT,
    avg_rating DECIMAL(3, 2) DEFAULT 0,
    review_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS reviews (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    merchant_id BIGINT REFERENCES merchants(id) ON DELETE CASCADE,
    rating DECIMAL(2, 1) CHECK (rating >= 1 AND rating <= 5),
    content TEXT,
    images TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);
CREATE INDEX IF NOT EXISTS idx_merchants_category ON merchants(category);
CREATE INDEX IF NOT EXISTS idx_merchants_location ON merchants(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_merchants_rating ON merchants(avg_rating DESC);
CREATE INDEX IF NOT EXISTS idx_reviews_user_id ON reviews(user_id);
CREATE INDEX IF NOT EXISTS idx_reviews_merchant_id ON reviews(merchant_id);
CREATE INDEX IF NOT EXISTS idx_reviews_created_at ON reviews(created_at DESC);

-- Permissions
ALTER TABLE merchants ENABLE ROW LEVEL SECURITY;
ALTER TABLE reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

GRANT SELECT ON merchants TO anon, authenticated;
GRANT SELECT ON reviews TO anon, authenticated;
GRANT ALL ON reviews TO authenticated;
GRANT SELECT, UPDATE ON users TO authenticated;
GRANT SELECT ON users TO anon;

-- RLS Policies
-- Reviews
CREATE POLICY "Anyone can view reviews" ON reviews FOR SELECT USING (true);
CREATE POLICY "Users can insert their own reviews" ON reviews FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own reviews" ON reviews FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete their own reviews" ON reviews FOR DELETE USING (auth.uid() = user_id);

-- Users (Profiles)
CREATE POLICY "Anyone can view profiles" ON users FOR SELECT USING (true);
CREATE POLICY "Users can update their own profile" ON users FOR UPDATE USING (auth.uid() = id);
-- Note: Insert is usually handled by a trigger on auth.users, but we might allow manual insert if needed?
-- Better to use a trigger. I will add a trigger to auto-create user profile.

-- Function to handle new user
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
  INSERT INTO public.users (id, email, nickname)
  VALUES (new.id, new.email, split_part(new.email, '@', 1));
  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();
