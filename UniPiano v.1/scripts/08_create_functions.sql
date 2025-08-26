-- Function to get user progress summary
CREATE OR REPLACE FUNCTION get_user_progress_summary(user_uuid UUID)
RETURNS TABLE (
    total_lessons INTEGER,
    completed_lessons INTEGER,
    in_progress_lessons INTEGER,
    total_exercises INTEGER,
    completed_exercises INTEGER,
    average_score DECIMAL,
    total_practice_time INTEGER,
    current_level TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        (SELECT COUNT(*)::INTEGER FROM lessons WHERE is_active = true) as total_lessons,
        (SELECT COUNT(DISTINCT lesson_id)::INTEGER FROM progress WHERE user_id = user_uuid AND status = 'completed') as completed_lessons,
        (SELECT COUNT(DISTINCT lesson_id)::INTEGER FROM progress WHERE user_id = user_uuid AND status = 'in_progress') as in_progress_lessons,
        (SELECT COUNT(*)::INTEGER FROM exercises WHERE is_active = true) as total_exercises,
        (SELECT COUNT(*)::INTEGER FROM progress WHERE user_id = user_uuid AND status = 'completed' AND exercise_id IS NOT NULL) as completed_exercises,
        (SELECT COALESCE(AVG(score), 0)::DECIMAL FROM progress WHERE user_id = user_uuid AND score IS NOT NULL) as average_score,
        (SELECT COALESCE(SUM(time_spent), 0)::INTEGER FROM progress WHERE user_id = user_uuid) as total_practice_time,
        (SELECT level FROM users WHERE id = user_uuid) as current_level;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check and award achievements
CREATE OR REPLACE FUNCTION check_and_award_achievements(user_uuid UUID)
RETURNS TABLE (
    achievement_id UUID,
    title TEXT,
    description TEXT,
    icon TEXT,
    newly_earned BOOLEAN
) AS $$
DECLARE
    user_stats RECORD;
    achievement RECORD;
    already_earned BOOLEAN;
BEGIN
    -- Get user statistics
    SELECT * INTO user_stats FROM get_user_progress_summary(user_uuid);
    
    -- Check each achievement
    FOR achievement IN SELECT * FROM achievements WHERE is_active = true LOOP
        -- Check if user already has this achievement
        SELECT EXISTS(
            SELECT 1 FROM user_achievements 
            WHERE user_id = user_uuid AND achievement_id = achievement.id
        ) INTO already_earned;
        
        -- Skip if already earned
        IF already_earned THEN
            CONTINUE;
        END IF;
        
        -- Check achievement conditions
        CASE achievement.condition_type
            WHEN 'lessons_completed' THEN
                IF user_stats.completed_lessons >= achievement.condition_value THEN
                    INSERT INTO user_achievements (user_id, achievement_id) VALUES (user_uuid, achievement.id);
                    RETURN QUERY SELECT achievement.id, achievement.title, achievement.description, achievement.icon, true;
                END IF;
            WHEN 'practice_time' THEN
                IF user_stats.total_practice_time >= achievement.condition_value THEN
                    INSERT INTO user_achievements (user_id, achievement_id) VALUES (user_uuid, achievement.id);
                    RETURN QUERY SELECT achievement.id, achievement.title, achievement.description, achievement.icon, true;
                END IF;
            WHEN 'score_average' THEN
                IF user_stats.average_score >= achievement.condition_value THEN
                    INSERT INTO user_achievements (user_id, achievement_id) VALUES (user_uuid, achievement.id);
                    RETURN QUERY SELECT achievement.id, achievement.title, achievement.description, achievement.icon, true;
                END IF;
        END CASE;
    END LOOP;
    
    -- Return all user achievements (including previously earned ones)
    FOR achievement IN 
        SELECT a.id, a.title, a.description, a.icon
        FROM achievements a
        JOIN user_achievements ua ON a.id = ua.achievement_id
        WHERE ua.user_id = user_uuid
    LOOP
        RETURN QUERY SELECT achievement.id, achievement.title, achievement.description, achievement.icon, false;
    END LOOP;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get recommended lessons for a user
CREATE OR REPLACE FUNCTION get_recommended_lessons(user_uuid UUID)
RETURNS TABLE (
    lesson_id UUID,
    title TEXT,
    description TEXT,
    level TEXT,
    duration INTEGER,
    progress_status TEXT,
    recommendation_reason TEXT
) AS $$
DECLARE
    user_level TEXT;
    completed_lessons UUID[];
BEGIN
    -- Get user level
    SELECT users.level INTO user_level FROM users WHERE id = user_uuid;
    
    -- Get completed lessons
    SELECT ARRAY_AGG(DISTINCT lesson_id) INTO completed_lessons
    FROM progress 
    WHERE user_id = user_uuid AND status = 'completed';
    
    -- Return recommended lessons
    RETURN QUERY
    SELECT 
        l.id,
        l.title,
        l.description,
        l.level,
        l.duration,
        COALESCE(p.status, 'not_started') as progress_status,
        CASE 
            WHEN l.level = user_level AND (completed_lessons IS NULL OR l.id != ALL(completed_lessons)) THEN 'Perfect for your level'
            WHEN l.order_index = (SELECT MIN(order_index) FROM lessons WHERE level = user_level AND (completed_lessons IS NULL OR id != ALL(completed_lessons))) THEN 'Next in sequence'
            WHEN p.status = 'in_progress' THEN 'Continue where you left off'
            ELSE 'Recommended'
        END as recommendation_reason
    FROM lessons l
    LEFT JOIN progress p ON l.id = p.lesson_id AND p.user_id = user_uuid
    WHERE l.is_active = true
    AND (
        l.level = user_level 
        OR (l.level = 'beginner' AND user_level IN ('intermediate', 'advanced'))
        OR p.status = 'in_progress'
    )
    ORDER BY 
        CASE WHEN p.status = 'in_progress' THEN 1 ELSE 2 END,
        l.order_index;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
