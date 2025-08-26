import * as FileSystem from "expo-file-system"
import supabase from "./supabase"

class AudioService {
  async uploadAudio(uri: string, exerciseId: string, userId: string) {
    try {
      // Read the file as base64
      const base64 = await FileSystem.readAsStringAsync(uri, {
        encoding: FileSystem.EncodingType.Base64,
      })

      // Convert base64 to blob
      const byteCharacters = atob(base64)
      const byteNumbers = new Array(byteCharacters.length)
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i)
      }
      const byteArray = new Uint8Array(byteNumbers)
      const blob = new Blob([byteArray], { type: "audio/m4a" })

      // Generate unique filename
      const fileName = `${userId}/${exerciseId}/${Date.now()}.m4a`

      // Upload to Supabase Storage
      const { data: uploadData, error: uploadError } = await supabase.storage
        .from("audio-submissions")
        .upload(fileName, blob)

      if (uploadError) {
        console.error("Upload error:", uploadError)
        return { success: false, error: uploadError.message }
      }

      // Save submission record to database
      const { data: submissionData, error: dbError } = await supabase
        .from("audio_submissions")
        .insert({
          user_id: userId,
          exercise_id: exerciseId,
          file_path: fileName,
          status: "pending",
        })
        .select()
        .single()

      if (dbError) {
        console.error("Database error:", dbError)
        return { success: false, error: dbError.message }
      }

      return { success: true, data: submissionData }
    } catch (error) {
      console.error("Audio upload error:", error)
      return { success: false, error: "Failed to upload audio" }
    }
  }

  async getSubmissions(userId: string) {
    try {
      const { data, error } = await supabase
        .from("audio_submissions")
        .select("*, exercises(*)")
        .eq("user_id", userId)
        .order("created_at", { ascending: false })

      if (error) {
        console.error("Get submissions error:", error)
        return { success: false, error: error.message }
      }

      return { success: true, data }
    } catch (error) {
      console.error("Get submissions error:", error)
      return { success: false, error: "Failed to get submissions" }
    }
  }

  async getSubmissionFeedback(submissionId: string) {
    try {
      const { data, error } = await supabase.from("audio_submissions").select("*").eq("id", submissionId).single()

      if (error) {
        console.error("Get feedback error:", error)
        return { success: false, error: error.message }
      }

      return { success: true, data }
    } catch (error) {
      console.error("Get feedback error:", error)
      return { success: false, error: "Failed to get feedback" }
    }
  }

  async analyzeAudio(submissionId: string) {
    try {
      // Call FastAPI backend for audio analysis
      const apiUrl = process.env.EXPO_PUBLIC_API_URL || "http://localhost:8000"
      const response = await fetch(`${apiUrl}/api/v1/audio/analyze/${submissionId}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      })

      if (!response.ok) {
        throw new Error("Analysis request failed")
      }

      const result = await response.json()
      return { success: true, data: result }
    } catch (error) {
      console.error("Audio analysis error:", error)
      return { success: false, error: "Failed to analyze audio" }
    }
  }
}

export default new AudioService()
