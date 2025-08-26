import supabase from "./supabase"

class ApiService {
  private baseUrl = process.env.EXPO_PUBLIC_API_URL || "http://localhost:8000/api/v1"

  // Auth methods
  async signUp(email: string, password: string, userData: any) {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: userData,
      },
    })
    return { data, error }
  }

  async signIn(email: string, password: string) {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    })
    return { data, error }
  }

  async signOut() {
    const { error } = await supabase.auth.signOut()
    return { error }
  }

  async getCurrentUser() {
    const {
      data: { user },
      error,
    } = await supabase.auth.getUser()
    return { user, error }
  }

  // Lessons methods
  async getLessons(level?: string, category?: string) {
    let query = supabase.from("lessons").select("*").eq("is_active", true).order("order_index")

    if (level) query = query.eq("level", level)
    if (category) query = query.eq("category", category)

    const { data, error } = await query
    return { data, error }
  }

  async getLesson(id: string) {
    const { data, error } = await supabase.from("lessons").select("*, exercises(*)").eq("id", id).single()
    return { data, error }
  }

  // Exercises methods
  async getExercises(lessonId?: string) {
    let query = supabase.from("exercises").select("*").eq("is_active", true).order("order_index")

    if (lessonId) query = query.eq("lesson_id", lessonId)

    const { data, error } = await query
    return { data, error }
  }

  // Progress methods
  async getUserProgress(userId: string) {
    const { data, error } = await supabase
      .from("progress")
      .select("*, lessons(*), exercises(*)")
      .eq("user_id", userId)
      .order("updated_at", { ascending: false })
    return { data, error }
  }

  async updateProgress(progressData: any) {
    const { data, error } = await supabase.from("progress").upsert(progressData).select()
    return { data, error }
  }

  // Achievements methods
  async getUserAchievements(userId: string) {
    const { data, error } = await supabase
      .from("achievements")
      .select("*")
      .eq("user_id", userId)
      .eq("is_unlocked", true)
      .order("unlocked_at", { ascending: false })
    return { data, error }
  }

  // Audio submissions methods
  async uploadAudio(file: any, exerciseId: string, userId: string) {
    const fileName = `${userId}/${exerciseId}/${Date.now()}.m4a`

    const { data: uploadData, error: uploadError } = await supabase.storage
      .from("audio-submissions")
      .upload(fileName, file)

    if (uploadError) return { data: null, error: uploadError }

    const { data, error } = await supabase
      .from("audio_submissions")
      .insert({
        user_id: userId,
        exercise_id: exerciseId,
        file_path: fileName,
        status: "pending",
      })
      .select()
      .single()

    return { data, error }
  }

  async getAudioSubmissions(userId: string, exerciseId?: string) {
    let query = supabase
      .from("audio_submissions")
      .select("*, exercises(*)")
      .eq("user_id", userId)
      .order("created_at", { ascending: false })

    if (exerciseId) query = query.eq("exercise_id", exerciseId)

    const { data, error } = await query
    return { data, error }
  }
}

export default new ApiService()
