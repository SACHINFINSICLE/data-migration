import streamlit as st
import pandas as pd
import json
import os
from pathlib import Path
from utils.file_handlers import ExcelHandler
from utils.mapping_handlers import HeaderMapper
from utils.config import template_config
from streamlit_option_menu import option_menu

# Set page config
st.set_page_config(
    page_title="Header Mapping Tool",
    page_icon="🔄",
    layout="wide"
)

# Initialize session state
if 'mapping' not in st.session_state:
    st.session_state.mapping = {}
if 'data' not in st.session_state:
    st.session_state.data = None
if 'source_headers' not in st.session_state:
    st.session_state.source_headers = []
if 'template_loaded' not in st.session_state:
    st.session_state.template_loaded = False

def save_mapping():
    """Save current mapping to JSON file"""
    if st.session_state.mapping:
        os.makedirs('mappings', exist_ok=True)
        with open('mappings/saved_mapping.json', 'w') as f:
            json.dump(st.session_state.mapping, f)
        st.success("Mapping saved successfully!")

def load_mapping():
    """Load saved mapping from JSON file"""
    try:
        with open('mappings/saved_mapping.json', 'r') as f:
            st.session_state.mapping = json.load(f)
        st.success("Mapping loaded successfully!")
    except FileNotFoundError:
        st.warning("No saved mapping found.")

def main():
    st.title("Header Mapping Tool 🔄")
    
    # Navigation
    selected = option_menu(
        menu_title=None,
        options=["Upload", "Map Headers", "Transform"],
        icons=["upload", "arrow-left-right", "arrow-repeat"],
        orientation="horizontal",
    )

    if selected == "Upload":
        st.header("Upload Files")
        
        # Template file upload
        st.subheader("1. Upload Template Excel File")
        template_file = st.file_uploader("Choose your template Excel file", type=['xlsx', 'xls'], key='template')
        if template_file:
            try:
                template_config.load_template(template_file)
                st.session_state.template_loaded = True
                st.success("Template file loaded successfully!")
                
                # Preview template
                st.write("Template Headers:", ", ".join(template_config.template_headers))
                with st.expander("View Template Data"):
                    st.dataframe(template_config.template_df.head())
            except Exception as e:
                st.error(f"Error reading template file: {str(e)}")
        
        # Customer file upload
        st.subheader("2. Upload Customer Excel File")
        uploaded_file = st.file_uploader("Choose customer's Excel file", type=['xlsx', 'xls'], key='customer')
        if uploaded_file:
            try:
                excel_handler = ExcelHandler()
                st.session_state.data = excel_handler.read_file(uploaded_file)
                st.session_state.source_headers = excel_handler.get_headers()
                st.success("Customer file uploaded successfully!")
                
                # Preview the data
                with st.expander("View Customer Data"):
                    st.dataframe(st.session_state.data.head())
            except Exception as e:
                st.error(f"Error reading customer file: {str(e)}")

    elif selected == "Map Headers":
        st.header("Map Headers")

        if not st.session_state.template_loaded:
            st.warning("Please upload a template Excel file first!")
            return

        if not st.session_state.source_headers:
            st.warning("Please upload a customer Excel file first!")
            return

        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Map Customer Headers to Template")
            for header in st.session_state.source_headers:
                mapping = st.selectbox(
                    label=f"Map '{header}' to:",
                    options=["Ignore"] + template_config.template_headers,
                    key=f"mapping_{header}",
                    index=0 if header not in st.session_state.mapping else 
                          (["Ignore"] + template_config.template_headers).index(st.session_state.mapping[header])
                )
                if mapping != "Ignore":
                    st.session_state.mapping[header] = mapping

        with col2:
            st.subheader("Actions")
            if st.button("Save Mapping", type="primary"):
                save_mapping()
            if st.button("Load Saved Mapping"):
                load_mapping()

            # Display current mappings
            if st.session_state.mapping:
                st.subheader("Current Mappings")
                for source, target in st.session_state.mapping.items():
                    st.write(f"{source} → {target}")

    elif selected == "Transform":
        st.header("Transform Data")

        if not st.session_state.template_loaded:
            st.warning("Please upload a template Excel file first!")
            return

        if st.session_state.data is None:
            st.warning("Please upload a customer Excel file first!")
            return

        if not st.session_state.mapping:
            st.warning("Please map headers first!")
            return

        try:
            mapper = HeaderMapper(st.session_state.data, st.session_state.mapping)
            transformed_data = mapper.transform_data()
            
            st.subheader("Preview Transformed Data")
            st.dataframe(transformed_data.head())

            # Create Excel file in memory
            from io import BytesIO
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                transformed_data.to_excel(writer, index=False)
            
            # Download button
            st.download_button(
                label="Download Transformed Data",
                data=buffer.getvalue(),
                file_name="transformed_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except Exception as e:
            st.error(f"Error transforming data: {str(e)}")

if __name__ == "__main__":
    main()
