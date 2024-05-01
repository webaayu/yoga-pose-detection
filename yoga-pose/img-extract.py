import streamlit as st
import os,io
import fitz  # PyMuPDF
from PIL import Image
def extract_images_from_pdf(pdf_filename):
    try:
        images = []
        # Open the PDF file
        pdf_document = fitz.open(pdf_filename)
        
        # Iterate through each page of the PDF
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            
            # Get images on the page
            image_list = page.get_images(full=True)
            
            # Iterate through each image on the page
            for img_index, img_info in enumerate(image_list):
                xref = img_info[0]
                base_image = pdf_document.extract_image(xref)
                image_bytes = base_image["image"]
                image = Image.open(io.BytesIO(image_bytes))
                images.append(image)
                
        return images
    except Exception as e:
        st.error(f"Error extracting images from PDF: {e}")
        return None

def main():
    st.title("Yoga Pose Image Extractor")
    st.write("Click the button below to extract images from the PDF.")

    if st.button("Extract Images"):
        pdf_files = [file for file in os.listdir() if file.endswith(".pdf")]
        if not pdf_files:
            st.warning("No PDF file found in the current directory.")
        else:
            pdf_filename = pdf_files[0]  # Assuming only one PDF file is present
            images = extract_images_from_pdf(pdf_filename)
            if images:
                st.success(f"Extracted {len(images)} images from PDF")
                for idx, image in enumerate(images):
                    st.image(image, caption=f"Yoga Pose Image {idx + 1}")
            else:
                st.warning("No images found in the PDF")

if __name__ == "__main__":
    main()
