# Template headers - customize these according to your needs
TEMPLATE_HEADERS = [
    "First Name",
    "Last Name",
    "Email",
    "Mobile Number",  # This will be handled as a phone number
    "Address",
    "City",
    "State",
    "Zip Code",
    "Country",
    "Company",
    "Job Title",
    "Department"
]

# Required headers - these must be mapped
REQUIRED_HEADERS = [
    "First Name",
    "Last Name",
    "Email",
    "Mobile Number"
]

import pandas as pd
from typing import List, Optional

class TemplateConfig:
    def __init__(self):
        self.template_headers: List[str] = TEMPLATE_HEADERS
        self.required_headers: List[str] = REQUIRED_HEADERS
        self.template_df: Optional[pd.DataFrame] = None

    def load_template(self, template_file) -> None:
        """Load template headers from Excel file"""
        self.template_df = pd.read_excel(template_file)
        self.template_headers = list(self.template_df.columns)
        # You can specify which headers are required
        self.required_headers = self.template_headers.copy()

# Initialize template configuration
template_config = TemplateConfig()
