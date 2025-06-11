import streamlit as st
import matplotlib.pyplot as plt
from io import BytesIO
import numpy as np

def create_sheet_music_from_notes(notes):
    """Create sheet music visualization using matplotlib."""
    try:
        fig, ax = plt.subplots(figsize=(12, 6))
        
        #  staff lines
        staff_lines = [0, 1, 2, 3, 4]
        for line in staff_lines:
            ax.axhline(y=line, color='black', linewidth=1)
        
        #  notes
        note_positions = {'C': 0, 'D': 0.5, 'E': 1, 'F': 1.5, 'G': 2, 'A': 2.5, 'B': 3}
        
        x_pos = 0
        for note in notes:
            if note['note_name']:
                note_base = note['note_name'][0]
                if note_base in note_positions:
                    y_pos = note_positions[note_base]
                    ax.scatter(x_pos, y_pos, s=200, c='black')
                    ax.text(x_pos, y_pos + 0.3, note['note_name'], ha='center', fontsize=8)
            x_pos += 1
        
        ax.set_xlim(-0.5, len(notes) + 0.5)
        ax.set_ylim(-0.5, 4.5)
        ax.set_title("Generated Sheet Music")
        ax.axis('off')
        
        # save to bytes
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
        buf.seek(0)
        plt.close()
        
        return buf.getvalue()
    except Exception as e:
        st.error(f"Error creating sheet music: {e}")
        return None

def create_midi_from_notes(notes, output_path):
    """Create MIDI file from detected notes."""
    try:
        import pretty_midi
        
        midi = pretty_midi.PrettyMIDI()
        instrument = pretty_midi.Instrument(program=0)  # Piano
        
        for i, note in enumerate(notes):
            if note['note_name'] and note['frequency'] > 0:
                # Convert note name to MIDI number
                note_number = pretty_midi.note_name_to_number(note['note_name'])
                
                # Create note with duration
                midi_note = pretty_midi.Note(
                    velocity=100,
                    pitch=note_number,
                    start=note['start_time'],
                    end=note['end_time']
                )
                instrument.notes.append(midi_note)
        
        midi.instruments.append(instrument)
        midi.write(output_path)
        return True
    except Exception as e:
        st.error(f"Error creating MIDI: {e}")
        return False

def canvas_to_midi(canvas_data, output_path):
    """Convert canvas drawing to MIDI file."""
    try:
        import pretty_midi
        
        if canvas_data is None or canvas_data.image_data is None:
            return False
        
        # Get image data
        img_data = np.array(canvas_data.image_data)
        
        # Convert to grayscale if RGB
        if len(img_data.shape) == 3:
            img_data = np.mean(img_data[:, :, :3], axis=2)
        
        height, width = img_data.shape
        
        # Create MIDI
        midi = pretty_midi.PrettyMIDI()
        instrument = pretty_midi.Instrument(program=0)  # Piano
        
        # Parameters
        time_step = 0.25  # Each column = 0.25 seconds
        pitch_range = (60, 84)  # C4 to C6
        
        # Process each column (time step)
        for x in range(width):
            column = img_data[:, x]
            
            # Find pixels that are drawn (non-white)
            drawn_pixels = np.where(column < 200)[0]  # Threshold for "drawn"
            
            for y in drawn_pixels:
                # Convert y position to pitch
                pitch = int(pitch_range[1] - (y / height) * (pitch_range[1] - pitch_range[0]))
                pitch = max(pitch_range[0], min(pitch_range[1], pitch))
                
                # Create note
                start_time = x * time_step
                end_time = start_time + time_step
                
                midi_note = pretty_midi.Note(
                    velocity=100,
                    pitch=pitch,
                    start=start_time,
                    end=end_time
                )
                instrument.notes.append(midi_note)
        
        midi.instruments.append(instrument)
        midi.write(output_path)
        return True
    except Exception as e:
        st.error(f"Error converting canvas to MIDI: {e}")
        return False

def midi_to_audio(midi_path, output_path):
    """Convert MIDI file to audio for playback."""
    try:
        import pretty_midi
        import soundfile as sf
        
        midi = pretty_midi.PrettyMIDI(midi_path)
        audio = midi.synthesize(fs=22050)
        sf.write(output_path, audio, 22050)
        return True
    except Exception as e:
        st.error(f"Error converting MIDI to audio: {e}")
        return False
