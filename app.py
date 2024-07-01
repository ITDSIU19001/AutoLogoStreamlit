import streamlit as st
import os
import io
import zipfile
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from PIL import Image

class WatermarkApp:
    def __init__(self):
        # Center-align the title
        st.markdown(
            "<h1 style='text-align: center;'>Auto Watermark</h1>",
            unsafe_allow_html=True
        )

        # Right-align the st.write text
        st.markdown(
            "<div style='text-align: right;'>Made by Truong Quoc An</div>",
            unsafe_allow_html=True
        )

    def add_watermark_to_image(self, uploaded_file, watermark_path, position="Bottom Right", size=50, opacity=0.2, max_dimension_percent=50):
        if uploaded_file is None:
            st.error("No image uploaded.")
            return None

        try:
            original_image = Image.open(uploaded_file)
        except Exception as e:
            st.error(f"Error: {e}")
            return None

        max_allowed_pixels = 178956970
        if original_image.width * original_image.height > max_allowed_pixels:
            ratio = (max_allowed_pixels / (original_image.width * original_image.height)) ** 0.5
            new_width = int(original_image.width * ratio)
            new_height = int(original_image.height * ratio)
            original_image = original_image.resize((new_width, new_height))

        if original_image.mode == "CMYK":
            original_image = original_image.convert("RGB")

        max_width = int(original_image.width * max_dimension_percent / 100)
        max_height = int(original_image.height * max_dimension_percent / 100)
        original_image.thumbnail((max_width, max_height))

        watermark = Image.open(watermark_path)
        watermark_width = original_image.width * size // 100
        w_percent = watermark_width / float(watermark.width)
        watermark_height = int(w_percent * watermark.height)
        watermark = watermark.resize((watermark_width, watermark_height), Image.LANCZOS)

        if "Top" in position:
            y_position = 0
        elif "Bottom" in position:
            y_position = original_image.height - watermark_height
        else:
            y_position = (original_image.height - watermark_height) // 2

        if "Left" in position:
            x_position = 0
        elif "Right" in position:
            x_position = original_image.width - watermark_width
        else:
            x_position = (original_image.width - watermark_width) // 2

        watermark = watermark.convert("RGBA")
        watermark_with_opacity = Image.new("RGBA", watermark.size)
        for x in range(watermark.width):
            for y in range(watermark.height):
                r, g, b, a = watermark.getpixel((x, y))
                watermark_with_opacity.putpixel((x, y), (r, g, b, int(a * opacity)))

        watermarked_image = original_image.copy()
        watermarked_image.paste(watermark_with_opacity, (x_position, y_position), watermark_with_opacity)

        st.image(watermarked_image, caption='Processed Image', use_column_width=True)

    def add_watermark_to_video(self, video_path, watermark_path, output_path, position="center", size=60, opacity=0.5):
        try:
            video = VideoFileClip(video_path)
            watermark = ImageClip(watermark_path).set_duration(video.duration)

            watermark = watermark.set_opacity(opacity)
            watermark = watermark.resize(width=video.w * size / 100)
            watermark = watermark.set_position(position)

            final = CompositeVideoClip([video, watermark])
            final.write_videofile(output_path, codec="libx264", audio_codec="aac")

            return output_path
        except Exception as e:
            st.error(f"Error processing video: {e}")
            return None

    def save_uploaded_file(self, uploaded_file, target_path):
        try:
            with open(target_path, "wb") as f:
                f.write(uploaded_file.read())
            return target_path
        except Exception as e:
            st.error(f"Error saving file: {e}")
            return None

