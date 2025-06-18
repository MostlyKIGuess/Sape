import streamlit as st
import os
import logging
from basic_pitch import ICASSP_2022_MODEL_PATH

from audio_to_midi import render_audio_to_midi_ui
from whistle_to_sheet import render_whistle_to_sheet_ui
from draw_to_music import render_draw_to_music_ui
from image_to_musicxml import render_image_to_musicxml_ui

logging.basicConfig(level=logging.ERROR)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

st.set_page_config(layout="wide", page_title="SoundScape Studio")

def main():
    """Main application function."""
    st.title("SoundScape Studio")
    st.write("Turn sounds into music, drawings into melodies, and whistles into sheet music.")

    mode = st.selectbox(
        "Choose conversion mode:",
        ["Whistle-to-Sheet","Audio-to-MIDI", "Draw-to-Music", "Image-to-MusicXML"],
        label_visibility="collapsed"
    )
    st.markdown("<br>", unsafe_allow_html=True)

    logging.info(f"Model path: {ICASSP_2022_MODEL_PATH}")
    # purly for debugging purposes
    if mode == "Audio-to-MIDI" and not os.path.exists(ICASSP_2022_MODEL_PATH):
        st.error("Basic Pitch model path not found.")
        st.stop()

    if mode == "Audio-to-MIDI":
        render_audio_to_midi_ui()
    elif mode == "Whistle-to-Sheet":
        render_whistle_to_sheet_ui()
    elif mode == "Draw-to-Music":
        render_draw_to_music_ui()
    elif mode == "Image-to-MusicXML":
        render_image_to_musicxml_ui()
    else:
        st.error("Unknown mode selected.")

if __name__ == "__main__":
    main()
