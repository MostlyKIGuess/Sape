import streamlit as st
import tempfile
import os
from midi_utils import canvas_to_midi, midi_to_audio

class DrawToMusicApp:
    """Modular class for Draw-to-Music functionality."""
    
    def __init__(self):
        self.canvas_key = "drawing_canvas"
        
    def render_canvas_controls(self):
        """Render canvas drawing controls."""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            drawing_mode = st.selectbox(
                "Drawing tool:", 
                ["freedraw", "line", "rect", "circle"],
                key="drawing_mode"
            )
        
        with col2:
            stroke_width = st.slider(
                "Stroke width:", 
                1, 25, 3,
                key="stroke_width"
            )
        
        with col3:
            stroke_color = st.color_picker(
                "Stroke color:", 
                "#000000",
                key="stroke_color"
            )
        
        return drawing_mode, stroke_width, stroke_color
    
    def render_canvas(self, drawing_mode, stroke_width, stroke_color):
        """Render the drawing canvas."""
        from streamlit_drawable_canvas import st_canvas
        
        canvas_result = st_canvas(
            fill_color="rgba(255, 255, 255, 0)",
            stroke_width=stroke_width,
            stroke_color=stroke_color,
            background_color="#ffffff",
            height=500,  # Made bigger
            width=1000,  # Made bigger
            drawing_mode=drawing_mode,
            key=self.canvas_key,
        )
        
        return canvas_result
    
    def clear_canvas(self):
        """Clear the canvas by updating the key."""
        import time
        if self.canvas_key in st.session_state:
            del st.session_state[self.canvas_key]
        self.canvas_key = f"drawing_canvas_{int(time.time())}"
    
    def process_drawing(self, canvas_result):
        """Process the drawing and return MIDI and audio files."""
        if canvas_result is None or canvas_result.image_data is None:
            return None, None
        
        with tempfile.TemporaryDirectory() as temp_dir:
            midi_output_path = os.path.join(temp_dir, "drawn_music.mid")
            audio_output_path = os.path.join(temp_dir, "drawn_music.wav")
            
            #  drawing to MIDI
            if canvas_to_midi(canvas_result, midi_output_path):
                #  MIDI to audio for playback
                if midi_to_audio(midi_output_path, audio_output_path):
                    # Read files into memory
                    with open(midi_output_path, "rb") as f:
                        midi_bytes = f.read()
                    with open(audio_output_path, "rb") as f:
                        audio_bytes = f.read()
                    
                    return midi_bytes, audio_bytes
        
        return None, None
    
    def render_instructions(self):
        """Render usage instructions."""
        st.subheader("How to Use:")
        st.write("- **X-axis (horizontal)**: Represents time progression")
        st.write("- **Y-axis (vertical)**: Represents pitch (top = high notes, bottom = low notes)")
        st.write("- Draw patterns, melodies, or abstract shapes")
        st.write("- Each column of pixels becomes a time step in the music")
        st.write("- Try drawing horizontal lines for sustained notes or curves for melodies")
        st.write("- **Canvas size**: 1000x500 pixels for more detailed drawings")

def render_draw_to_music_ui():
    """Render the complete Draw-to-Music interface."""
    st.header("Draw to Music")
    st.write("Draw on the canvas to create music. X-axis = time, Y-axis = pitch (higher = higher pitch).")
    
    try:
        if 'draw_app' not in st.session_state:
            st.session_state.draw_app = DrawToMusicApp()
        
        draw_app = st.session_state.draw_app
        
        drawing_mode, stroke_width, stroke_color = draw_app.render_canvas_controls()
        canvas_result = draw_app.render_canvas(drawing_mode, stroke_width, stroke_color)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Listen to Drawing", key="listen_drawing"):
                if canvas_result.image_data is not None:
                    with st.spinner("Converting drawing to music..."):
                        midi_bytes, audio_bytes = draw_app.process_drawing(canvas_result)
                    
                    if audio_bytes:
                        st.success("Music generated from your drawing!")
                        st.subheader("Listen to Your Drawing")
                        st.audio(audio_bytes, format="audio/wav")
                        
                        # Store for download
                        st.session_state.drawing_midi = midi_bytes
                        st.session_state.drawing_audio = audio_bytes
                    else:
                        st.error("Failed to generate music from drawing.")
                else:
                    st.warning("Please draw something on the canvas first.")
        
        with col2:
            if st.button("Download MIDI", key="download_drawing"):
                if hasattr(st.session_state, 'drawing_midi') and st.session_state.drawing_midi:
                    st.download_button(
                        label="Download MIDI File",
                        data=st.session_state.drawing_midi,
                        file_name="drawn_music.mid",
                        mime="audio/midi",
                        key="download_midi_actual"
                    )
                else:
                    st.warning("Please generate music first by clicking 'Listen to Drawing'.")
        
        with col3:
            if st.button("Clear Canvas", key="clear_canvas"):
                draw_app.clear_canvas()
                if hasattr(st.session_state, 'drawing_midi'):
                    del st.session_state.drawing_midi
                if hasattr(st.session_state, 'drawing_audio'):
                    del st.session_state.drawing_audio
                st.rerun()
        
        draw_app.render_instructions()
        
    except ImportError:
        st.error("Drawable canvas not available. Please install streamlit-drawable-canvas.")
