import streamlit as st
import tempfile
import os
import traceback
from basic_pitch.inference import predict_and_save
from basic_pitch import ICASSP_2022_MODEL_PATH
from audio_recorder_streamlit import audio_recorder

def process_audio(audio_file_path, output_directory, source_filename="input_audio"):
    """Processes an audio file and save the MIDI output."""
    try:
        model_path_to_load = ICASSP_2022_MODEL_PATH
        
        with st.status("Converting audio to MIDI...") as status:
            if not os.path.exists(model_path_to_load):
                st.error(f"Model path not found at {model_path_to_load}")
                return None, None

            status.update(label="Generating MIDI transcription...")
            predict_and_save(
                [audio_file_path],
                output_directory,
                True,    # save_midi
                False,   # sonify_midi
                False,   # save_model_outputs
                False,   # save_notes
                model_path_to_load
            )

        base_name = os.path.splitext(os.path.basename(source_filename))[0]
        midi_file_path = os.path.join(output_directory, f"{base_name}_basic_pitch.mid")

        if os.path.exists(midi_file_path):
            return midi_file_path, base_name
        else:
            st.error("MIDI file generation failed.")
            return None, None

    except Exception as e:
        print(f"Error during transcription: {e}")
        print(traceback.format_exc())
        st.error(f"Transcription error: {type(e).__name__}")
        return None, None

def render_audio_to_midi_ui():
    """Render the complete Audio-to-MIDI interface."""
    st.header("Audio to MIDI Conversion")
    tab1, tab2 = st.tabs(["Upload File", "Record Audio"])

    with tab1:
        st.subheader("Upload an Audio File")
        uploaded_file = st.file_uploader(
            "Choose an audio file (.wav, .mp3, .ogg, .flac)",
            type=['wav', 'mp3', 'ogg', 'flac'],
            key="file_uploader"
        )

        if uploaded_file:
            st.audio(uploaded_file.getvalue())

            if st.button("Convert Uploaded Audio to MIDI", key="convert_upload"):
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_audio_path = os.path.join(temp_dir, uploaded_file.name)
                    output_dir = os.path.join(temp_dir, "midi_output_upload")
                    os.makedirs(output_dir, exist_ok=True)

                    try:
                        with open(temp_audio_path, "wb") as f:
                            f.write(uploaded_file.getvalue())

                        if os.path.exists(temp_audio_path) and os.path.getsize(temp_audio_path) > 0:
                            st.success(f"Audio saved ({os.path.getsize(temp_audio_path)} bytes)")

                            with st.spinner("Processing uploaded audio..."):
                                midi_file_path, base_name = process_audio(temp_audio_path, output_dir, uploaded_file.name)

                            if midi_file_path and os.path.exists(midi_file_path):
                                st.success("MIDI conversion successful!")

                                with open(midi_file_path, "rb") as f:
                                    midi_bytes = f.read()

                                st.download_button(
                                    label="Download MIDI File",
                                    data=midi_bytes,
                                    file_name=f"{base_name}_basic_pitch.mid",
                                    mime="audio/midi",
                                    key="download_upload"
                                )
                            elif not midi_file_path:
                                 st.warning("Conversion process did not return a MIDI file path.")
                            else:
                                 st.error("MIDI file was not found after processing.")
                        else:
                            st.error("Failed to save uploaded audio file. Please try again.")

                    except Exception as e:
                        st.error(f"Error processing uploaded audio: {type(e).__name__}")
                        print(traceback.format_exc())
        else:
            st.info("Upload an audio file to begin.")

    with tab2:
        st.subheader("Record Audio from Microphone")
        st.write("Click the microphone icon to start recording. Click again to stop.")
        st.write("Note: Yellow -> recording, green -> ready to record")

        audio_bytes = audio_recorder(
            text="Click to Record:",
            recording_color="#e8b62c",
            neutral_color="#6aa36f",
            icon_name="microphone",
            icon_size="3x",
            pause_threshold=8.0,
        )

        if audio_bytes:
            st.subheader("Recorded Audio")
            st.audio(audio_bytes, format="audio/wav")

            if st.button("Convert Recorded Audio to MIDI", key="convert_record"):
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_audio_path = os.path.join(temp_dir, "recorded_audio.wav")
                    output_dir = os.path.join(temp_dir, "midi_output_record")
                    os.makedirs(output_dir, exist_ok=True)

                    try:
                        with open(temp_audio_path, "wb") as f:
                            f.write(audio_bytes)

                        if os.path.exists(temp_audio_path) and os.path.getsize(temp_audio_path) > 0:
                            st.success(f"Recorded audio saved ({os.path.getsize(temp_audio_path)} bytes)")

                            with st.spinner("Processing recorded audio..."):
                                midi_file_path, base_name = process_audio(temp_audio_path, output_dir, "recorded_audio.wav")

                            if midi_file_path and os.path.exists(midi_file_path):
                                st.success("MIDI conversion successful!")

                                with open(midi_file_path, "rb") as f:
                                    midi_bytes = f.read()

                                st.download_button(
                                    label="Download MIDI File",
                                    data=midi_bytes,
                                    file_name=f"{base_name}_basic_pitch.mid",
                                    mime="audio/midi",
                                    key="download_record"
                                )
                            elif not midi_file_path:
                                st.warning("Conversion process did not return a MIDI file path.")
                            else:
                                st.error("MIDI file was not found after processing.")
                        else:
                            st.error("Failed to save recorded audio file. Please try again.")

                    except Exception as e:
                        st.error(f"Error processing recorded audio: {type(e).__name__}")
                        print(traceback.format_exc())
        else:
            st.info("Click the microphone icon above to start recording.")
