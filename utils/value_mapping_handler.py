import pandas as pd
from typing import Dict, List, Optional
import json
from pathlib import Path

class ValueMappingHandler:
    def __init__(self):
        self.value_mappings: Dict[str, Dict[str, str]] = {}
        self.mapping_file = "config/value_mappings.json"
        self.load_mappings()  # Always load mappings on initialization
        
    def add_value_mapping(self, column: str, source_value: str, target_value: str) -> bool:
        """Add a value mapping for a specific column"""
        try:
            if column not in self.value_mappings:
                self.value_mappings[column] = {}
            self.value_mappings[column][str(source_value)] = str(target_value)
            self.save_mappings()  # Auto-save after adding mapping
            return True
        except Exception as e:
            print(f"Error adding value mapping: {str(e)}")
            return False
        
    def remove_value_mapping(self, column: str, source_value: str) -> bool:
        """Remove a value mapping for a specific column"""
        try:
            if column in self.value_mappings and str(source_value) in self.value_mappings[column]:
                del self.value_mappings[column][str(source_value)]
                if not self.value_mappings[column]:
                    del self.value_mappings[column]
                self.save_mappings()  # Auto-save after removing mapping
                return True
            return False
        except Exception as e:
            print(f"Error removing value mapping: {str(e)}")
            return False
                
    def get_value_mappings(self, column: str) -> Dict[str, str]:
        """Get all value mappings for a specific column"""
        return self.value_mappings.get(str(column), {})
    
    def get_all_value_mappings(self) -> Dict[str, Dict[str, str]]:
        """Get all value mappings"""
        return self.value_mappings
    
    def clear_value_mappings(self, column: Optional[str] = None) -> bool:
        """Clear value mappings for a specific column or all columns"""
        try:
            if column:
                if str(column) in self.value_mappings:
                    del self.value_mappings[str(column)]
            else:
                self.value_mappings.clear()
            self.save_mappings()  # Auto-save after clearing
            return True
        except Exception as e:
            print(f"Error clearing value mappings: {str(e)}")
            return False
    
    def transform_values(self, df: pd.DataFrame, header_mapping: Optional[Dict[str, str]] = None) -> pd.DataFrame:
        """Transform values in the dataframe based on mappings"""
        try:
            df_copy = df.copy()
            
            # If header mapping is provided, we need to map the column names
            column_mapping = {}
            if header_mapping:
                for customer_col, template_col in header_mapping.items():
                    if customer_col in self.value_mappings:
                        column_mapping[template_col] = self.value_mappings[customer_col]
            else:
                column_mapping = self.value_mappings
            
            # Apply value mappings
            for column, mappings in column_mapping.items():
                if column in df_copy.columns:
                    # Convert both series and mapping values to string for comparison
                    df_copy[column] = df_copy[column].astype(str)
                    str_mappings = {str(k): str(v) for k, v in mappings.items()}
                    df_copy[column] = df_copy[column].map(str_mappings).fillna(df_copy[column])
            
            return df_copy
        except Exception as e:
            print(f"Error transforming values: {str(e)}")
            return df
    
    def save_mappings(self) -> bool:
        """Save value mappings to JSON file"""
        try:
            Path("config").mkdir(exist_ok=True)
            with open(self.mapping_file, 'w') as f:
                json.dump(self.value_mappings, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving value mappings: {str(e)}")
            return False
            
    def load_mappings(self) -> bool:
        """Load value mappings from JSON file"""
        try:
            if Path(self.mapping_file).exists():
                with open(self.mapping_file, 'r') as f:
                    loaded_mappings = json.load(f)
                    # Convert all keys and values to strings
                    self.value_mappings = {
                        str(col): {str(k): str(v) for k, v in mappings.items()}
                        for col, mappings in loaded_mappings.items()
                    }
                return True
            return False
        except Exception as e:
            print(f"Error loading value mappings: {str(e)}")
            return False
    
    def get_unique_values(self, df: pd.DataFrame, column: str) -> List[str]:
        """Get unique values for a column in the dataframe"""
        if column in df.columns:
            return sorted(df[column].astype(str).unique().tolist())
        return []
