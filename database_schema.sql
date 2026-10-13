-- =====================================================
-- Regrowth OS — Supabase Database Schema
-- INSTRUCTIONS: Copy ALL of this and run it in your
-- Supabase project → SQL Editor → New Query → Run
-- =====================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- USERS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    treatment_start_date DATE DEFAULT CURRENT_DATE,
    dosage_frequency INTEGER DEFAULT 2 CHECK (dosage_frequency IN (1, 2)),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- =====================================================
-- CHECK_INS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS check_ins (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    check_in_date DATE NOT NULL,
    time_of_day VARCHAR(20) NOT NULL CHECK (time_of_day IN ('morning', 'night')),
    ml_used DECIMAL(3,1) DEFAULT 1.0,
    points_earned INTEGER DEFAULT 10,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, check_in_date, time_of_day)
);

CREATE INDEX IF NOT EXISTS idx_check_ins_user_id ON check_ins(user_id);
CREATE INDEX IF NOT EXISTS idx_check_ins_date ON check_ins(check_in_date);

-- =====================================================
-- STREAKS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS streaks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    total_points INTEGER DEFAULT 0,
    last_check_in DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- MEDICINE_INVENTORY TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS medicine_inventory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    bottle_size_ml INTEGER DEFAULT 60,
    current_volume_ml DECIMAL(5,2) DEFAULT 60.00,
    doses_per_day INTEGER DEFAULT 2 CHECK (doses_per_day IN (1, 2)),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- PHOTOS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS photos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    photo_url TEXT NOT NULL,
    capture_date DATE NOT NULL,
    day_number INTEGER,
    photo_type VARCHAR(20) NOT NULL CHECK (photo_type IN ('hairline', 'crown')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_photos_user_id ON photos(user_id);
CREATE INDEX IF NOT EXISTS idx_photos_type ON photos(photo_type);

-- =====================================================
-- SYMPTOM_QUERIES TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS symptom_queries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    concern_type VARCHAR(100) NOT NULL,
    ai_response TEXT,
    escalated_to_doctor BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_symptom_queries_user_id ON symptom_queries(user_id);

-- =====================================================
-- DISABLE ROW LEVEL SECURITY
-- (Our app uses its own JWT auth, not Supabase Auth)
-- =====================================================
ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE check_ins DISABLE ROW LEVEL SECURITY;
ALTER TABLE streaks DISABLE ROW LEVEL SECURITY;
ALTER TABLE medicine_inventory DISABLE ROW LEVEL SECURITY;
ALTER TABLE photos DISABLE ROW LEVEL SECURITY;
ALTER TABLE symptom_queries DISABLE ROW LEVEL SECURITY;

-- =====================================================
-- UPDATED_AT TRIGGER
-- =====================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE OR REPLACE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE OR REPLACE TRIGGER update_streaks_updated_at
    BEFORE UPDATE ON streaks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- STORAGE BUCKET (Run SEPARATELY in Supabase Dashboard)
-- =====================================================
-- Go to: Supabase Dashboard → Storage → New Bucket
-- Name: progress-photos
-- Public: YES (check "Public bucket")
-- Then add this policy in Storage → progress-photos → Policies:
-- Policy name: "Allow all" 
-- For: ALL operations
-- Check: "Allow access to everyone"

-- =====================================================
-- VERIFY SETUP (run this to check tables were created)
-- =====================================================
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
