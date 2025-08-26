-- Insert sample achievements
INSERT INTO achievements (title, description, icon, category, condition_type, condition_value, points) VALUES
('First Steps', 'Complete your first lesson', '🎯', 'progress', 'lessons_completed', 1, 10),
('Practice Makes Perfect', 'Practice for 30 minutes total', '⏰', 'practice', 'practice_time', 1800, 15),
('Week Warrior', 'Practice for 7 days in a row', '🔥', 'streak', 'streak_days', 7, 25),
('Rhythm Master', 'Complete 5 rhythm exercises', '🥁', 'skill', 'custom', 5, 20),
('Melody Maker', 'Complete 5 melody exercises', '🎵', 'skill', 'custom', 5, 20),
('Dedicated Student', 'Complete 10 lessons', '📚', 'progress', 'lessons_completed', 10, 50),
('Speed Demon', 'Complete a lesson in under 10 minutes', '⚡', 'special', 'custom', 1, 30),
('Perfect Score', 'Get 100% on any exercise', '⭐', 'skill', 'score_average', 100, 40);

-- Insert sample lessons for beginners
INSERT INTO lessons (title, description, level, duration, order_index, learning_objectives) VALUES
('Welcome to Piano', 'Learn the basics of piano and proper posture', 'beginner', 15, 1, ARRAY['Understand piano layout', 'Learn proper sitting posture', 'Identify white and black keys']),
('Finding Middle C', 'Locate and play Middle C on the piano', 'beginner', 10, 2, ARRAY['Find Middle C', 'Play with correct finger', 'Understand hand position']),
('Right Hand Basics', 'Learn to play simple melodies with your right hand', 'beginner', 20, 3, ARRAY['Play C-D-E-F-G', 'Use correct fingering', 'Play simple melodies']),
('Left Hand Basics', 'Introduction to left hand playing', 'beginner', 20, 4, ARRAY['Play bass notes', 'Coordinate left hand', 'Simple bass patterns']),
('Both Hands Together', 'Coordinate both hands playing simple pieces', 'beginner', 25, 5, ARRAY['Hand coordination', 'Play simple duets', 'Maintain steady tempo']);

-- Insert sample exercises for the first lesson
INSERT INTO exercises (lesson_id, title, description, type, difficulty, order_index, instructions, expected_notes) VALUES
((SELECT id FROM lessons WHERE title = 'Welcome to Piano'), 'Piano Tour', 'Explore the piano keyboard', 'theory', 1, 1, 'Look at the piano and identify the pattern of black and white keys', '[]'),
((SELECT id FROM lessons WHERE title = 'Welcome to Piano'), 'Posture Check', 'Practice proper sitting posture', 'technique', 1, 2, 'Sit up straight with feet flat on the floor', '[]'),
((SELECT id FROM lessons WHERE title = 'Finding Middle C'), 'Find Middle C', 'Locate Middle C on your piano', 'theory', 2, 1, 'Find the group of two black keys and locate C to the left', '["C4"]'),
((SELECT id FROM lessons WHERE title = 'Finding Middle C'), 'Play Middle C', 'Press Middle C with your right thumb', 'melody', 2, 2, 'Use your right thumb (finger 1) to press Middle C', '["C4"]'),
((SELECT id FROM lessons WHERE title = 'Right Hand Basics'), 'C-D-E Scale', 'Play C-D-E with fingers 1-2-3', 'scale', 3, 1, 'Use fingers 1, 2, 3 to play C, D, E', '["C4", "D4", "E4"]'),
((SELECT id FROM lessons WHERE title = 'Right Hand Basics'), 'Simple Melody', 'Play a simple 3-note melody', 'melody', 3, 2, 'Play C-E-D-C using the correct fingers', '["C4", "E4", "D4", "C4"]');
