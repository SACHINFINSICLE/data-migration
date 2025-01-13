# Header Mapping Tool

A Python-based local application for mapping headers between customer-provided data files and a predefined template. The application handles data from both local MS Excel files and Google Sheets.

## Features

- Upload data from Excel files or Google Sheets
- Interactive header mapping interface with dropdowns
- Save and load mapping configurations
- Transform data according to template headers
- Export transformed data to Excel or Google Sheets
- Modern UI with shadcn-style components

## Prerequisites

- Python 3.8+
- Google Cloud Project with Sheets API enabled (for Google Sheets functionality)

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up Google Sheets Authentication:
   - Create a service account in Google Cloud Console
   - Enable Google Sheets API and Drive API
   - Download credentials and save as `credentials/google_credentials.json`

## Project Structure

```
.
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── README.md              # Documentation
├── credentials/           # Google API credentials
│   └── google_credentials.json
├── mappings/             # Saved header mappings
│   └── saved_mapping.json
├── output/               # Transformed data output
└── utils/               # Utility modules
    ├── __init__.py
    ├── config.py        # Configuration and constants
    ├── file_handlers.py # Excel and Google Sheets handlers
    └── mapping_handlers.py # Header mapping logic
```

## Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Upload Data:
   - Choose between Excel file or Google Sheet
   - Upload file or provide sheet URL

3. Map Headers:
   - Use dropdowns to map source headers to template headers
   - Save mapping for future use

4. Transform Data:
   - Preview transformed data
   - Download as Excel or save to Google Sheets

## Customization

Edit `utils/config.py` to modify:
- Template headers
- Required headers
- Other configuration settings
