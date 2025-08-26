-- Create lessons table
CREATE TABLE IF NOT EXISTS lessons (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    level TEXT NOT NULL CHECK (level IN ('beginner', 'intermediate', 'advanced')),
    duration INTEGER NOT NULL, -- in minutes
    video_url TEXT,
    audio_url TEXT,
    sheet_music_url TEXT,
    thumbnail_url TEXT,
    order_index INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    prerequisites TEXT[], -- array of lesson IDs that must be completed first
    learning_objectives TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create RLS policies for lessons table
ALTER TABLE lessons ENABLE ROW LEVEL SECURITY;

-- All authenticated users can view active lessons
CREATE POLICY "Authenticated users can view active lessons" ON lessons
    FOR SELECT USING (auth.role() = 'authenticated' AND is_active = true);

-- Create index for better performance
CREATE INDEX IF NOT EXISTS idx_lessons_level ON lessons(level);
CREATE INDEX IF NOT EXISTS idx_lessons_order ON lessons(order_index);
CREATE INDEX IF NOT EXISTS idx_lessons_active ON lessons(is_active);

-- Apply updated_at trigger to lessons table
CREATE TRIGGER update_lessons_updated_at
    BEFORE UPDATE ON lessons
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
