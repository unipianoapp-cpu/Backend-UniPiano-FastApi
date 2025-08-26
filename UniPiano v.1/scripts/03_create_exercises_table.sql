-- Create exercises table
CREATE TABLE IF NOT EXISTS exercises (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    lesson_id UUID REFERENCES lessons(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('rhythm', 'melody', 'chord', 'scale', 'technique', 'theory')),
    difficulty INTEGER NOT NULL CHECK (difficulty >= 1 AND difficulty <= 10),
    audio_url TEXT,
    sheet_music_url TEXT,
    expected_notes JSONB, -- array of expected notes/chords
    tempo INTEGER, -- BPM for rhythm exercises
    key_signature TEXT, -- for melody/chord exercises
    time_signature TEXT, -- for rhythm exercises
    instructions TEXT,
    hints TEXT[],
    order_index INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create RLS policies for exercises table
ALTER TABLE exercises ENABLE ROW LEVEL SECURITY;

-- All authenticated users can view active exercises
CREATE POLICY "Authenticated users can view active exercises" ON exercises
    FOR SELECT USING (auth.role() = 'authenticated' AND is_active = true);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_exercises_lesson_id ON exercises(lesson_id);
CREATE INDEX IF NOT EXISTS idx_exercises_type ON exercises(type);
CREATE INDEX IF NOT EXISTS idx_exercises_difficulty ON exercises(difficulty);
CREATE INDEX IF NOT EXISTS idx_exercises_order ON exercises(order_index);

-- Apply updated_at trigger to exercises table
CREATE TRIGGER update_exercises_updated_at
    BEFORE UPDATE ON exercises
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
