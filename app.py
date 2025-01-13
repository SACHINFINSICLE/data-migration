import streamlit as st
import pandas as pd
import json
import os
from pathlib import Path
from utils.file_handlers import ExcelHandler
from utils.mapping_handlers import HeaderMapper
from utils.header_mapper_ui import HeaderMapperUI
from utils.value_mapper_ui import ValueMapperUI
from utils.value_mapping_handler import ValueMappingHandler
from utils.config import template_config
from streamlit_option_menu import option_menu

def get_base_path():
    """Get the base path for the application"""
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle
        return Path(sys._MEIPASS)
    else:
        # If the application is run from a Python interpreter
        return Path(os.path.dirname(os.path.abspath(__file__)))

def ensure_directories():
    """Ensure required directories exist"""
    dirs = ['mappings', 'output']
    for dir_name in dirs:
        os.makedirs(dir_name, exist_ok=True)

# Initialize directories
ensure_directories()

# Set page config
st.set_page_config(
    page_title="ScholarCred Data Migration",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Add custom CSS for better desktop appearance
st.markdown("""
    <style>
        .stApp {
            margin: 0 2rem;
        }
        .main-header {
            text-align: center;
            margin-bottom: 2rem;
            padding: 1rem;
            color: #0F52BA;
        }
        .stButton>button {
            width: 100%;
        }
        .upload-section {
            background-color: #f8f9fa;
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 1rem;
        }
        .upload-header {
            color: #0F52BA;
            margin-bottom: 1rem;
        }
        .preview-section {
            margin-top: 1rem;
            padding: 1rem;
            border: 1px solid #e0e0e0;
            border-radius: 5px;
        }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'mapping' not in st.session_state:
    st.session_state.mapping = {}
if 'data' not in st.session_state:
    st.session_state.data = None
if 'source_headers' not in st.session_state:
    st.session_state.source_headers = []
if 'template_loaded' not in st.session_state:
    st.session_state.template_loaded = False
if 'template_data' not in st.session_state:
    st.session_state.template_data = None
if 'customer_data' not in st.session_state:
    st.session_state.customer_data = None

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

def map_headers():
    """Map headers between customer data and template"""
    st.markdown("## Header Mapping")
    
    if 'template_data' not in st.session_state or 'customer_data' not in st.session_state:
        st.warning("Please upload both template and customer files first.")
        return
    
    # Initialize the header mapper UI
    header_mapper_ui = HeaderMapperUI()
    
    # Get the headers
    customer_headers = list(st.session_state.customer_data.columns)
    template_headers = list(st.session_state.template_data.columns)
    
    # Create mapping interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Render the visual mapping interface
        header_mapper_ui.render_mapping_interface(
            customer_headers=customer_headers,
            template_headers=template_headers,
            required_headers=template_config.required_headers,
            current_mapping=st.session_state.mapping,
            customer_data=st.session_state.customer_data
        )
    
    with col2:
        st.markdown("### Create Mapping")
        # Dropdown for customer headers
        customer_header = st.selectbox(
            "Select Customer Header",
            options=[""] + customer_headers
        )
        
        # Dropdown for template headers
        template_header = st.selectbox(
            "Select Template Header",
            options=["Ignore"] + template_headers
        )
        
        # Map button
        if st.button("Map Headers"):
            if customer_header and template_header != "Ignore":
                st.session_state.mapping[customer_header] = template_header
                st.rerun()
        
        # Clear mapping button
        if st.button("Clear All Mappings"):
            st.session_state.mapping = {}
            st.rerun()
        
        # Show current mappings
        st.markdown("### Current Mappings")
        st.json(st.session_state.mapping)
        
        # Validate mappings
        if st.session_state.mapping:
            mapper = HeaderMapper(st.session_state.customer_data, st.session_state.mapping)
            if not mapper.validate_mapping(template_config.required_headers):
                missing = mapper.get_missing_headers(template_config.required_headers)
                st.error(f"Missing required headers: {', '.join(missing)}")
            else:
                st.success("All required headers are mapped!")

def main():
    # Main title with custom styling
    st.markdown('<h1 class="main-header">ScholarCred Data Migration System</h1>', unsafe_allow_html=True)
    
    # Navigation menu
    selected = option_menu(
        menu_title=None,
        options=["Upload", "Map Headers", "Map Values", "Transform"],
        icons=["cloud-upload", "arrow-left-right", "list-task", "arrow-repeat"],
        orientation="horizontal",
    )

    if selected == "Upload":
        # Create two columns for upload sections
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="upload-section">', unsafe_allow_html=True)
            st.markdown('<h3 class="upload-header">Upload Template Excel File</h3>', unsafe_allow_html=True)
            template_file = st.file_uploader("Choose your template Excel file", type=['xlsx', 'xls'], key='template')
            if template_file:
                try:
                    excel_handler = ExcelHandler()
                    st.session_state.template_data = excel_handler.read_file(template_file)
                    st.success("✓ Template file loaded successfully!")
                    
                    # Preview template in an expander
                    with st.expander("View Template Data"):
                        st.markdown('<div class="preview-section">', unsafe_allow_html=True)
                        st.write("**Template Headers:**", ", ".join(st.session_state.template_data.columns))
                        st.dataframe(st.session_state.template_data.head(), use_container_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error reading template file: {str(e)}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="upload-section">', unsafe_allow_html=True)
            st.markdown('<h3 class="upload-header">Upload Customer Excel File</h3>', unsafe_allow_html=True)
            uploaded_file = st.file_uploader("Choose customer's Excel file", type=['xlsx', 'xls'], key='customer')
            if uploaded_file:
                try:
                    excel_handler = ExcelHandler()
                    st.session_state.customer_data = excel_handler.read_file(uploaded_file)
                    st.success("✓ Customer file loaded successfully!")
                    
                    # Preview the data in an expander
                    with st.expander("View Customer Data"):
                        st.markdown('<div class="preview-section">', unsafe_allow_html=True)
                        st.write("**Customer Headers:**", ", ".join(st.session_state.customer_data.columns))
                        st.dataframe(st.session_state.customer_data.head(), use_container_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error reading customer file: {str(e)}")
            st.markdown('</div>', unsafe_allow_html=True)

        # Add instructions at the bottom
        if not template_file or not uploaded_file:
            st.info("👆 Please upload both template and customer Excel files to proceed with the mapping process.")

    elif selected == "Map Headers":
        map_headers()

    elif selected == "Map Values":
        st.header("Map Values")
        
        if 'template_data' not in st.session_state or st.session_state.template_data is None:
            st.warning("Please upload a template Excel file first!")
            return

        if 'customer_data' not in st.session_state or st.session_state.customer_data is None:
            st.warning("Please upload a customer Excel file first!")
            return

        if not st.session_state.mapping:
            st.warning("Please map headers first!")
            return
            
        # Initialize and render value mapping interface
        value_mapper_ui = ValueMapperUI()
        value_mapper_ui.render_value_mapping_interface(
            customer_data=st.session_state.customer_data,
            template_data=st.session_state.template_data,
            header_mapping=st.session_state.mapping
        )

    elif selected == "Transform":
        st.header("Transform Data")
        
        if st.session_state.template_data is None:
            st.warning("Please upload a template Excel file first!")
            return

        if 'customer_data' not in st.session_state or st.session_state.customer_data is None:
            st.warning("Please upload a customer Excel file first!")
            return

        if not st.session_state.mapping:
            st.warning("Please map headers first!")
            return

        try:
            # First apply header mapping
            mapper = HeaderMapper(st.session_state.customer_data, st.session_state.mapping)
            header_transformed_data = mapper.transform_data()
            
            # Then apply value mapping if available
            value_mapper = ValueMappingHandler()
            transformed_data = value_mapper.transform_values(header_transformed_data, st.session_state.mapping)
            
            st.subheader("Preview Transformed Data")
            st.dataframe(transformed_data.head(10))
            
            # Download button
            if not transformed_data.empty:
                excel_handler = ExcelHandler()
                excel_data = excel_handler.save_to_excel(transformed_data)
                
                st.download_button(
                    label="📥 Download Transformed Excel",
                    data=excel_data,
                    file_name="transformed_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
                
                # Show statistics
                st.subheader("Transformation Statistics")
                st.write(f"Total rows: {len(transformed_data)}")
                st.write(f"Total columns: {len(transformed_data.columns)}")
                
        except Exception as e:
            st.error(f"Error during transformation: {str(e)}")

if __name__ == "__main__":
    main()
