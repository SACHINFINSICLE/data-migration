import streamlit as st
from streamlit_elements import elements, dashboard, mui, html
from typing import Dict, List, Optional
import pandas as pd
from utils.mapping_handlers import HeaderMapper

class HeaderMapperUI:
    def __init__(self):
        self.customer_headers: List[str] = []
        self.template_headers: List[str] = []
        self.required_headers: List[str] = []
        self.current_mapping: Dict[str, str] = {}
        
    def _get_header_color(self, header: str, is_template: bool = False) -> str:
        """Get color for header based on mapping status"""
        if is_template:
            if header in self.required_headers:
                return "#ef5350" if header not in self.current_mapping.values() else "#66bb6a"
            return "#90caf9" if header in self.current_mapping.values() else "#e0e0e0"
        else:
            return "#66bb6a" if header in self.current_mapping else "#e0e0e0"
    
    def _get_preview_data(self, data: pd.DataFrame, mapping: Dict[str, str]) -> pd.DataFrame:
        """Get preview of transformed data based on current mapping"""
        if not mapping:
            return pd.DataFrame()
            
        try:
            mapper = HeaderMapper(data, mapping)
            preview_data = mapper.transform_data()
            return preview_data.head(5)
        except Exception as e:
            st.warning(f"Preview not available: {str(e)}")
            return pd.DataFrame()
    
    def render_mapping_interface(self, 
                               customer_headers: List[str],
                               template_headers: List[str],
                               required_headers: List[str],
                               current_mapping: Dict[str, str],
                               customer_data: pd.DataFrame):
        """Render the header mapping interface"""
        self.customer_headers = customer_headers
        self.template_headers = template_headers
        self.required_headers = required_headers
        self.current_mapping = current_mapping
        
        # Create two columns for the mapping interface
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Customer Headers")
            for header in customer_headers:
                color = self._get_header_color(header)
                mapped_to = current_mapping.get(header, "")
                
                # Create a container for each header with background color
                with st.container():
                    st.markdown(
                        f"""
                        <div style="
                            background-color: {color};
                            padding: 10px;
                            border-radius: 5px;
                            margin: 5px 0;
                        ">
                            <span>{header}</span>
                            {f'→ {mapped_to}' if mapped_to else ''}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        
        with col2:
            st.markdown("### Template Headers")
            for header in template_headers:
                color = self._get_header_color(header, True)
                is_required = header in required_headers
                
                # Create a container for each header with background color
                with st.container():
                    st.markdown(
                        f"""
                        <div style="
                            background-color: {color};
                            padding: 10px;
                            border-radius: 5px;
                            margin: 5px 0;
                            position: relative;
                        ">
                            <span>{header}</span>
                            {' (Required)' if is_required else ''}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        
        # Preview section with real-time updates
        st.markdown("### Live Data Preview")
        if current_mapping:
            preview_data = self._get_preview_data(customer_data, current_mapping)
            if not preview_data.empty:
                st.dataframe(preview_data, use_container_width=True)
                st.caption("Preview shows first 5 rows with current mapping applied")
            else:
                st.info("Complete the required mappings to see data preview")
        else:
            st.info("Start mapping headers to see data preview")
            
        # Legend
        st.markdown("""
        ### Legend
        - 🟩 Green: Mapped header
        - 🟥 Red: Required but unmapped header
        - 🔵 Blue: Optional mapped header
        - ⚪ Grey: Unmapped header
        """)
