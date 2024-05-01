import streamlit as st
import os
import io
import fitz  # PyMuPDF
from PIL import Image
import google.generativeai as genai

# Configure Google API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to extract image from PDF based on image name
def extract_image_from_pdf(pdf_filename, image_name):
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

                # Get the name of the image
                img_name = base_image.get("image_name", f"Image {page_num + 1}")

                # Check if the image name matches the requested image name
                if image_name.lower() in img_name.lower():
                    # Extract the image
                    image_bytes = base_image["image"]
                    image = Image.open(io.BytesIO(image_bytes))
                    return image, img_name

        # If image is not found, return None
        return None, None
    except Exception as e:
        st.error(f"Error extracting image from PDF: {e}")
        return None, None

# Function to get description of the yoga pose from Gemini
def get_gemini_response(input_prompt, image, prompt):
    try:
        # Load the gemini-pro-vision model
        model = genai.GenerativeModel('gemini-pro-vision')

        # Generate content using Gemini
        response = model.generate_content([input_prompt, image, prompt])
        return response
    except Exception as e:
        st.error(f"Error generating response from Gemini: {e}")
        return None

def main():
    st.set_page_config(page_title="Yoga Pose Image Extractor")
    st.title("Yoga Pose Image Extractor with Gemini")

    # Get list of PDF files in the current directory
    pdf_files = [file for file in os.listdir() if file.endswith(".pdf")]
    if not pdf_files:
        st.warning("No PDF file found in the current directory.")
        return

    # Select the first PDF file (assuming only one PDF file is present)
    pdf_filename = pdf_files[0]

    # Display input field for yoga pose
    prompt = st.text_input("Enter yoga pose:", "")

    # Display "Show Pose" button
    if st.button("Show Pose"):
        # Extract image corresponding to the entered yoga pose
        image, img_name = extract_image_from_pdf(pdf_filename, prompt)

        if image:
            # Display the image
            st.image(image, caption=img_name)

            # Generate description using Gemini
            input_prompt = f"You are an expert in understanding yoga poses. Please provide a description for the yoga pose: {prompt}"
            response = get_gemini_response(input_prompt, [image], "")
            if response:
                st.write(f"Description for {prompt}: {response}")
        else:
            st.warning(f"No image found for the yoga pose: {prompt}")

if __name__ == "__main__":
    main()
