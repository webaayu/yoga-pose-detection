import os
import streamlit as st
from PIL import Image
import google.generativeai as genai
import base64
import io
from unstructured.partition.pdf import partition_pdf
#from peft import PeftModel, PeftConfig
#from transformers import AutoModelForCausalLM
#config = PeftConfig.from_pretrained("sshh12/Mistral-7B-LoRA-Multi-VisionCLIPPool-LLAVA")
#model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1")
#model = PeftModel.from_pretrained(model, "sshh12/Mistral-7B-LoRA-Multi-VisionCLIPPool-LLAVA")

st.title("Yoga Pose Image Extractor")
st.markdown("Upload a PDF file containing images of yoga poses.")

# Configure Google GenerativeAI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to get response from Gemini model
def get_gemini_response(input, image, prompt):
    model = genai.GenerativeModel('gemini-pro-vision')
    response = model.generate_content([input, image[0], prompt])
    return response.text

# Function to convert image to base64 string
def image2base64(image_path):
    with Image.open(image_path) as image:
        buffer = io.BytesIO()
        image.save(buffer, format=image.format)
        image_str = base64.b64encode(buffer.getvalue())
        return image_str.decode("utf-8")

# Function to extract images from PDF and get descriptions
def extract_images_and_descriptions(pdf_file):
    # Save the file to a temporary directory
    with open("temp.pdf", "wb") as f:
        f.write(pdf_file.read())
    
    # Partition PDF and extract images
    try:
        partitioned_pdf = partition_pdf(
            filename="temp.pdf",
            extract_images_in_pdf=True,
            infer_table_structure=True,
            chunking_strategy="by_title",
            max_characters=4000,
            new_after_n_chars=3800,
            combine_text_under_n_chars=2000
        )
        images = partitioned_pdf.images
        
        descriptions = []
        for image in images:
            image_str = image2base64(image)
            response = get_gemini_response("how LLM model behave like", [image], "please give a summary of the image provided")
            descriptions.append(response)
        
        return images, descriptions
    
    except AttributeError:
        st.warning("No images found in the PDF")
        return None, None

# Main Streamlit app
uploaded_file = st.file_uploader("Upload PDF", type="pdf")

if uploaded_file is not None:
    images, descriptions = extract_images_and_descriptions(uploaded_file)
    
    if images:
        st.success(f"Extracted {len(images)} images from PDF")
        
        for i in range(len(images)):
            st.image(images[i], caption=f"Yoga Pose {i+1}")
            st.write(f"Description: {descriptions[i]}")