def main():
    app = WatermarkApp()

    tabs = st.tabs(["Image Watermarking", "Video Watermarking"])

    with tabs[0]:
        uploaded_images = st.file_uploader("Select images to watermark", type=["png", "jpg", "jpeg", "gif"], accept_multiple_files=True)
        
        watermark_option = st.radio("Select watermark option or upload new:", ("Logo HTX Thanh Ngọt Năm Cập", "Logo Dr. KaKa", "Upload New"), key="image_watermark_option")
        if watermark_option == "Logo HTX Thanh Ngọt Năm Cập":
            watermark_path = "logo1.png"  # Replace with the path to your pre-existing watermark file
            st.image("logo1.png", width=50)
        elif watermark_option == "Logo Dr. KaKa":
            watermark_path = "logo2.png"  # Replace with the path to your pre-existing watermark file
            st.image("logo2.png", width=50)
        else:
            watermark_file = st.file_uploader("Select or upload watermark image", type=["png", "jpg", "jpeg", "gif"], key="image_watermark_file")
            if watermark_file:
                watermark_path = app.save_uploaded_file(watermark_file, "watermark.png")

        watermark_position_image = st.selectbox("Select watermark position", ["Top Right", "Top Center", "Top Left", "Center Right", "Center", "Center Left", "Bottom Right", "Bottom Center", "Bottom Left"], index=4, key="image_watermark_position")
        watermark_size_image = st.slider("Select watermark size (%)", min_value=1, max_value=100, value=50, key="image_watermark_size")
        opacity_image = st.slider("Select watermark opacity", min_value=0.0, max_value=1.0, value=0.2, key="image_watermark_opacity")
        max_dimension_percent_image = st.slider("Select maximum dimension (%)", min_value=1, max_value=100, value=50, key="image_watermark_max_dim")

        col1, col2, col3 = st.columns([3, 1, 3])
        with col2:
            preview_button_image = st.button("Preview")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            start_process_button_image = st.button("Start Watermarking")

        if start_process_button_image:
            if watermark_path and uploaded_images:
                app.add_watermark_to_image(uploaded_images, watermark_path, watermark_position_image, watermark_size_image, opacity_image, max_dimension_percent_image)

        if preview_button_image:
            if watermark_path and uploaded_images:
                app.add_watermark_to_image(uploaded_images, watermark_path, watermark_position_image, watermark_size_image, opacity_image, max_dimension_percent_image)

    with tabs[1]:
        uploaded_videos = st.file_uploader("Select videos to watermark", type=["mp4"], accept_multiple_files=True)
        
        watermark_option_video = st.radio("Select watermark option or upload new:", ("Logo HTX Thanh Ngọt Năm Cập", "Logo Dr. KaKa", "Upload New"), key="video_watermark_option")
        if watermark_option_video == "Logo HTX Thanh Ngọt Năm Cập":
            watermark_path_video = "logo1.png"  # Replace with the path to your pre-existing watermark file
            st.image("logo1.png", width=50)
        elif watermark_option_video == "Logo Dr. KaKa":
            watermark_path_video = "logo2.png"  # Replace with the path to your pre-existing watermark file
            st.image("logo2.png", width=50)
        else:
            watermark_file_video = st.file_uploader("Select or upload watermark image", type=["png", "jpg", "jpeg", "gif"], key="video_watermark_file")
            if watermark_file_video:
                watermark_path_video = app.save_uploaded_file(watermark_file_video, "watermark.png")

        watermark_position_video = st.selectbox("Select watermark position", ["Center", "Top Left", "Top Right", "Bottom Left", "Bottom Right"], index=0, key="video_watermark_position")
        watermark_size_video = st.slider("Select watermark size (%)", min_value=1, max_value=100, value=60, key="video_watermark_size")
        opacity_video = st.slider("Select watermark opacity", min_value=0.0, max_value=1.0, value=0.5, key="video_watermark_opacity")

        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            start_video_process_button = st.button("Start Video Watermarking")

        if start_video_process_button:
            if watermark_path_video and uploaded_videos:
                output_directory = "watermarked_videos"
                os.makedirs(output_directory, exist_ok=True)
                output_files = []
                for i, video_file in enumerate(uploaded_videos):
                    video_filename = video_file.name
                    video_path = app.save_uploaded_file(video_file, os.path.join(output_directory, video_filename))
                    if video_path:
                        output_file = os.path.join(output_directory, f"watermarked_video_{i}.mp4")
                        app.add_watermark_to_video(video_path, watermark_path_video, output_file, watermark_position_video, watermark_size_video, opacity_video)
                        if output_file:
                            output_files.append(output_file)

                if output_files:
                    output_zip = io.BytesIO()
                    with zipfile.ZipFile(output_zip, "w") as zipf:
                        for output_file in output_files:
                            with open(output_file, "rb") as f:
                                zipf.writestr(os.path.basename(output_file), f.read())

                    st.download_button(label="Download Watermarked Videos", data=output_zip.getvalue(), file_name="watermarked_videos.zip")

if __name__ == "__main__":
    main()
