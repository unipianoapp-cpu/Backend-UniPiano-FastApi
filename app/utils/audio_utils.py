import librosa
import numpy as np
from typing import Dict, List, Tuple, Any
import logging

logger = logging.getLogger(__name__)

class AudioAnalyzer:
    """Audio analysis utilities for piano recordings"""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
    
    def load_audio(self, file_path: str) -> Tuple[np.ndarray, int]:
        """Load audio file"""
        try:
            audio, sr = librosa.load(file_path, sr=self.sample_rate)
            return audio, sr
        except Exception as e:
            logger.error(f"Error loading audio file {file_path}: {e}")
            raise
    
    def extract_pitch(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Extract pitch using librosa"""
        try:
            # Use piptrack for pitch detection
            pitches, magnitudes = librosa.piptrack(y=audio, sr=sr, threshold=0.1)
            
            # Get the most prominent pitch at each time frame
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                pitch_values.append(pitch)
            
            return np.array(pitch_values)
        except Exception as e:
            logger.error(f"Error extracting pitch: {e}")
            raise
    
    def detect_notes(self, pitches: np.ndarray) -> List[str]:
        """Convert pitches to note names"""
        try:
            notes = []
            for pitch in pitches:
                if pitch > 0:  # Valid pitch
                    # Convert frequency to MIDI note number
                    midi_note = librosa.hz_to_midi(pitch)
                    # Convert MIDI note to note name
                    note_name = librosa.midi_to_note(int(round(midi_note)))
                    notes.append(note_name)
            
            return notes
        except Exception as e:
            logger.error(f"Error detecting notes: {e}")
            raise
    
    def analyze_rhythm(self, audio: np.ndarray, sr: int) -> Dict[str, Any]:
        """Analyze rhythm and timing"""
        try:
            # Detect onset times
            onset_frames = librosa.onset.onset_detect(y=audio, sr=sr)
            onset_times = librosa.frames_to_time(onset_frames, sr=sr)
            
            # Calculate tempo
            tempo, beats = librosa.beat.beat_track(y=audio, sr=sr)
            
            return {
                "tempo": float(tempo),
                "onset_times": onset_times.tolist(),
                "beat_times": librosa.frames_to_time(beats, sr=sr).tolist()
            }
        except Exception as e:
            logger.error(f"Error analyzing rhythm: {e}")
            raise
    
    def compare_with_expected(self, detected_notes: List[str], expected_notes: List[str]) -> Dict[str, float]:
        """Compare detected notes with expected notes"""
        try:
            if not expected_notes:
                return {"accuracy": 0.0, "precision": 0.0, "recall": 0.0}
            
            # Simple accuracy calculation
            correct_notes = 0
            total_expected = len(expected_notes)
            total_detected = len(detected_notes)
            
            # Count correct notes (simple matching)
            for i, expected in enumerate(expected_notes):
                if i < len(detected_notes) and detected_notes[i] == expected:
                    correct_notes += 1
            
            accuracy = (correct_notes / total_expected) * 100 if total_expected > 0 else 0
            precision = (correct_notes / total_detected) * 100 if total_detected > 0 else 0
            recall = (correct_notes / total_expected) * 100 if total_expected > 0 else 0
            
            return {
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall
            }
        except Exception as e:
            logger.error(f"Error comparing notes: {e}")
            raise
    
    def analyze_audio_submission(self, file_path: str, expected_notes: List[str]) -> Dict[str, Any]:
        """Complete audio analysis for a submission"""
        try:
            # Load audio
            audio, sr = self.load_audio(file_path)
            
            # Extract features
            pitches = self.extract_pitch(audio, sr)
            detected_notes = self.detect_notes(pitches)
            rhythm_analysis = self.analyze_rhythm(audio, sr)
            
            # Compare with expected
            comparison = self.compare_with_expected(detected_notes, expected_notes)
            
            # Calculate overall score
            pitch_score = comparison["accuracy"]
            rhythm_score = 85.0  # Placeholder - would need more sophisticated rhythm analysis
            timing_score = 80.0  # Placeholder - would need timing analysis
            
            overall_score = (pitch_score + rhythm_score + timing_score) / 3
            
            return {
                "score": int(overall_score),
                "pitch_accuracy": pitch_score,
                "rhythm_accuracy": rhythm_score,
                "timing_accuracy": timing_score,
                "detected_notes": detected_notes,
                "expected_notes": expected_notes,
                "tempo": rhythm_analysis["tempo"],
                "analysis_details": {
                    "onset_times": rhythm_analysis["onset_times"],
                    "beat_times": rhythm_analysis["beat_times"],
                    "pitch_values": pitches.tolist()
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing audio submission: {e}")
            raise

# Global analyzer instance
audio_analyzer = AudioAnalyzer()
