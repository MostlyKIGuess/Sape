import streamlit as st
import tempfile
import os
import traceback
from audio_processing import process_whistle_audio
from midi_utils import create_sheet_music_from_notes, create_midi_from_notes
from audio_recorder_streamlit import audio_recorder

class WhistleToSheetApp:
    """Modular class for Whistle-to-Sheet functionality."""
    
    def process_uploaded_whistle(self, uploaded_file):
        """Process uploaded whistle audio file."""
        return self._process_whistle_common(uploaded_file.getvalue(), "uploaded whistle")
    
    def process_recorded_whistle(self, audio_bytes):
        """Process recorded whistle audio."""
        return self._process_whistle_common(audio_bytes, "recorded whistle")
    
    def _process_whistle_common(self, audio_bytes, source_name):
        """Common processing logic for whistle audio."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_audio_path = os.path.join(temp_dir, f"{source_name}.wav")
            midi_output_path = os.path.join(temp_dir, f"{source_name}_melody.mid")
            
            try:
                # Save audio
                with open(temp_audio_path, "wb") as f:
                    f.write(audio_bytes)
                
                # Load and process audio
                import librosa
                audio_data, sr = librosa.load(temp_audio_path)
                
                with st.spinner("Analyzing whistled melody..."):
                    notes = process_whistle_audio(audio_data, sr)
                
                if notes:
                    st.success(f"Detected {len(notes)} musical notes!")
                    
                    # Display detected notes
                    st.subheader("Detected Notes")
                    for i, note in enumerate(notes):
                        st.write(f"Note {i+1}: {note['note_name']} "
                               f"({note['start_time']:.2f}s - {note['end_time']:.2f}s)")
                    
                    # Generate sheet music
                    with st.spinner("Generating sheet music..."):
                        sheet_image = create_sheet_music_from_notes(notes)
                    
                    if sheet_image:
                        st.subheader("Generated Sheet Music")
                        st.image(sheet_image, caption="Sheet Music Preview")
                    
                    # Generate MIDI
                    if create_midi_from_notes(notes, midi_output_path):
                        with open(midi_output_path, "rb") as f:
                            midi_bytes = f.read()
                        
                        return midi_bytes
                else:
                    st.warning("No clear melody detected. Try whistling more clearly or loudly.")
                    return None
                    
            except Exception as e:
                st.error(f"Error processing {source_name}: {type(e).__name__}")
                print(traceback.format_exc())
                return None

def render_whistle_to_sheet_ui():
    """Render the complete Whistle-to-Sheet interface."""
    st.header("Whistle to Sheet Music")
    st.write("Record or upload a whistled melody to generate sheet music and MIDI.")
    
    whistle_app = WhistleToSheetApp()
    tab1, tab2 = st.tabs(["Upload Audio", "Record Whistle"])
    
    with tab1:
        st.subheader("Upload Whistled Audio")
        uploaded_whistle = st.file_uploader(
            "Choose a whistled audio file (.wav)",
            type=['wav'],
            key="whistle_uploader"
        )
        
        if uploaded_whistle:
            st.audio(uploaded_whistle.getvalue())
            
            if st.button("Process Whistled Audio", key="process_whistle_upload"):
                midi_bytes = whistle_app.process_uploaded_whistle(uploaded_whistle)
                
                if midi_bytes:
                    st.download_button(
                        label="Download MIDI File",
                        data=midi_bytes,
                        file_name="whistle_melody.mid",
                        mime="audio/midi",
                        key="download_whistle_upload"
                    )
    
    with tab2:
        st.subheader("Record Whistled Melody")
        st.write("Whistle a simple melody into your microphone.")
        
        whistle_audio = audio_recorder(
            text="Whistle your melody:",
            recording_color="#e8b62c",
            neutral_color="#6aa36f",
            icon_name="microphone",
            icon_size="3x",
            pause_threshold=5.0,
            key="whistle_recorder"
        )
        
        if whistle_audio:
            st.audio(whistle_audio, format="audio/wav")
            
            if st.button("Process Whistled Melody", key="process_whistle_record"):
                midi_bytes = whistle_app.process_recorded_whistle(whistle_audio)
                
                if midi_bytes:
                    st.download_button(
                        label="Download MIDI File",
                        data=midi_bytes,
                        file_name="whistle_melody.mid",
                        mime="audio/midi",
                        key="download_whistle_record"
                    )
