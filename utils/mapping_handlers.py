import pandas as pd
import re
from typing import Dict, List

class HeaderMapper:
    def __init__(self, data: pd.DataFrame, mapping: Dict[str, str]):
        self.data = data
        self.mapping = mapping

    def _clean_phone_number(self, value) -> str:
        """Clean phone number by removing spaces, commas, and other formatting"""
        if pd.isna(value):
            return ""
        # Convert to string if it's not already
        value = str(value)
        # Remove any non-digit characters except + (for country code)
        cleaned = re.sub(r'[^\d+]', '', value)
        # Ensure + is only at the start if present
        if '+' in cleaned and not cleaned.startswith('+'):
            cleaned = cleaned.replace('+', '')
        return cleaned

    def _format_value(self, value) -> str:
        """Format any value as a clean string without commas"""
        if pd.isna(value):
            return ""
        
        # Convert to string
        value_str = str(value)
        
        # If it's a number (contains only digits, decimal point, or negative sign)
        if re.match(r'^-?\d*\.?\d+$', value_str):
            # Remove any decimal if it's .0
            if value_str.endswith('.0'):
                value_str = value_str[:-2]
            # Ensure no scientific notation
            try:
                value_str = str(int(float(value_str)))
            except ValueError:
                pass
        
        return value_str.strip()

    def transform_data(self) -> pd.DataFrame:
        """Transform data according to header mapping"""
        if self.data is None:
            raise ValueError("No data loaded!")
        
        if not self.mapping:
            raise ValueError("No mapping defined!")

        # Create new DataFrame with mapped headers
        new_data = pd.DataFrame()
        
        # Phone number column names (add more variations as needed)
        phone_columns = ['phone', 'mobile', 'contact', 'cell', 'telephone', 
                        'phone number', 'mobile number', 'contact number',
                        'cell number', 'tel']
        
        # Apply mapping
        for source_header, template_header in self.mapping.items():
            if template_header != "Ignore" and source_header in self.data.columns:
                # Check if this is a phone number column
                if any(phone_term in template_header.lower() for phone_term in phone_columns):
                    # Clean phone numbers
                    new_data[template_header] = self.data[source_header].apply(self._clean_phone_number)
                else:
                    # For other columns, format as clean strings
                    new_data[template_header] = self.data[source_header].apply(self._format_value)

        return new_data

    def validate_mapping(self, required_headers: List[str]) -> bool:
        """Validate if all required headers are mapped"""
        mapped_headers = set(self.mapping.values())
        required_headers = set(required_headers)
        return required_headers.issubset(mapped_headers)

    def get_missing_headers(self, required_headers: List[str]) -> List[str]:
        """Get list of required headers that are not mapped"""
        mapped_headers = set(self.mapping.values())
        required_headers = set(required_headers)
        return list(required_headers - mapped_headers)
