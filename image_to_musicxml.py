import streamlit as st
import subprocess
import os
import music21
from PIL import Image

def image_to_musicxml(image_path, output_dir="."):
    if not os.path.exists(image_path):
        st.error(f"Error: Image file not found at {image_path}")
        return None

    try:
        env = os.environ.copy()
        env['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'
        env['CUDA_MEMORY_FRACTION'] = '0.7'
        
        commands_to_try = [
            ["oemer", image_path, "-o", output_dir, "--without-deskew"],
            ["oemer", image_path, "-o", output_dir],
            ["oemer", image_path, "-o", output_dir, "--use-tf", "--without-deskew"],
        ]
        
        last_error = None
        for i, command in enumerate(commands_to_try):
            try:
                st.info(f"Attempt {i+1}: Trying with command: {' '.join(command)}")
                result = subprocess.run(command, check=True, capture_output=True, text=True, env=env, timeout=300)
                
                base_name = os.path.splitext(os.path.basename(image_path))[0]
                musicxml_path = os.path.join(output_dir, base_name + ".musicxml")
                
                if os.path.exists(musicxml_path):
                    st.success(f"Successfully converted image to MusicXML using attempt {i+1}")
                    return musicxml_path
                    
            except subprocess.TimeoutExpired:
                last_error = f"Attempt {i+1}: Process timed out after 5 minutes"
                st.warning(last_error)
                continue
            except subprocess.CalledProcessError as e:
                last_error = f"Attempt {i+1}: Command failed with error: {e.stderr}"
                st.warning(last_error)
                continue
        
        st.error(f"All conversion attempts failed. Last error: {last_error}")
        return None
        
    except Exception as e:
        st.error(f"Unexpected error during conversion: {str(e)}")
        return None

def resize_image(image_path, output_path, max_size=600):
    try:
        with Image.open(image_path) as img:
            original_size = img.size
            
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            width, height = img.size
            if max(width, height) > max_size:
                if width > height:
                    new_width = max_size
                    new_height = int((height * max_size) / width)
                else:
                    new_height = max_size
                    new_width = int((width * max_size) / height)
                
                img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                img_resized.save(output_path, "JPEG", quality=95, optimize=True)
                
                st.info(f"Image resized from {original_size} to {(new_width, new_height)}")
                return output_path
            else:
                img.save(output_path, "JPEG", quality=95, optimize=True)
                return output_path
                
    except Exception as e:
        st.error(f"Error resizing image: {str(e)}")
        return image_path

def render_image_to_musicxml_ui():
    st.header("Image to MusicXML & MIDI Conversion")
    st.write("Upload an image of a music sheet to convert it into a MusicXML file and a MIDI file.")
    
    st.info("Using GPU acceleration for faster processing. Large images will be resized to prevent memory issues.")

    uploaded_file = st.file_uploader("Choose an image file", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        temp_dir = "temp"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        original_image_path = os.path.join(temp_dir, uploaded_file.name)
        base_name, _ = os.path.splitext(uploaded_file.name)
        processed_image_path = os.path.join(temp_dir, base_name + "_processed.jpg")

        with open(original_image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        final_image_path = resize_image(original_image_path, processed_image_path, max_size=600)

        st.subheader("Processed Image")
        processed_image = Image.open(final_image_path)
        st.image(processed_image, caption="Image ready for processing", use_column_width=True)

        if st.button("Convert to MusicXML and MIDI"):
            with st.spinner("Converting image to MusicXML using GPU acceleration..."):
                musicxml_path = image_to_musicxml(final_image_path, temp_dir)

            if musicxml_path:
                st.success("Conversion completed successfully!")
                
                with open(musicxml_path, "rb") as file:
                    st.download_button(
                        label="Download MusicXML",
                        data=file,
                        file_name=os.path.basename(musicxml_path),
                        mime="application/xml"
                    )

                try:
                    score = music21.converter.parse(musicxml_path)
                    midi_path = musicxml_path.replace(".musicxml", ".mid")
                    score.write('midi', fp=midi_path)
                    
                    if os.path.exists(midi_path):
                        with open(midi_path, "rb") as file:
                            st.download_button(
                                label="Download MIDI",
                                data=file,
                                file_name=os.path.basename(midi_path),
                                mime="audio/midi"
                            )
                        st.success("MIDI file generated successfully!")
                except Exception as e:
                    st.warning(f"Could not generate MIDI file: {str(e)}")
            else:
                st.error("Failed to convert the image to MusicXML. Please try with a different image.")

if __name__ == "__main__":
    render_image_to_musicxml_ui()
