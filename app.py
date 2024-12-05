import os
import cv2
import streamlit as st
from skimage.metrics import structural_similarity as ssim
from PIL import Image
import numpy as np

THRESHOLD = 80

# Initialize the signature_dict in session state if it doesn't exist
if 'signature_dict' not in st.session_state:
    st.session_state.signature_dict = {}

def match(image1, image2):
    """
    Compare two images and calculate their similarity using Structural Similarity Index (SSIM).
    """
    # Convert images to grayscale
    img1_gray = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    img2_gray = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

    # Resize images for comparison
    img1_resized = cv2.resize(img1_gray, (300, 300))
    img2_resized = cv2.resize(img2_gray, (300, 300))

    # Calculate SSIM similarity
    similarity_value = ssim(img1_resized, img2_resized) * 100
    similarity_value = round(similarity_value, 2)

    return similarity_value, img1_gray, img2_gray, img1_resized, img2_resized

def check_similarity(image1, image2):
    """Compare the similarity between two signatures."""
    similarity, img1_gray, img2_gray, img1_resized, img2_resized = match(image1, image2)
    if similarity <= THRESHOLD:
        return f"Failure: Signatures Do Not Match. They are {similarity}% similar!", similarity, img1_gray, img2_gray, img1_resized, img2_resized
    else:
        return f"Success: Signatures Match! They are {similarity}% similar!", similarity, img1_gray, img2_gray, img1_resized, img2_resized

# Streamlit Page Setup
st.title("IPCV Project - Signature Matching Tool")

# Create Tabs
tabs = st.sidebar.radio("Select Tab", ["Upload", "Compare"])

if tabs == "Upload":
    # Upload Tab - where users upload their signatures with names
    st.subheader("Upload Signature with Name")
    sig_name = st.text_input("Enter Name for Signature", key="sig_name")
    sig_file = st.file_uploader("Upload Signature", type=["jpg", "png", "jpeg"], key="sig_upload")

    if sig_file and sig_name:
        # Save the uploaded signature and map it to the given name
        sig_image = np.array(Image.open(sig_file))
        st.session_state.signature_dict[sig_name] = sig_image  # Store in session state

        # Display the uploaded signature
        st.image(sig_image, caption=f"Signature: {sig_name}", width=300)
        st.success(f"Signature uploaded successfully under the name '{sig_name}'!")

    else:
        st.info("Please provide both name and signature file to upload.")

elif tabs == "Compare":
    # Compare Tab - where users can select a name and upload another signature to compare
    st.subheader("Compare Signatures")

    if len(st.session_state.signature_dict) == 0:
        st.warning("No signatures available. Please upload signatures first in the 'Upload' tab.")
    else:
        # Step 1: Select Signature 1 by Name for Comparison
        selected_name = st.selectbox("Select Name for Signature 1", list(st.session_state.signature_dict.keys()))

        # Step 2: Upload Signature 2 to Compare
        sig2_file = st.file_uploader("Upload Signature 2", type=["jpg", "png", "jpeg"], key="sig2_upload")

        if sig2_file:
            # Load Signature 2
            sig2_image = np.array(Image.open(sig2_file))

            # Display Signature 2
            st.image(sig2_image, caption="Signature 2", width=300)

            # Convert the first selected signature and the uploaded second signature to BGR for OpenCV
            sig1_bgr = cv2.cvtColor(st.session_state.signature_dict[selected_name], cv2.COLOR_RGB2BGR)
            sig2_bgr = cv2.cvtColor(sig2_image, cv2.COLOR_RGB2BGR)

            # Compare the two signatures when button is clicked
            if st.button("Compare Signatures"):
                result_message, similarity, img1_gray, img2_gray, img1_resized, img2_resized = check_similarity(sig1_bgr, sig2_bgr)
                st.write(f"**Result:** {result_message}")

                # Display similarity result in color-coded boxes
                if similarity >= 80:
                    st.markdown(
                        f'<div style="background-color:green; padding:10px; border-radius:5px; color:white; text-align:center;">Similarity: {similarity}%</div>', 
                        unsafe_allow_html=True
                    )
                elif 50 <= similarity < 80:
                    st.markdown(
                        f'<div style="background-color:yellow; padding:10px; border-radius:5px; color:black; text-align:center;">Similarity: {similarity}%</div>', 
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f'<div style="background-color:red; padding:10px; border-radius:5px; color:white; text-align:center;">Similarity: {similarity}%</div>', 
                        unsafe_allow_html=True
                    )
                
                # Stepwise images: Original, Grayscale, Resized, Overlapped
                st.subheader("Stepwise Comparison:")
                
                # Original Images
                st.markdown("### Original Signatures")
                col1, col2 = st.columns(2)
                with col1:
                    st.image(st.session_state.signature_dict[selected_name], caption="Original Signature 1", width=300)
                with col2:
                    st.image(sig2_image, caption="Original Signature 2", width=300)

                # Grayscale Images
                st.markdown("### Grayscale Images")
                col1, col2 = st.columns(2)
                with col1:
                    st.image(img1_gray, caption="Grayscale Signature 1", width=300)
                with col2:
                    st.image(img2_gray, caption="Grayscale Signature 2", width=300)

                # Resized Images
                st.markdown("### Resized Images")
                col1, col2 = st.columns(2)
                with col1:
                    st.image(img1_resized, caption="Resized Signature 1", width=300)
                with col2:
                    st.image(img2_resized, caption="Resized Signature 2", width=300)

                # Overlapped Image (overlay signature 1 on top of signature 2)
                st.markdown("### Overlapped Images")
                overlapped = cv2.addWeighted(img1_resized, 0.5, img2_resized, 0.5, 0)
                st.image(overlapped, caption="Overlapped Signatures", width=600)

        else:
            st.info("Please upload Signature 2 to compare.")

# Footer
st.markdown("---")
st.markdown("Developed by Vibhu Mishra, Priyanshu Chaturvedi & Prince Patel")
