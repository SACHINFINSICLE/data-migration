import pandas as pd
from pathlib import Path

class ExcelHandler:
    def __init__(self):
        self.data = None
        self.headers = []

    def read_file(self, file):
        """Read Excel file and store headers"""
        try:
            self.data = pd.read_excel(file)
            self.headers = list(self.data.columns)
            return self.data
        except Exception as e:
            raise Exception(f"Error reading Excel file: {str(e)}")

    def get_headers(self):
        """Return list of headers"""
        return self.headers

    def save_file(self, data, output_path):
        """Save DataFrame to Excel file"""
        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            data.to_excel(output_path, index=False)
        except Exception as e:
            raise Exception(f"Error saving Excel file: {str(e)}")
