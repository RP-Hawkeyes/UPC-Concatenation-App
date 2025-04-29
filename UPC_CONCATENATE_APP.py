#!/usr/bin/env python
# coding: utf-8

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

# Function to preprocess data
def preprocess_data(df, offer_id_column, offer_headline_column, item_name_column, barcode_column):
    # Clean the 'offer_headline_column' and 'barcode_column'
    df[offer_headline_column] = df[offer_headline_column].astype(str).str.strip().replace('\s+', ' ', regex=True)
    df[barcode_column] = df[barcode_column].apply(lambda x: '{:.0f}'.format(float(x)).zfill(14) if pd.notna(x) and str(x).strip() != '' else '')

    # Drop rows with empty barcode values
    df = df[df[barcode_column] != '']
    
    # Drop duplicates based on the specified columns
    df_unique = df.drop_duplicates(subset=[offer_id_column, offer_headline_column, barcode_column])
    
    # Group by 'offer_id_column' and 'offer_headline_column', joining barcodes as a comma-separated string, joining item names one by one
    new_df = df_unique.groupby([offer_id_column, offer_headline_column]).agg({
        barcode_column: lambda x: ','.join(x),
        item_name_column: lambda x: '\n'.join(x)
    }).reset_index()

    # Predefined custom column names for the output file
    new_df.columns = ["OFFER ID", "TITLE", "CONCATENATED FINAL UPC", "ITEM NAME"]
    
    return new_df

# Set wider layout
st.set_page_config(layout="wide")

# Styling
st.markdown("""
    <style>
        .reportview-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 100%;
        }
        .logo-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 10px 0;
        }
        .logo-container img {
            max-height: 100px;
            width: auto;
            margin: 0 10px;
        }
        .top-left-logo { order: 1; }
        .top-right-logo { order: 2; }
        div.stButton > button {
            background-color: #4CAF50 !important;
            color: white !important;
            padding: 10px 20px !important;
            font-size: 16px !important;
            cursor: pointer !important;
        }
    </style>
""", unsafe_allow_html=True)

# Logo display
st.markdown('<div class="logo-container">'
            '<div class="top-left-logo"><img src="https://www.digitaledition.net/themes/custom/epublications/digicomlogo.png" alt="Digital Edition Logo"></div>'
            '<div class="top-right-logo"><img src="https://www.digitaledition.net/themes/custom/epublications/digicomlogo.png" alt="Digital Edition Logo"></div>'
            '</div>', unsafe_allow_html=True)

# Page heading
st.markdown("<h1 style='font-size:1.5em;'>Our Clients</h1>", unsafe_allow_html=True)

# Client logos
logos = {
    'United Supermarkets': 'https://www.unitedsupermarkets.com/Themes/United5/Content/Images/Default-Logo.png',
    'MarketStreet': 'https://www.marketstreetunited.com/Themes/MarketStreetUnited5/Content/Images/Default-Logo.png',
    'Albertsons Market': 'https://www.albertsonsmarket.com/Themes/AlbertsonsMarket5/Content/Images/Default-Logo.png',
    'Amigos': 'https://www.amigosunited.com/Themes/Amigos5/Content/Images/Default-Logo.png',
}
logo_html = '<div class="logo-container">'
for logo, url in logos.items():
    logo_html += f'<img src="{url}" alt="{logo}">'
logo_html += '</div>'
st.markdown(logo_html, unsafe_allow_html=True)

# Main title
st.title('UPC Concatenation App')

# File uploader
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "xls"], key="fileuploader", accept_multiple_files=False)

# Only show column selectors if file is uploaded
if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        st.write("Columns in uploaded file:", df.columns.tolist())

        column_options = df.columns.tolist()

        # Auto-suggest column dropdowns
        offer_id_column = st.selectbox("Select the column for Offer ID", column_options, key="offer_id_column")
        offer_headline_column = st.selectbox("Select the column for Title/Headline", column_options, key="offer_headline_column")
        item_name_column = st.selectbox("Select the column for Item Name", column_options, key="item_name_column")
        barcode_column = st.selectbox("Select the column for UPC/Barcode", column_options, key="barcode_column")

        # File name input
        file_name_placeholder = st.text_input("Enter the desired file name (without extension):", key="file_name_input")

        # Process button
        if st.button("Click to Process Data"):
            state.download_clicked = True
            if offer_id_column and offer_headline_column and item_name_column and barcode_column and file_name_placeholder:
                try:
                    df_processed = preprocess_data(df, offer_id_column, offer_headline_column, item_name_column, barcode_column)

                    # Show result
                    st.dataframe(df_processed)

                    # Save processed data to Excel in memory
                    excel_data = io.BytesIO()
                    df_processed.to_excel(excel_data, index=False, engine='openpyxl')

                    # Save to temp file
                    with tempfile.TemporaryDirectory() as temp_dir:
                        temp_file_path = os.path.join(temp_dir, f"{file_name_placeholder.strip()}.xlsx")
                        with open(temp_file_path, "wb") as f:
                            f.write(excel_data.getvalue())

                        st.write(f"File '{file_name_placeholder.strip()}.xlsx' has been created.")
                        st.markdown(get_binary_file_downloader_html(temp_file_path, f"{file_name_placeholder.strip()}.xlsx"), unsafe_allow_html=True)

                    st.success("Data processed successfully! 🎉")

                except Exception as e:
                    st.warning(f"An error occurred: {e}")
            else:
                st.warning("Please provide valid input for all fields. ⚠️")

    except Exception as e:
        st.error(f"Error reading Excel file: {e}")

# Copyright
st.markdown("<br><br><br><br><br><br><hr><p style='text-align:center; font-size:0.8em;'><strong>© 2024 Redpepper Digital. All rights reserved.</strong></p>", unsafe_allow_html=True)
