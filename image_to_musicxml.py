import streamlit as st
import subprocess
import os

def image_to_musicxml(image_path, output_dir="."):
    """
    Converts an image of a music sheet to a MusicXML file using oemer.

    Args:
        image_path (str): Path to the image file.
        output_dir (str): Directory to save the output MusicXML file.

    Returns:
        str: Path to the generated MusicXML file, or None if conversion fails.
    """
    if not os.path.exists(image_path):
        print(f"Error: Image file not found at {image_path}")
        return None

    try:
        output_filename = os.path.splitext(os.path.basename(image_path))[0] + ".musicxml"
        output_path = os.path.join(output_dir, output_filename)
        
        command = ["oemer", image_path, "-o", output_dir]
        
        subprocess.run(command, check=True, capture_output=True, text=True)

        if os.path.exists(output_path):
            return output_path
        else:
            files = [f for f in os.listdir(output_dir) if f.endswith('.musicxml')]
            if files:
                return os.path.join(output_dir, files[0])
            else:
                print("Error: oemer did not produce a MusicXML file.")
                return None

    except FileNotFoundError:
        print("Error: 'oemer' command not found. Please make sure it is installed and in your PATH.")
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error executing oemer: {e}")
        print(f"Stderr: {e.stderr}")
        print(f"Stdout: {e.stdout}")
        return None

def render_image_to_musicxml_ui():
    """Renders the UI for the Image-to-MusicXML feature."""
    st.header("Image to MusicXML Conversion")
    st.write("Upload an image of a music sheet to convert it into a MusicXML file.")

    uploaded_file = st.file_uploader("Choose an image file", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        temp_dir = "temp"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        image_path = os.path.join(temp_dir, uploaded_file.name)
        with open(image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.image(image_path, caption="Uploaded Image", use_column_width=True)

        if st.button("Convert to MusicXML"):
            with st.spinner("Converting image to MusicXML..."):
                musicxml_path = image_to_musicxml(image_path, temp_dir)

            if musicxml_path and os.path.exists(musicxml_path):
                st.success("Conversion successful!")
                with open(musicxml_path, "r") as f:
                    st.download_button(
                        label="Download MusicXML",
                        data=f.read(),
                        file_name=os.path.basename(musicxml_path),
                        mime="application/vnd.recordare.musicxml+xml"
                    )
            else:
                st.error("Failed to convert the image.")
