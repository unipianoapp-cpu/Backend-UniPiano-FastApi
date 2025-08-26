"use client"

import { useState, useEffect } from "react"
import { View, Text, ScrollView, TouchableOpacity, StyleSheet } from "react-native"
import { Ionicons } from "@expo/vector-icons"
import apiService from "../services/api"
import type { Lesson } from "../types"

export default function LessonsScreen() {
  const [lessons, setLessons] = useState<Lesson[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedLevel, setSelectedLevel] = useState<string>("all")

  useEffect(() => {
    loadLessons()
  }, [selectedLevel])

  const loadLessons = async () => {
    setLoading(true)
    try {
      const level = selectedLevel === "all" ? undefined : selectedLevel
      const { data, error } = await apiService.getLessons(level)
      if (data) setLessons(data)
    } catch (error) {
      console.error("Error loading lessons:", error)
    }
    setLoading(false)
  }

  const levels = [
    { key: "all", label: "All Levels" },
    { key: "beginner", label: "Beginner" },
    { key: "intermediate", label: "Intermediate" },
    { key: "advanced", label: "Advanced" },
  ]

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Piano Lessons</Text>
        <Text style={styles.subtitle}>Choose your learning path</Text>
      </View>

      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.levelFilter}>
        {levels.map((level) => (
          <TouchableOpacity
            key={level.key}
            style={[styles.levelButton, selectedLevel === level.key && styles.levelButtonActive]}
            onPress={() => setSelectedLevel(level.key)}
          >
            <Text style={[styles.levelButtonText, selectedLevel === level.key && styles.levelButtonTextActive]}>
              {level.label}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      <ScrollView style={styles.lessonsList}>
        {lessons.map((lesson) => (
          <TouchableOpacity key={lesson.id} style={styles.lessonCard}>
            <View style={styles.lessonIcon}>
              <Ionicons name="musical-notes" size={24} color="#6366f1" />
            </View>
            <View style={styles.lessonContent}>
              <Text style={styles.lessonTitle}>{lesson.title}</Text>
              <Text style={styles.lessonDescription}>{lesson.description}</Text>
              <View style={styles.lessonMeta}>
                <Text style={styles.lessonLevel}>{lesson.level}</Text>
                <Text style={styles.lessonDuration}>{lesson.duration_minutes} min</Text>
              </View>
            </View>
            <Ionicons name="chevron-forward" size={20} color="#94a3b8" />
          </TouchableOpacity>
        ))}
      </ScrollView>
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
  levelFilter: {
    paddingHorizontal: 24,
    marginBottom: 24,
  },
  levelButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: "#f1f5f9",
    marginRight: 12,
  },
  levelButtonActive: {
    backgroundColor: "#6366f1",
  },
  levelButtonText: {
    fontSize: 14,
    color: "#64748b",
    fontWeight: "500",
  },
  levelButtonTextActive: {
    color: "#ffffff",
  },
  lessonsList: {
    flex: 1,
    paddingHorizontal: 24,
  },
  lessonCard: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#f8fafc",
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  lessonIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: "#e0e7ff",
    alignItems: "center",
    justifyContent: "center",
  },
  lessonContent: {
    flex: 1,
    marginLeft: 16,
  },
  lessonTitle: {
    fontSize: 16,
    fontWeight: "600",
    color: "#1e293b",
    marginBottom: 4,
  },
  lessonDescription: {
    fontSize: 14,
    color: "#64748b",
    marginBottom: 8,
  },
  lessonMeta: {
    flexDirection: "row",
  },
  lessonLevel: {
    fontSize: 12,
    color: "#6366f1",
    fontWeight: "500",
    marginRight: 16,
    textTransform: "capitalize",
  },
  lessonDuration: {
    fontSize: 12,
    color: "#64748b",
  },
})
