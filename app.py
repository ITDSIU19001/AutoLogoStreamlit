import streamlit as st
from PIL import Image
import os
import io
import zipfile
from base64 import b64encode

class WatermarkApp:
    def __init__(self):
        st.title("Auto watermark - made by Truong Quoc An")
        st.info("Need support? Click the button below!")
        self.support_box = st.empty()

    def add_watermark(self, uploaded_files, watermark_file, watermark_position, watermark_size, opacity, max_dimension_percent):
        if uploaded_files and watermark_file:
            watermark_path = self.save_uploaded_file(watermark_file, "watermark.png")

            output_zip = io.BytesIO()
            with zipfile.ZipFile(output_zip, "w") as zipf:
                progress_bar = st.progress(0)
                counter_text = st.empty()
                n_files = len(uploaded_files)
                for i, uploaded_file in enumerate(uploaded_files, start=1):
                    watermarked_image = self.add_watermark_to_image(uploaded_file, watermark_path, watermark_position, watermark_size, opacity, max_dimension_percent)
                    watermarked_image_bytes = self.image_to_bytes(watermarked_image)
                    zipf.writestr(f"watermarked_{i}.png", watermarked_image_bytes.getvalue())

                    # Update progress bar
                    progress_bar.progress(i / n_files)
                    counter_text.text(f"{i}/{n_files} ảnh đã được Watermark")

            # Provide download link for the zip file
            st.markdown(self.get_binary_file_downloader_html(output_zip, "watermarked_images.zip", "Tải xuống Ảnh Đã Watermark"), unsafe_allow_html=True)

    def preview_watermark(self, uploaded_files, watermark_file, watermark_position, watermark_size, opacity, max_dimension_percent):
        if uploaded_files and watermark_file:
            watermark_path = self.save_uploaded_file(watermark_file, "watermark.png")
            first_uploaded_file = uploaded_files[0]

            watermarked_image = self.add_watermark_to_image(first_uploaded_file, watermark_path, watermark_position, watermark_size, opacity, max_dimension_percent)
            st.image(watermarked_image, caption="Xem trước Ảnh đã Watermark")

    def add_watermark_to_image(self, uploaded_file, watermark_path, position="Bottom Right", size=50, opacity=0.2, max_dimension_percent=50):
        original_image = Image.open(uploaded_file)

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

    def save_uploaded_file(self, uploaded_file, target_filename):
        with open(target_filename, "wb") as f:
            f.write(uploaded_file.read())
        return target_filename

    def image_to_bytes(self, image):
        img_byte_array = io.BytesIO()
        image.save(img_byte_array, format="PNG")
        return img_byte_array

    def get_binary_file_downloader_html(self, bin_data, file_label='File', button_label='Download'):
        href = f'<a href="data:application/zip;base64,{b64encode(bin_data.getvalue()).decode()}" download="{file_label}">{button_label}</a>'
        return href

def main():
    app = WatermarkApp()

    uploaded_files = st.file_uploader("Chọn ảnh để Watermark", type=["png", "jpg", "jpeg", "gif"], accept_multiple_files=True)
    watermark_file = st.file_uploader("Chọn watermark", type=["png", "jpg", "jpeg", "gif"])
    watermark_position = st.selectbox("Chọn vị trí watermark", ["Phía Trên Bên Phải", "Phía Trên Ở Giữa", "Phía Trên Bên Trái", "Ở Giữa Bên Phải", "Ở Giữa", "Ở Giữa Bên Trái", "Phía Dưới Bên Phải", "Phía Dưới Ở Giữa", "Phía Dưới Bên Trái"])
    watermark_size = st.slider("Chọn kích thước watermark (phần trăm)", min_value=1, max_value=100, value=50)
    opacity = st.slider("Chọn độ trong suốt của watermark", min_value=0.0, max_value=1.0, value=0.2)
    max_dimension_percent = st.slider("Chọn kích thước tối đa là bao nhiêu phần trăm so với ảnh gốc", min_value=1, max_value=100, value=50)

    col1, col2, col3 = st.columns([3, 1, 3])
    with col2:
        preview_button = st.button("Xem Trước")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        start_process_button = st.button("Bắt đầu quá trình watermark")

    if start_process_button:
        app.add_watermark(uploaded_files, watermark_file, watermark_position, watermark_size, opacity, max_dimension_percent)

    if preview_button:
        app.preview_watermark(uploaded_files, watermark_file, watermark_position, watermark_size, opacity, max_dimension_percent)

    if st.button("Hỗ trợ❤️"):
        app.support_box.text("Truong Quoc An\nTPBank\n0327026628\n❤️")

if __name__ == "__main__":
    main()
