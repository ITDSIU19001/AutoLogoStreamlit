import streamlit as st
from PIL import Image
import os
import io
import zipfile
from base64 import b64encode

class WatermarkApp:
    def __init__(self):
        # Center-align the title
        st.markdown(
            "<h1 style='text-align: center;'>Auto watermark</h1>",
            unsafe_allow_html=True
        )

        # Right-align the st.write text
        st.markdown(
            "<div style='text-align: right;'>Made by Truong Quoc An</div>",
            unsafe_allow_html=True
        )

    @st.cache
    def add_watermark_to_image(self, uploaded_files, watermark_path, position="Bottom Right", size=50, opacity=0.2, max_dimension_percent=50):
        watermarked_images = []
        for uploaded_file in uploaded_files:
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
            if "Trên" in position:
                y_position = 0
            elif "Dưới" in position:
                y_position = original_image.height - watermark_height
            else:
                y_position = (original_image.height - watermark_height) // 2

            if "Trái" in position:
                x_position = 0
            elif "Phải" in position:
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

            watermarked_images.append(watermarked_image)

        return watermarked_images

    def image_to_bytes(self, image):
        img_byte_array = io.BytesIO()
        image.save(img_byte_array, format="PNG")
        return img_byte_array

def main():
    app = WatermarkApp()

    uploaded_files = st.file_uploader("Chọn ảnh để Watermark", type=["png", "jpg", "jpeg", "gif"], accept_multiple_files=True)

    watermark_file = None
    if watermark_file is None:
        watermark_option = st.radio("Chọn một trong những logo có sẵn hoặc tải lên mới:", ("Logo HTX Thanh Ngọt Năm Cập", "Logo Dr. KaKa", "Tải lên mới"))
        if watermark_option == "Logo HTX Thanh Ngọt Năm Cập":
            watermark_path = "logo1.png"  # Replace with the path to your pre-existing watermark file
            st.image("logo1.png", width=50)
        elif watermark_option == "Logo Dr. KaKa":
            watermark_path = "logo2.png"  # Replace with the path to your pre-existing watermark file
            st.image("logo2.png", width=50)
        else:
            watermark_path = watermark_file = st.file_uploader("Chọn watermark hoặc tải lên mới", type=["png", "jpg", "jpeg", "gif"])
    else:
        watermark_path = app.save_uploaded_file(watermark_file, "watermark.png")

    watermark_position = st.selectbox("Chọn vị trí watermark", ["Phía Trên Bên Phải", "Phía Trên Ở Giữa", "Phía Trên Bên Trái", "Ở Giữa Bên Phải", "Ở Giữa", "Ở Giữa Bên Trái", "Phía Dưới Bên Phải", "Phía Dưới Ở Giữa", "Phía Dưới Bên Trái"], index=4)
    watermark_size = st.slider("Chọn kích thước watermark (phần trăm)", min_value=1, max_value=100, value=50)
    opacity = st.slider("Chọn độ trong suốt của watermark", min_value=0.0, max_value=1.0, value=0.2)
    max_dimension_percent = st.slider("Chọn kích thước tối đa là bao nhiêu phần trăm so với ảnh gốc (Số càng nhỏ chạy càng nhanh)", min_value=1, max_value=100, value=50)

    col1, col2, col3 = st.columns([3, 1, 3])
    with col2:
        preview_button = st.button("Xem Trước")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        start_process_button = st.button("Bắt đầu quá trình watermark")

    watermarked_images = None
    if start_process_button:
        watermarked_images = app.add_watermark_to_image(uploaded_files, watermark_path, watermark_position, watermark_size, opacity, max_dimension_percent)


    if preview_button:
        app.preview_watermark(uploaded_files, watermark_path, watermark_position, watermark_size, opacity, max_dimension_percent)

    with st.expander("Danh sách ảnh đã được đóng dấu", expanded=True):
        if watermarked_images:
            col1, col2 = st.columns([3, 1])
            for i, image in enumerate(watermarked_images, start=1):
                preview_image = image.resize((100, 100))
                with col1:
                    st.image(preview_image, caption=f"Watermarked Image {i}")
                with col2:
                    st.download_button(label=f"Download Image {i}", data=app.image_to_bytes(image).getvalue(), file_name=f"watermarked_image_{i}.png")

    with st.expander("Hỗ trợ❤️❤️"):
        st.write("Truong Quoc An")
        st.write("TPBank")
        st.write("0327026628")

if __name__ == "__main__":
    main()
