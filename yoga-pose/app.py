import streamlit as st
import os
import io
import fitz  # PyMuPDF
from PIL import Image
import google.generativeai as genai

# Configure Google API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def extract_image_from_pdf(pdf_filename, yoga_pose):
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
                image_bytes = base_image["image"]
                image = Image.open(io.BytesIO(image_bytes))

                # Check if the image name is available
                if "image_name" in base_image:
                    image_name = base_image["image_name"]
                else:
                    image_name = f"Yoga Pose {page_num + 1}"

                # Check if the image name matches the requested yoga pose
                if yoga_pose.lower() in image_name.lower():
                    return image, image_name

        return None, None
    except Exception as e:
        st.error(f"Error extracting image from PDF: {e}")
        return None, None

def get_gemini_response(input, image, prompt):
    # Load the gemini-pro-vision model
    model = genai.GenerativeModel('gemini-pro-vision')
    response = model.generate_content([input, image, prompt])
    return response

def main():
    st.title("Yoga Pose Image Extractor with Gemini")
    st.write("Enter the name of the yoga pose you want to see.")

    yoga_pose = st.text_input("Enter yoga pose:", "")

    if st.button("Show Pose"):
        pdf_files = [file for file in os.listdir() if file.endswith(".pdf")]
        if not pdf_files:
            st.warning("No PDF file found in the current directory.")
        else:
            pdf_filename = pdf_files[0]  # Assuming only one PDF file is present
            image, image_name = extract_image_from_pdf(pdf_filename, yoga_pose)
            if image:
                st.image(image, caption=image_name)
                # Generate description using Gemini
                input_prompt = f"You are an expert in understanding yoga poses. Please provide a description for the yoga pose: {yoga_pose}"
                response = get_gemini_response(input_prompt, image, "")
                st.write(f"Description for {yoga_pose}: {response}")
            else:
                st.warning(f"No image found for the yoga pose: {yoga_pose}")

if __name__ == "__main__":
    main()
