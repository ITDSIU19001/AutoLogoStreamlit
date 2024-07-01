import streamlit as st
import os
import io
import zipfile
from PIL import Image
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip

class WatermarkApp:
    def __init__(self):
        # Center-align the title
        st.markdown(
            "<h1 style='text-align: center;'>Auto Watermark</h1>",
            unsafe_allow_html=True
        )

        # Right-align the footer
        st.markdown(
            "<div style='text-align: right;'>Made by Truong Quoc An</div>",
            unsafe_allow_html=True
        )

    def add_watermark_to_image(self, uploaded_file, watermark_path, position="Center", size=50, opacity=0.2, max_dimension_percent=50):
        # Check if the uploaded file is None
        if uploaded_file is None:
            st.error("No image uploaded.")
            return None

        # Open the image file
        try:
            original_image = Image.open(uploaded_file)
        except Exception as e:
            st.error(f"Error: {e}")
            return None

        # Resize the image if its size exceeds the limit
        max_allowed_pixels = 178956970
        if original_image.width * original_image.height > max_allowed_pixels:
            ratio = (max_allowed_pixels / (original_image.width * original_image.height)) ** 0.5
            new_width = int(original_image.width * ratio)
            new_height = int(original_image.height * ratio)
            original_image = original_image.resize((new_width, new_height))

        # Convert to RGB mode if the image is in CMYK mode
        if original_image.mode == "CMYK":
            original_image = original_image.convert("RGB")

        # Calculate the maximum dimensions based on the original image size and the specified percentage
        max_width = int(original_image.width * max_dimension_percent / 100)
        max_height = int(original_image.height * max_dimension_percent / 100)

        # Resize the image to reduce processing time
        original_image.thumbnail((max_width, max_height))

        watermark = Image.open(watermark_path)

        # Resize watermark based on size percentage
        watermark_width = original_image.width * size // 100
        w_percent = watermark_width / float(watermark.width)
        watermark_height = int(w_percent * watermark.height)
        watermark = watermark.resize((watermark_width, watermark_height), Image.LANCZOS)

        # Calculate watermark position
        if "Top" in position[0] and "Left" in position[1]:
            x_position = 0
            y_position = 0
        elif "Top" in position[0] and "Right" in position[1]:
            x_position = original_image.width - watermark_width
            y_position = 0
        elif "Bottom" in position[0] and "Left" in position[1]:
            x_position = 0
            y_position = original_image.height - watermark_height
        elif "Bottom" in position[0] and "Right" in position[1]:
            x_position = original_image.width - watermark_width
            y_position = original_image.height - watermark_height
        else:
            x_position = (original_image.width - watermark_width) // 2
            y_position = (original_image.height - watermark_height) // 2

        # Convert opacity to alpha value
        watermark = watermark.convert("RGBA")
        watermark_with_opacity = Image.new("RGBA", watermark.size)
        for x in range(watermark.width):
            for y in range(watermark.height):
                r, g, b, a = watermark.getpixel((x, y))
                watermark_with_opacity.putpixel((x, y), (r, g, b, int(a * opacity)))

        # Paste watermark onto original image
        watermarked_image = original_image.copy()
        watermarked_image.paste(watermark_with_opacity, (x_position, y_position), watermark_with_opacity)

        return watermarked_image

    def add_watermark_to_video(self, video_path, watermark_path, output_path, position=("Center", "Center"), opacity=0.5):
        try:
            # Load the video and the watermark
            video = VideoFileClip(video_path)
            watermark = ImageClip(watermark_path).set_duration(video.duration)
            
            # Set the opacity of the watermark
            watermark = watermark.set_opacity(opacity)
            
            # Position the watermark
            if "Top" in position[0] and "Left" in position[1]:
                watermark = watermark.set_position(("left", "top"))
            elif "Top" in position[0] and "Right" in position[1]:
                watermark = watermark.set_position(("right", "top"))
            elif "Bottom" in position[0] and "Left" in position[1]:
                watermark = watermark.set_position(("left", "bottom"))
            elif "Bottom" in position[0] and "Right" in position[1]:
                watermark = watermark.set_position(("right", "bottom"))
            else:
                watermark = watermark.set_position(("center", "center"))

            # Create a composite video with the watermark
            final = CompositeVideoClip([video, watermark])
            
            # Write the result to a file
            final.write_videofile(output_path, codec="libx264", audio_codec="aac")
            
            st.success(f"Successfully watermarked {video_path} and saved to {output_path}")
        except Exception as e:
            st.error(f"Error processing video: {e}")

def main():
    app = WatermarkApp()

    uploaded_files = st.file_uploader("Select image to watermark", type=["png", "jpg", "jpeg", "gif"], accept_multiple_files=True)
    watermark_option = st.radio("Select watermark option or upload new:",
                                ("Logo HTX Thanh Ngọt Năm Cập", "Logo Dr. KaKa", "Upload New"))

    watermark_file = None
    if watermark_option == "Logo HTX Thanh Ngọt Năm Cập":
        watermark_path = "logo1.png"  # Replace with the path to your pre-existing watermark file
        st.image("logo1.png", width=50)
    elif watermark_option == "Logo Dr. KaKa":
        watermark_path = "logo2.png"  # Replace with the path to your pre-existing watermark file
        st.image("logo2.png", width=50)
    else:
        watermark_file = st.file_uploader("Select watermark image or upload new", type=["png", "jpg", "jpeg", "gif"])
        if watermark_file:
            watermark_path = os.path.join("./temp", "uploaded_watermark.png")
            with open(watermark_path, "wb") as f:
                f.write(watermark_file.read())

    watermark_position = st.selectbox("Select watermark position",
                                     ["Top Left", "Top Center", "Top Right", "Center Left", "Center", "Center Right", "Bottom Left", "Bottom Center", "Bottom Right"],
                                     index=4)
    watermark_opacity = st.slider("Select watermark opacity", min_value=0.0, max_value=1.0, value=0.5)

    if st.button("Start Image Watermarking"):
        if uploaded_files:
            for i, uploaded_file in enumerate(uploaded_files):
                watermarked_image = app.add_watermark_to_image(uploaded_file, watermark_path, position=watermark_position.split(), opacity=watermark_opacity)
                if watermarked_image:
                    st.image(watermarked_image, caption=f"Watermarked Image {i+1}")

        st.write("---")

    video_file = st.file_uploader("Select video to watermark", type=["mp4", "mov", "avi"])
    if video_file:
        watermark_position_video = st.selectbox("Select watermark position for video",
                                                ["Top Left", "Top Center", "Top Right", "Center Left", "Center", "Center Right", "Bottom Left", "Bottom Center", "Bottom Right"],
                                                index=4)
        video_output_path = "./output/output_video.mp4"

        if st.button("Start Video Watermarking"):
            if watermark_file:
                app.add_watermark_to_video(video_file, watermark_path, video_output_path, position=watermark_position_video.split(), opacity=watermark_opacity)
            else:
                st.warning("Please upload a watermark image.")

if __name__ == "__main__":
    main()
