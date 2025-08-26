export interface User {
  id: string
  email: string
  name: string
  age?: number
  level: "beginner" | "intermediate" | "advanced"
  created_at: string
  updated_at: string
}

export interface Lesson {
  id: string
  title: string
  description: string
  level: "beginner" | "intermediate" | "advanced"
  category: string
  duration_minutes: number
  order_index: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Exercise {
  id: string
  lesson_id: string
  title: string
  description: string
  type: "scales" | "chords" | "melody" | "rhythm"
  difficulty: number
  instructions: string
  audio_example_url?: string
  sheet_music_url?: string
  order_index: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Progress {
  id: string
  user_id: string
  lesson_id?: string
  exercise_id?: string
  status: "not_started" | "in_progress" | "completed"
  score?: number
  time_spent_minutes: number
  completed_at?: string
  created_at: string
  updated_at: string
}

export interface Achievement {
  id: string
  user_id: string
  title: string
  description: string
  icon: string
  is_unlocked: boolean
  unlocked_at?: string
  created_at: string
}

export interface AudioSubmission {
  id: string
  user_id: string
  exercise_id: string
  file_path: string
  status: "pending" | "analyzed" | "failed"
  feedback?: string
  score?: number
  created_at: string
  updated_at: string
}
