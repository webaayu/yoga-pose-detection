import streamlit as st
import os
import io
import fitz  # PyMuPDF
from PIL import Image
import google.generativeai as genai

# Configure Google API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def extract_images_from_pdf(pdf_filename):
    images_data = []
    try:
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

                # Get image name
                image_name = base_image.get("image_name", f"Image {page_num + 1}")

                # Append image name and page number to the list
                images_data.append({"Image Name": image_name, "Page Number": page_num + 1})

        return images_data
    except Exception as e:
        st.error(f"Error extracting images from PDF: {e}")
        return None

def get_gemini_response(prompt):
    # Load the gemini-pro-vision model
    model = genai.GenerativeModel('gemini-pro-vision')
    response = model.generate_content(prompt)
    return response

def main():
    st.set_page_config(page_title="PDF Image Extractor")
    st.title("PDF Image Extractor with Gemini")

    pdf_files = [file for file in os.listdir() if file.endswith(".pdf")]
    if not pdf_files:
        st.warning("No PDF file found in the current directory.")
        return

    pdf_filename = pdf_files[0]  # Assuming only one PDF file is present
    images_data = extract_images_from_pdf(pdf_filename)

    if not images_data:
        st.warning("No images found in the PDF.")
        return

    st.write("Click the button below to fetch the list of images from the PDF.")
    if st.button("Fetch Image List"):
        st.write("List of images in the PDF:")
        for image_data in images_data:
            st.write(image_data["Image Name"])

        prompt = st.text_input("Enter text to find similar image:", "")

        if st.button("Show Similar Image"):
            # Filter images based on prompt
            similar_images_data = [image_data for image_data in images_data if prompt.lower() in image_data["Image Name"].lower()]
            if similar_images_data:
                st.write("Found images similar to the provided text:")
                for image_data in similar_images_data:
                    st.write(image_data["Image Name"])
            else:
                st.warning("No similar images found for the provided text.")

            # Get Gemini response
            gemini_response = get_gemini_response(prompt)
            st.write("Gemini Response:")
            st.write(gemini_response)

if __name__ == "__main__":
    main()
