#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import pandas as pd
import streamlit as st
import io
import base64
import tempfile

# Initialize session state
state = st.session_state

# Function to create a download link for a file
def get_binary_file_downloader_html(file_path, file_label):
    with open(file_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    return '<a href="data:application/octet-stream;base64,{}" download="{}">Click here to download {}</a>'.format(b64, file_label, file_label)

# Function to clean and preprocess the data
def preprocess_data(df, offer_id_column, barcode_column):
    df[offer_id_column] = df[offer_id_column].str.strip().replace('\s+', ' ', regex=True)
    df[barcode_column] = df[barcode_column].apply(lambda x: '{:.0f}'.format(x).zfill(14) if pd.notna(x) else '')
    df_unique = df.drop_duplicates(subset=[offer_id_column, barcode_column])
    new_df = df_unique.groupby(offer_id_column)[barcode_column].apply(lambda x: ','.join(x)).reset_index()
    return new_df

# Set wider layout
st.set_page_config(layout="wide")

# Workaround for wide layout
st.markdown("""
    <style>
        .reportview-container {
            display: flex;
            flex-direction: column; /* Align content in a vertical column */
            align-items: center; /* Center content horizontally */
            width: 100%;
        }
        .logo-container {
            display: flex;
            justify-content: space-between; /* Space between logos */
            align-items: center; /* Center logos vertically */
            margin: 10px 0; /* Add margin on the top */
        }
        .logo-container img {
            max-height: 100px; /* Set the maximum height of the logo */
            width: auto; /* Allow the width to adjust accordingly */
            margin: 0 10px; /* Adjust margin on both sides */
        }
        .top-left-logo {
            order: 1; /* Order the logo to be the first in the container (top-left corner) */
        }
        .top-right-logo {
            order: 2; /* Order the logo to be the second in the container (top-right corner) */
        }
        div.stButton > button {
            background-color: #4CAF50 !important;
            color: white !important;
            padding: 10px 20px !important;
            font-size: 16px !important;
            cursor: pointer !important;
        }
    </style>
""", unsafe_allow_html=True)

# Logo container for "digitaledition"
st.markdown('<div class="logo-container">'
            '<div class="top-left-logo"><img src="https://www.digitaledition.net/themes/custom/epublications/digicomlogo.png" alt="Digital Edition Logo"></div>'
            '<div class="top-right-logo"><img src="https://www.digitaledition.net/themes/custom/epublications/digicomlogo.png" alt="Digital Edition Logo"></div>'
            '</div>', unsafe_allow_html=True)

# Set the title with reduced font size
st.markdown("<h1 style='font-size:1.5em;'>Our Clients</h1>", unsafe_allow_html=True)

# List of logos with their URLs
logos = {
    'United Supermarkets': 'https://www.unitedsupermarkets.com/Themes/United5/Content/Images/Default-Logo.png',
    'MarketStreet': 'https://www.marketstreetunited.com/Themes/MarketStreetUnited5/Content/Images/Default-Logo.png',
    'Albertsons Market': 'https://www.albertsonsmarket.com/Themes/AlbertsonsMarket5/Content/Images/Default-Logo.png',
    'Amigos': 'https://www.amigosunited.com/Themes/Amigos5/Content/Images/Default-Logo.png',
}

# Display logos side by side horizontally
logo_html = '<div class="logo-container">'
for logo, url in logos.items():
    logo_html += '<img src="{}" alt="{}">'.format(url, logo)
logo_html += '</div>'

# Render logos using HTML
st.markdown(logo_html, unsafe_allow_html=True)

# Streamlit app
st.title('UPC Concatenation App')

# File upload section with hidden default uploader
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "xls"], key="fileuploader", accept_multiple_files=False)

# User input for column names
st.markdown("<div style='font-family: Times New Roman, sans-serif; font-size: 16px;'><b>Enter the column name in which title is given in your dataset:</b></div>", unsafe_allow_html=True)
offer_id_column = st.text_input("", key="offer_id_column")

st.markdown("<div style='font-family: Times New Roman, sans-serif; font-size: 16px;'><b>Enter the column name in which UPC code is given in your dataset:</b></div>", unsafe_allow_html=True)
barcode_column = st.text_input("", key="barcode_column")

# Placeholder for user-specified file name
st.markdown("<div style='font-family: Times New Roman, sans-serif; font-size: 16px;'><b>Enter the desired file name (without extension):</b></div>", unsafe_allow_html=True)
file_name_placeholder = st.text_input("", key="file_name_input")

if st.button("Click to Process Data"):
    state.download_clicked = True
    if uploaded_file is not None and offer_id_column and barcode_column and file_name_placeholder:
        try:
            # Load data from Excel
            df = pd.read_excel(uploaded_file)

            # Clean and preprocess the data
            df_processed = preprocess_data(df, offer_id_column, barcode_column)

            # Display processed data
            st.dataframe(df_processed)

            # Create an in-memory Excel file
            excel_data = io.BytesIO()
            df_processed.to_excel(excel_data, index=False, engine='openpyxl')

            # Save the Excel file to a temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_file_path = os.path.join(temp_dir, "{}.xlsx".format(file_name_placeholder.strip()))
                with open(temp_file_path, "wb") as f:
                    f.write(excel_data.getvalue())

                # Provide a message to the user
                st.write("File '{}.xlsx' has been created.".format(file_name_placeholder.strip()))

                # Provide a download link
                st.markdown(get_binary_file_downloader_html(temp_file_path, "{}.xlsx".format(file_name_placeholder.strip())), unsafe_allow_html=True)

           # After successful data processing, display confetti animation
            st.success("Data processed successfully! 🎉")

        except Exception as e:
            st.warning("Please provide valid input for all fields. ⚠️")
            
#Copyright statement at the lower bottom with center alignment
st.markdown("<br><br><br><br><br><br><hr><p style='text-align:center; font-size:0.8em;'><strong>© 2024 Redpepper Digital. All rights reserved.</strong></p>", unsafe_allow_html=True)

# In[ ]:




