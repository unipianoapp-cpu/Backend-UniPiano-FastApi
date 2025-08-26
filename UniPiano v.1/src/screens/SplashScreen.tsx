import { View, Text, ActivityIndicator, StyleSheet } from "react-native"

export default function SplashScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>🎹 Piano Learning</Text>
      <ActivityIndicator size="large" color="#6366f1" style={styles.loader} />
      <Text style={styles.subtitle}>Loading...</Text>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#ffffff",
  },
  title: {
    fontSize: 32,
    fontWeight: "bold",
    color: "#1e293b",
    marginBottom: 20,
  },
  loader: {
    marginVertical: 20,
  },
  subtitle: {
    fontSize: 16,
    color: "#64748b",
  },
})
