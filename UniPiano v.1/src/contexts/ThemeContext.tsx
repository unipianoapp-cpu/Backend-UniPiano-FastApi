"use client"

import type React from "react"
import { createContext, useState, type ReactNode } from "react"

interface ThemeContextType {
  isDark: boolean
  toggleTheme: () => void
  colors: {
    primary: string
    background: string
    surface: string
    text: string
    textSecondary: string
    border: string
  }
}

const lightColors = {
  primary: "#6366f1",
  background: "#ffffff",
  surface: "#f8fafc",
  text: "#1e293b",
  textSecondary: "#64748b",
  border: "#e2e8f0",
}

const darkColors = {
  primary: "#818cf8",
  background: "#0f172a",
  surface: "#1e293b",
  text: "#f1f5f9",
  textSecondary: "#94a3b8",
  border: "#334155",
}

export const ThemeContext = createContext<ThemeContextType>({
  isDark: false,
  toggleTheme: () => {},
  colors: lightColors,
})

interface ThemeProviderProps {
  children: ReactNode
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const [isDark, setIsDark] = useState(false)

  const toggleTheme = () => {
    setIsDark(!isDark)
  }

  const value = {
    isDark,
    toggleTheme,
    colors: isDark ? darkColors : lightColors,
  }

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
}
