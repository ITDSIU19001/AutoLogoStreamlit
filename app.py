import streamlit as st
import os
import io
import zipfile
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from PIL import Image
import tempfile
import numpy as np

class WatermarkApp:
    def __init__(self):
        st.set_page_config(page_title="Auto Watermark", layout="wide")
        st.markdown("<h1 style='text-align: center;'>Auto Watermark</h1>", unsafe_allow_html=True)
        st.markdown("<div style='text-align: right;'>Made by Truong Quoc An</div>", unsafe_allow_html=True)

    def load_image(self, image_file):
        return Image.open(image_file)

    def add_watermark_to_image(self, original_image, watermark_path, position="Bottom Right", size=50, opacity=0.2, max_dimension_percent=50):
        try:
            max_allowed_pixels = 178956970
            if original_image.width * original_image.height > max_allowed_pixels:
                ratio = (max_allowed_pixels / (original_image.width * original_image.height)) ** 0.5
                new_width = int(original_image.width * ratio)
                new_height = int(original_image.height * ratio)
                original_image = original_image.resize((new_width, new_height), resample=Image.LANCZOS)

            if original_image.mode == "CMYK":
                original_image = original_image.convert("RGB")

            max_width = int(original_image.width * max_dimension_percent / 100)
            max_height = int(original_image.height * max_dimension_percent / 100)
            original_image.thumbnail((max_width, max_height), Image.LANCZOS)

            watermark = Image.open(watermark_path)
            watermark_width = original_image.width * size // 100
            w_percent = watermark_width / float(watermark.width)
            watermark_height = int(w_percent * watermark.height)
            watermark = watermark.resize((watermark_width, watermark_height), resample=Image.LANCZOS)

            x_position, y_position = self.calculate_position(position, original_image, watermark)

            watermark = watermark.convert("RGBA")
            watermark_with_opacity = Image.new("RGBA", watermark.size)
            for x in range(watermark.width):
                for y in range(watermark.height):
                    r, g, b, a = watermark.getpixel((x, y))
                    watermark_with_opacity.putpixel((x, y), (r, g, b, int(a * opacity)))

            watermarked_image = original_image.copy()
            watermarked_image.paste(watermark_with_opacity, (x_position, y_position), watermark_with_opacity)

            return watermarked_image
        except Exception as e:
            st.error(f"Error processing image: {e}")
            return None

    def calculate_position(self, position, original_image, watermark):
        if "Top" in position:
            y_position = 0
        elif "Bottom" in position:
            y_position = original_image.height - watermark.height
        else:
            y_position = (original_image.height - watermark.height) // 2

        if "Left" in position:
            x_position = 0
        elif "Right" in position:
            x_position = original_image.width - watermark.width
        else:
            x_position = (original_image.width - watermark.width) // 2

        return x_position, y_position



    def add_watermark_to_video(self, video_path, watermark_path, output_path, position="center", size=60, opacity=0.5):
        try:
            with st.spinner("Processing video..."):
                video = VideoFileClip(video_path)
                
                # Load the watermark image using PIL
                watermark_pil = Image.open(watermark_path).convert("RGBA")
                
                # Resize the watermark
                new_width = int(video.w * size / 100)
                watermark_pil = watermark_pil.resize((new_width, int(new_width * watermark_pil.height / watermark_pil.width)), 
                                                     resample=Image.LANCZOS)
                
                # Convert PIL image to numpy array
                watermark_array = np.array(watermark_pil)
                
                # Apply opacity
                watermark_array[:, :, 3] = (watermark_array[:, :, 3] * opacity).astype(np.uint8)
                
                # Create ImageClip from numpy array
                watermark = ImageClip(watermark_array, transparent=True).set_duration(video.duration)
    
                watermark = watermark.set_position(self.get_video_position(position))
    
                final = CompositeVideoClip([video, watermark])
                final.write_videofile(output_path, codec="libx264", audio_codec="aac")
    
            return output_path
        except Exception as e:
            st.error(f"Error processing video: {e}")
            return None

    def get_video_position(self, position):
        positions = {
            "center": ("center", "center"),
            "top left": ("left", "top"),
            "top right": ("right", "top"),
            "bottom left": ("left", "bottom"),
            "bottom right": ("right", "bottom")
        }
        return positions.get(position, ("center", "center"))

    def save_uploaded_file(self, uploaded_file):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                tmp_file.write(uploaded_file.read())
                return tmp_file.name
        except Exception as e:
            st.error(f"Error saving file: {e}")
            return None

