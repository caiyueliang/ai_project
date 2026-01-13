-- Users table (Supabase Auth handles the actual user management, this is for profile data)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email VARCHAR(255),
    phone VARCHAR(20),
    nickname VARCHAR(50),
    avatar_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Merchants table
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

-- Reviews table
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

-- Enable Row Level Security
ALTER TABLE merchants ENABLE ROW LEVEL SECURITY;
ALTER TABLE reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Grant permissions
GRANT SELECT ON merchants TO anon, authenticated;
GRANT SELECT ON reviews TO anon, authenticated;
GRANT ALL ON reviews TO authenticated;
GRANT SELECT, UPDATE ON users TO authenticated;
GRANT SELECT ON users TO anon;

-- RLS Policies

-- Merchants (Read only for public)
CREATE POLICY "Anyone can view merchants" ON merchants FOR SELECT USING (true);

-- Reviews
CREATE POLICY "Anyone can view reviews" ON reviews FOR SELECT USING (true);
CREATE POLICY "Users can insert their own reviews" ON reviews FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own reviews" ON reviews FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete their own reviews" ON reviews FOR DELETE USING (auth.uid() = user_id);

-- Users (Profiles)
CREATE POLICY "Anyone can view profiles" ON users FOR SELECT USING (true);
CREATE POLICY "Users can update their own profile" ON users FOR UPDATE USING (auth.uid() = id);

-- Function to handle new user creation
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
  INSERT INTO public.users (id, email, nickname)
  VALUES (new.id, new.email, split_part(new.email, '@', 1));
  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger for new user creation
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();

-- Insert some dummy data for merchants
INSERT INTO merchants (name, description, category, address, phone, business_hours, avg_rating, review_count, cover_image)
VALUES 
('好味道火锅', '正宗重庆老火锅，麻辣鲜香', '餐饮', '天河区体育西路101号', '020-88888888', '10:00-24:00', 4.8, 120, 'https://images.unsplash.com/photo-1596796929662-34721a63f969?w=800&auto=format&fit=crop&q=60'),
('星光电影院', 'IMAX巨幕影厅，极致视听享受', '娱乐', '海珠区江南西路202号', '020-66666666', '09:00-02:00', 4.5, 85, 'https://images.unsplash.com/photo-1517604931442-710c22061633?w=800&auto=format&fit=crop&q=60'),
('乐购超市', '生活用品一站式购物', '购物', '越秀区北京路303号', '020-99999999', '08:00-22:00', 4.2, 50, 'https://images.unsplash.com/photo-1578916171728-46686eac8d58?w=800&auto=format&fit=crop&q=60'),
('阳光咖啡馆', '安静舒适，适合办公', '餐饮', '天河区珠江新城404号', '020-77777777', '08:00-20:00', 4.6, 60, 'https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=800&auto=format&fit=crop&q=60'),
('极限健身房', '专业器械，私教指导', '娱乐', '白云区白云大道505号', '020-55555555', '07:00-23:00', 4.3, 40, 'https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=800&auto=format&fit=crop&q=60');
