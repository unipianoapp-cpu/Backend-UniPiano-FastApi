-- Create audio_submissions table for recording analysis
CREATE TABLE IF NOT EXISTS audio_submissions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    exercise_id UUID REFERENCES exercises(id) ON DELETE CASCADE,
    audio_url TEXT NOT NULL,
    file_size INTEGER, -- in bytes
    duration INTEGER, -- in seconds
    analysis_result JSONB, -- AI analysis results
    score INTEGER CHECK (score >= 0 AND score <= 100),
    feedback TEXT,
    notes_detected JSONB, -- detected notes/chords
    timing_accuracy DECIMAL(5,2), -- percentage
    pitch_accuracy DECIMAL(5,2), -- percentage
    rhythm_accuracy DECIMAL(5,2), -- percentage
    processed BOOLEAN DEFAULT false,
    processing_error TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create RLS policies for audio_submissions table
ALTER TABLE audio_submissions ENABLE ROW LEVEL SECURITY;

-- Users can view and manage their own audio submissions
CREATE POLICY "Users can view own audio submissions" ON audio_submissions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own audio submissions" ON audio_submissions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own audio submissions" ON audio_submissions
    FOR UPDATE USING (auth.uid() = user_id);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_audio_submissions_user_id ON audio_submissions(user_id);
CREATE INDEX IF NOT EXISTS idx_audio_submissions_exercise_id ON audio_submissions(exercise_id);
CREATE INDEX IF NOT EXISTS idx_audio_submissions_processed ON audio_submissions(processed);
CREATE INDEX IF NOT EXISTS idx_audio_submissions_created_at ON audio_submissions(created_at);

-- Apply updated_at trigger to audio_submissions table
CREATE TRIGGER update_audio_submissions_updated_at
    BEFORE UPDATE ON audio_submissions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
