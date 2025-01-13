import streamlit as st
from typing import Dict, List, Optional
import pandas as pd
from utils.value_mapping_handler import ValueMappingHandler

class ValueMapperUI:
    def __init__(self):
        self.value_mapper = ValueMappingHandler()
        if 'value_mapper_loaded' not in st.session_state:
            self.value_mapper.load_mappings()
            st.session_state.value_mapper_loaded = True
        
    def _get_value_color(self, value: str, mappings: Dict[str, str], is_template: bool = False) -> str:
        """Get color for value based on mapping status"""
        if is_template:
            return "#66bb6a" if value in mappings.values() else "#e0e0e0"
        else:
            return "#66bb6a" if value in mappings else "#e0e0e0"
    
    def render_value_mapping_interface(self, 
                                     customer_data: pd.DataFrame,
                                     template_data: pd.DataFrame,
                                     header_mapping: Dict[str, str]):
        """Render the value mapping interface"""
        st.markdown("## Value Mapping")
        
        # Load saved mappings
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("Load Saved Value Mappings", use_container_width=True):
                if self.value_mapper.load_mappings():
                    st.success("Value mappings loaded successfully!")
                    st.rerun()
                else:
                    st.info("No saved value mappings found.")

        # Get mapping status for each column
        column_mapping_status = {}
        for col in header_mapping.keys():
            mappings = self.value_mapper.get_value_mappings(col)
            column_mapping_status[col] = bool(mappings)

        # Create column selection with visual indicators
        st.markdown("### Select Column for Value Mapping")
        
        # Create a container for column buttons
        columns_container = st.container()
        
        # Create rows of 3 columns each
        column_list = list(header_mapping.keys())
        num_columns = 3
        
        for i in range(0, len(column_list), num_columns):
            cols = columns_container.columns(num_columns)
            for j, col in enumerate(column_list[i:i + num_columns]):
                is_mapped = column_mapping_status[col]
                with cols[j]:
                    # Create a styled button with background color
                    button_style = "primary" if is_mapped else "secondary"
                    if st.button(
                        f"{col} {'✓' if is_mapped else ''}",
                        key=f"col_{col}",
                        help=f"{'✓ Has value mappings' if is_mapped else '× No value mappings'}",
                        type=button_style,
                        use_container_width=True,
                    ):
                        st.session_state.selected_value_column = col
                        st.rerun()
                        
        # Get selected column from session state
        selected_column = st.session_state.get('selected_value_column', None)
        
        if selected_column:
            template_column = header_mapping[selected_column]
            
            st.markdown("---")
            
            # Get unique values
            source_values = self.value_mapper.get_unique_values(customer_data, selected_column)
            target_values = self.value_mapper.get_unique_values(template_data, template_column)
            
            # Show current mappings
            current_mappings = self.value_mapper.get_value_mappings(selected_column)
            
            # Create three equal columns for the mapping interface
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"### Customer Values")
                st.caption(f"Column: {selected_column}")
                for value in source_values:
                    color = self._get_value_color(value, current_mappings)
                    mapped_to = current_mappings.get(value, "")
                    
                    # Create a container for each value with background color
                    with st.container():
                        st.markdown(
                            f"""
                            <div style="
                                background-color: {color};
                                padding: 10px;
                                border-radius: 5px;
                                margin: 5px 0;
                            ">
                                <span>{value}</span>
                                {f'→ {mapped_to}' if mapped_to else ''}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
            
            with col2:
                st.markdown(f"### Template Values")
                st.caption(f"Column: {template_column}")
                for value in target_values:
                    color = self._get_value_color(value, current_mappings, True)
                    
                    # Create a container for each value with background color
                    with st.container():
                        st.markdown(
                            f"""
                            <div style="
                                background-color: {color};
                                padding: 10px;
                                border-radius: 5px;
                                margin: 5px 0;
                            ">
                                <span>{value}</span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

            with col3:
                st.markdown("### Create Mapping")
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Only show unmapped source values
                unmapped_values = [v for v in source_values if v not in current_mappings]
                source_value = st.selectbox(
                    "Customer Value",
                    options=[""] + unmapped_values,
                    key="source_select"
                )
                
                st.markdown("<br>", unsafe_allow_html=True)
                target_value = st.selectbox(
                    "Template Value",
                    options=[""] + target_values,
                    key="target_select"
                )
                
                st.markdown("<br>", unsafe_allow_html=True)
                add_mapping = st.button("➡️ Map", use_container_width=True)
                
                if add_mapping and source_value and target_value:
                    if self.value_mapper.add_value_mapping(selected_column, source_value, target_value):
                        st.success(f"✓ Mapped '{source_value}' to '{target_value}'")
                        # Force a rerun to update the UI
                        st.rerun()
                    else:
                        st.error("Failed to create mapping")
                elif add_mapping:
                    st.warning("Please select both values")
                
                # Save/Clear buttons
                st.markdown("<br>" * 2, unsafe_allow_html=True)
                if st.button("💾 Save", help="Save all mappings", use_container_width=True):
                    if self.value_mapper.save_mappings():
                        st.success("✓ Saved!")
                    else:
                        st.error("Failed to save mappings")
                
                if current_mappings:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("🗑️ Clear", help="Clear mappings for this column", use_container_width=True):
                        if self.value_mapper.clear_value_mappings(selected_column):
                            st.success("✓ Cleared!")
                            # Force a rerun to update the UI
                            st.rerun()
                        else:
                            st.error("Failed to clear mappings")
            
            # Preview section
            if current_mappings:
                st.markdown("### Live Data Preview")
                preview_data = customer_data[[selected_column]].head()
                transformed_data = self.value_mapper.transform_values(preview_data)
                st.dataframe(transformed_data, use_container_width=True)
                st.caption("Preview shows first 5 rows with current mapping applied")
            else:
                st.info("Start mapping values to see data preview")
            
            # Legend
            st.markdown("""
            ### Legend
            - 🟩 Green: Mapped value
            - ⚪ Grey: Unmapped value
            """)
