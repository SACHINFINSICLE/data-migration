import pandas as pd
from io import BytesIO
import openpyxl

class ExcelHandler:
    def __init__(self):
        self.data = None
        
    def read_file(self, file) -> pd.DataFrame:
        """Read Excel file and convert all columns to string"""
        # Read Excel file with all columns as string
        self.data = pd.read_excel(
            file,
            dtype=str,  # Convert all columns to string
            na_filter=False  # Don't convert empty cells to NaN
        )
        
        # Clean the data
        self.data = self.data.applymap(lambda x: str(x).strip() if pd.notna(x) else '')
        
        return self.data
    
    def get_headers(self) -> list:
        """Get headers from the loaded data"""
        if self.data is None:
            return []
        return list(self.data.columns)
    
    def save_to_excel(self, df: pd.DataFrame) -> BytesIO:
        """Save DataFrame to Excel file in memory"""
        output = BytesIO()
        
        # Create Excel writer
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Convert all columns to string before saving
            df = df.astype(str)
            # Replace 'nan' with empty string
            df = df.replace('nan', '')
            # Write to Excel without index
            df.to_excel(writer, index=False, sheet_name='Sheet1')
            
            # Auto-adjust columns width
            worksheet = writer.sheets['Sheet1']
            for idx, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(str(col))
                ) + 2
                worksheet.column_dimensions[openpyxl.utils.get_column_letter(idx + 1)].width = max_length
        
        output.seek(0)
        return output
