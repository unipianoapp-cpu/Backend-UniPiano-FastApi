"use client"

import { useState, useContext } from "react"
import { View, Text, TouchableOpacity, StyleSheet, Alert } from "react-native"
import { Ionicons } from "@expo/vector-icons"
import { Audio } from "expo-av"
import { AuthContext } from "../contexts/AuthContext"
import audioService from "../services/audioService"

export default function PracticeScreen() {
  const [recording, setRecording] = useState<Audio.Recording | null>(null)
  const [isRecording, setIsRecording] = useState(false)
  const [isPlaying, setIsPlaying] = useState(false)
  const [sound, setSound] = useState<Audio.Sound | null>(null)
  const [recordingUri, setRecordingUri] = useState<string | null>(null)
  const [uploading, setUploading] = useState(false)

  const { user } = useContext(AuthContext)

  const startRecording = async () => {
    try {
      const permission = await Audio.requestPermissionsAsync()
      if (permission.status !== "granted") {
        Alert.alert("Permission required", "Please grant microphone permission to record audio")
        return
      }

      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      })

      const { recording } = await Audio.Recording.createAsync(Audio.RecordingOptionsPresets.HIGH_QUALITY)
      setRecording(recording)
      setIsRecording(true)
    } catch (err) {
      console.error("Failed to start recording", err)
      Alert.alert("Error", "Failed to start recording")
    }
  }

  const stopRecording = async () => {
    if (!recording) return

    setIsRecording(false)
    await recording.stopAndUnloadAsync()
    const uri = recording.getURI()
    setRecordingUri(uri)
    setRecording(null)
  }

  const playRecording = async () => {
    if (!recordingUri) return

    try {
      if (sound) {
        await sound.unloadAsync()
      }

      const { sound: newSound } = await Audio.Sound.createAsync({ uri: recordingUri }, { shouldPlay: true })
      setSound(newSound)
      setIsPlaying(true)

      newSound.setOnPlaybackStatusUpdate((status) => {
        if (status.isLoaded && status.didJustFinish) {
          setIsPlaying(false)
        }
      })
    } catch (error) {
      console.error("Error playing recording:", error)
      Alert.alert("Error", "Failed to play recording")
    }
  }

  const uploadRecording = async () => {
    if (!recordingUri || !user) return

    setUploading(true)
    try {
      const result = await audioService.uploadAudio(recordingUri, "practice-session", user.id)
      if (result.success) {
        Alert.alert("Success", "Recording uploaded successfully! Analysis will be available shortly.")
        setRecordingUri(null)
      } else {
        Alert.alert("Error", result.error || "Failed to upload recording")
      }
    } catch (error) {
      console.error("Upload error:", error)
      Alert.alert("Error", "Failed to upload recording")
    }
    setUploading(false)
  }

  const clearRecording = () => {
    setRecordingUri(null)
    if (sound) {
      sound.unloadAsync()
      setSound(null)
    }
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Practice Session</Text>
        <Text style={styles.subtitle}>Record yourself playing and get feedback</Text>
      </View>

      <View style={styles.recordingArea}>
        <View style={styles.visualizer}>
          <Ionicons
            name={isRecording ? "radio-button-on" : "mic"}
            size={80}
            color={isRecording ? "#ef4444" : "#6366f1"}
          />
          {isRecording && <Text style={styles.recordingText}>Recording...</Text>}
        </View>

        <View style={styles.controls}>
          {!isRecording && !recordingUri && (
            <TouchableOpacity style={styles.recordButton} onPress={startRecording}>
              <Ionicons name="mic" size={24} color="#ffffff" />
              <Text style={styles.buttonText}>Start Recording</Text>
            </TouchableOpacity>
          )}

          {isRecording && (
            <TouchableOpacity style={styles.stopButton} onPress={stopRecording}>
              <Ionicons name="stop" size={24} color="#ffffff" />
              <Text style={styles.buttonText}>Stop Recording</Text>
            </TouchableOpacity>
          )}

          {recordingUri && (
            <View style={styles.playbackControls}>
              <TouchableOpacity style={styles.playButton} onPress={playRecording} disabled={isPlaying}>
                <Ionicons name={isPlaying ? "pause" : "play"} size={24} color="#ffffff" />
                <Text style={styles.buttonText}>{isPlaying ? "Playing..." : "Play Recording"}</Text>
              </TouchableOpacity>

              <TouchableOpacity style={styles.uploadButton} onPress={uploadRecording} disabled={uploading}>
                <Ionicons name="cloud-upload" size={24} color="#ffffff" />
                <Text style={styles.buttonText}>{uploading ? "Uploading..." : "Get Feedback"}</Text>
              </TouchableOpacity>

              <TouchableOpacity style={styles.clearButton} onPress={clearRecording}>
                <Ionicons name="trash" size={24} color="#ffffff" />
                <Text style={styles.buttonText}>Clear</Text>
              </TouchableOpacity>
            </View>
          )}
        </View>
      </View>

      <View style={styles.tips}>
        <Text style={styles.tipsTitle}>Recording Tips:</Text>
        <Text style={styles.tipText}>• Find a quiet environment</Text>
        <Text style={styles.tipText}>• Hold your device close to the piano</Text>
        <Text style={styles.tipText}>• Play clearly and at a steady tempo</Text>
        <Text style={styles.tipText}>• Record for 30-60 seconds for best analysis</Text>
      </View>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#ffffff",
  },
  header: {
    padding: 24,
    paddingTop: 60,
  },
  title: {
    fontSize: 28,
    fontWeight: "bold",
    color: "#1e293b",
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 16,
    color: "#64748b",
  },
  recordingArea: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: 24,
  },
  visualizer: {
    alignItems: "center",
    marginBottom: 48,
  },
  recordingText: {
    fontSize: 18,
    color: "#ef4444",
    fontWeight: "600",
    marginTop: 16,
  },
  controls: {
    width: "100%",
  },
  recordButton: {
    backgroundColor: "#6366f1",
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
  },
  stopButton: {
    backgroundColor: "#ef4444",
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
  },
  playbackControls: {
    gap: 12,
  },
  playButton: {
    backgroundColor: "#10b981",
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    padding: 16,
    borderRadius: 12,
  },
  uploadButton: {
    backgroundColor: "#6366f1",
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    padding: 16,
    borderRadius: 12,
  },
  clearButton: {
    backgroundColor: "#64748b",
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    padding: 16,
    borderRadius: 12,
  },
  buttonText: {
    color: "#ffffff",
    fontSize: 16,
    fontWeight: "600",
    marginLeft: 8,
  },
  tips: {
    padding: 24,
    backgroundColor: "#f8fafc",
  },
  tipsTitle: {
    fontSize: 16,
    fontWeight: "600",
    color: "#1e293b",
    marginBottom: 12,
  },
  tipText: {
    fontSize: 14,
    color: "#64748b",
    marginBottom: 4,
  },
})
