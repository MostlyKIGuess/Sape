import streamlit as st
import numpy as np

def extract_pitch_from_audio(audio_data, sr=16000):
    """Extract pitch using CREPE model."""
    try:
        import crepe
        import librosa
        
        # Resample to 16kHz for CREPE
        if sr != 16000:
            audio_data = librosa.resample(audio_data, orig_sr=sr, target_sr=16000)
            sr = 16000
        
        time, frequency, confidence, activation = crepe.predict(
            audio_data, sr, viterbi=True, step_size=10
        )
        
        frequency[confidence < 0.5] = 0
        # this removes low confidence frequencies
        # number can be adjusted on human feedback TODO!
        
        return time, frequency, confidence
    except Exception as e:
        st.error(f"Error extracting pitch: {e}")
        return None, None, None

def frequency_to_note_name(frequency):
    """Convert frequency to musical note name."""
    if frequency <= 0:
        return None
    
    A4 = 440
    C0 = A4 * np.power(2, -4.75)
    
    if frequency > C0:
        h = round(12 * np.log2(frequency / C0))
        octave = h // 12
        n = h % 12
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        return f"{note_names[n]}{octave}"
    return None

def process_whistle_audio(audio_data, sr=22050):
    """Process whistled audio to extract musical notes."""
    try:
        time, frequency, confidence = extract_pitch_from_audio(audio_data, sr)
        
        if time is None:
            return None
        
        # Segment into notes
        notes = []
        current_note = None
        note_threshold = 50  # Hz threshold for note changes
        min_duration = 0.1  # Minimum note duration in seconds
        
        for i, (t, f, c) in enumerate(zip(time, frequency, confidence)):
            note_name = frequency_to_note_name(f) if f > 0 else None
            
            if current_note is None and note_name:
                # Start new note
                current_note = {
                    'start_time': t,
                    'note_name': note_name,
                    'frequency': f,
                    'end_time': t
                }
            elif current_note and note_name:
                # Check if same note continues
                if abs(f - current_note['frequency']) < note_threshold:
                    current_note['end_time'] = t
                else:
                    # End current note and start new one
                    if current_note['end_time'] - current_note['start_time'] >= min_duration:
                        notes.append(current_note)
                    current_note = {
                        'start_time': t,
                        'note_name': note_name,
                        'frequency': f,
                        'end_time': t
                    }
            elif current_note and not note_name:
                if current_note['end_time'] - current_note['start_time'] >= min_duration:
                    notes.append(current_note)
                current_note = None
        
        if current_note and current_note['end_time'] - current_note['start_time'] >= min_duration:
            notes.append(current_note)
        
        return notes
    except Exception as e:
        st.error(f"Error processing whistle audio: {e}")
        return None