def main():
    app = WatermarkApp()

    tabs = st.tabs(["Image Watermarking", "Video Watermarking"])

    with tabs[0]:
        process_images(app)

    with tabs[1]:
        process_videos(app)

def process_images(app):
    uploaded_images = st.file_uploader("Select images to watermark", type=["png", "jpg", "jpeg", "gif"], accept_multiple_files=True)
    
    watermark_path = get_watermark_path("Image")

    watermark_position_image = st.selectbox("Select watermark position (Image)", ["Top Right", "Top Center", "Top Left", "Center Right", "Center", "Center Left", "Bottom Right", "Bottom Center", "Bottom Left"], index=4)
    watermark_size_image = st.slider("Select watermark size (%) (Image)", min_value=1, max_value=100, value=50)
    opacity_image = st.slider("Select watermark opacity (Image)", min_value=0.0, max_value=1.0, value=0.2)
    max_dimension_percent_image = st.slider("Select maximum dimension (%) (Image)", min_value=1, max_value=100, value=50)

    col1, col2 = st.columns(2)
    with col1:
        preview_button_image = st.button("Preview (Image)")
    with col2:
        start_process_button_image = st.button("Start Watermarking (Image)")

    if preview_button_image or start_process_button_image:
        if watermark_path and uploaded_images:
            for uploaded_file in uploaded_images:
                original_image = app.load_image(uploaded_file)
                watermarked_image = app.add_watermark_to_image(
                    original_image, watermark_path, watermark_position_image, 
                    watermark_size_image, opacity_image, max_dimension_percent_image
                )
                if watermarked_image:
                    st.image(watermarked_image, caption=f'Processed Image: {uploaded_file.name}', use_column_width=True)
                    if start_process_button_image:
                        save_image(watermarked_image, uploaded_file.name)

def process_videos(app):
    uploaded_videos = st.file_uploader("Select videos to watermark", type=["mp4"], accept_multiple_files=True)
    
    watermark_path_video = get_watermark_path("Video")

    watermark_position_video = st.selectbox("Select watermark position (Video)", ["Center", "Top Left", "Top Right", "Bottom Left", "Bottom Right"], index=0)
    watermark_size_video = st.slider("Select watermark size (%) (Video)", min_value=1, max_value=100, value=60)
    opacity_video = st.slider("Select watermark opacity (Video)", min_value=0.0, max_value=1.0, value=0.5)

    start_video_process_button = st.button("Start Video Watermarking")

    if start_video_process_button:
        if watermark_path_video and uploaded_videos:
            output_directory = tempfile.mkdtemp()
            output_files = []
            for i, video_file in enumerate(uploaded_videos):
                video_path = app.save_uploaded_file(video_file)
                if video_path:
                    output_file = os.path.join(output_directory, f"watermarked_video_{i}.mp4")
                    processed_file = app.add_watermark_to_video(
                        video_path, watermark_path_video, output_file, 
                        watermark_position_video, watermark_size_video, opacity_video
                    )
                    if processed_file:
                        output_files.append(processed_file)

            if output_files:
                save_videos(output_files)

def get_watermark_path(context):
    watermark_option = st.radio(f"Select watermark option or upload new ({context})", ("Logo HTX Thanh Ngọt Năm Cập", "Logo Dr. KaKa", "Upload New"))
    if watermark_option == "Logo HTX Thanh Ngọt Năm Cập":
        watermark_path = "logo1.png"
        st.image("logo1.png", width=50)
    elif watermark_option == "Logo Dr. KaKa":
        watermark_path = "logo2.png"
        st.image("logo2.png", width=50)
    else:
        watermark_file = st.file_uploader(f"Select or upload watermark image ({context})", type=["png", "jpg", "jpeg", "gif"])
        if watermark_file:
            watermark_path = WatermarkApp().save_uploaded_file(watermark_file)
        else:
            watermark_path = None
    return watermark_path

def save_image(image, filename):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    st.download_button(
        label=f"Download {filename}",
        data=buffered.getvalue(),
        file_name=f"watermarked_{filename}",
        mime="image/png"
    )

def save_videos(output_files):
    output_zip = io.BytesIO()
    with zipfile.ZipFile(output_zip, "w") as zipf:
        for output_file in output_files:
            zipf.write(output_file, os.path.basename(output_file))
    st.download_button(
        label="Download Watermarked Videos",
        data=output_zip.getvalue(),
        file_name="watermarked_videos.zip",
        mime="application/zip"
    )

if __name__ == "__main__":
    main()
