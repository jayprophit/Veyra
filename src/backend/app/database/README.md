# Local Database System

A unified local database manager for Veyra that handles SQL databases, Excel spreadsheets, documents (PDF, PowerPoint, Word), media files (images, video, audio), and other data formats.

## Features

### 📊 Supported File Types

#### Spreadsheets & Databases
- **SQL** - SQLite databases (.db, .sqlite, .sqlite3)
- **Excel** - Microsoft Excel (.xlsx, .xls)
- **CSV** - Comma-separated values
- **ODS** - OpenDocument Spreadsheet

#### Documents
- **PDF** - Portable Document Format
- **PowerPoint** - Presentations (.pptx, .ppt)
- **Word** - Documents (.docx, .doc)
- **Text** - Plain text, Markdown, code files

#### Media
- **Images** - JPG, PNG, GIF, BMP, SVG, WebP
- **Video** - MP4, AVI, MOV, MKV, WebM
- **Audio** - MP3, WAV, FLAC

#### Data
- **JSON** - JavaScript Object Notation
- **XML** - Extensible Markup Language
- **YAML** - YAML Ain't Markup Language

## Folder Structure

```text
local_database/
├── sql/                    # SQL databases
│   └── *.db, *.sqlite
├── spreadsheets/           # Excel and CSV files
│   └── *.xlsx, *.csv
├── documents/              # PDF, PowerPoint, Word
│   └── *.pdf, *.pptx, *.docx
├── media/
│   ├── images/            # Image files
│   │   └── *.jpg, *.png
│   ├── video/             # Video files
│   │   └── *.mp4, *.mov
│   └── audio/             # Audio files
│       └── *.mp3, *.wav
├── data/
│   ├── json/              # JSON files
│   └── xml/               # XML files
├── backups/               # Automatic backups
├── temp/                  # Temporary files
└── index.db              # SQLite search index
```

## Quick Start

```python
from app.database import DatabaseManager

# Initialize database
db = DatabaseManager("./my_database")

# Add files to database
file1 = db.add_file("/path/to/data.xlsx",
                    category="financial",
                    tags=["2024", "Q1", "revenue"],
                    description="Q1 2024 financial report")

file2 = db.add_file("/path/to/report.pdf",
                    tags=["annual", "report"])

# Search files
results = db.search_files(query="financial report",
                          file_type=FileType.EXCEL)

# Query SQL database
sql_results = db.query_sql_database(file1.file_id,
                                    "SELECT * FROM revenue WHERE quarter='Q1'")

# Read Excel data
excel_data = db.read_excel_sheet(file1.file_id, sheet_name="Revenue")

# Extract document text
text = db.extract_document_text(file2.file_id)

# Generate image thumbnail
thumb_path = db.get_image_thumbnail(image_file_id, size=(300, 300))
```

## Usage Examples

### Adding Files

```python
# Add with auto-detected type
db.add_file("data.csv")

# Add to specific category
db.add_file("report.pdf", category="annual_reports")

# Add with metadata
db.add_file(
    "financial_model.xlsx",
    category="models",
    tags=["valuation", "dcf", "2024"],
    description="Company DCF valuation model"
)
```

### Searching

```python
# Simple search
results = db.search_files("revenue")

# By file type
excel_files = db.search_files(file_type=FileType.EXCEL)

# By tags
tagged = db.search_files(tags=["2024", "Q1"])

# Combined
results = db.search_files(
    query="profit",
    file_type=FileType.PDF,
    tags=["annual"]
)
```

### Working with SQL Databases

```python
# List tables
tables = db.sql_handler.get_tables(db_path)

# Execute query
results = db.query_sql_database(
    file_id,
    "SELECT * FROM trades WHERE symbol='AAPL' AND date > '2024-01-01'"
)

# Get table data
data = db.sql_handler.get_table_data(db_path, "trades", limit=100)
```

### Working with Excel

```python
# Get sheet names
sheets = db.excel_handler.get_sheet_names(file_path)

# Read specific sheet
data = db.read_excel_sheet(file_id, sheet_name="Sheet1")

# Query with filters
filtered = db.excel_handler.query_data(
    file_path,
    filters={"Category": "Revenue", "Year": 2024}
)

# Export to CSV
csv_path = db.excel_handler.export_sheet_to_csv(
    file_path, "Sheet1", "output.csv"
)

# Create new Excel
new_file = db.export_to_excel(
    data=[{"Name": "AAPL", "Price": 150.00}, {"Name": "MSFT", "Price": 300.00}],
    output_name="stock_prices"
)
```

### Working with Documents

```python
# Extract text
text = db.extract_document_text(file_id)

# Search within document
matches = db.document_handler.search_in_document(
    file_path,
    search_term="profit margin"
)

# Get document info
info = db.document_handler.get_document_info(file_path)

# Create summary
summary = db.document_handler.create_text_summary(file_id, max_length=1000)
```

### Working with Media

```python
# Get image info
meta = db.media_handler.get_image_metadata(file_path)
# Returns: format, width, height, EXIF data

# Create thumbnail
thumb = db.get_image_thumbnail(file_id, size=(200, 200))

# Convert format
converted = db.media_handler.convert_image_format(
    file_path, "PNG", "output.png"
)

# Get video info
video_meta = db.media_handler.get_video_metadata(file_path)
# Returns: duration, resolution, fps, bitrate

# Extract audio from video
audio_path = db.media_handler.extract_audio_from_video(
    video_path, "audio.mp3"
)

# Trim video
trimmed = db.media_handler.trim_video(
    video_path, start=10, end=30, output_path="clip.mp4"
)
```

## Database Statistics

```python
# Get overall stats
stats = db.get_stats()
print(f"Total files: {stats['total_files']}")
print(f"Total size: {stats['total_size_mb']} MB")
print(f"By type: {stats['by_type']}")
```

## API Integration

The database module can be used within the Veyra API:

```python
from fastapi import APIRouter, UploadFile, File
from app.database import DatabaseManager

router = APIRouter()
db = DatabaseManager()

@router.post("/database/upload")
async def upload_file(file: UploadFile = File(...)):
    # Save uploaded file temporarily
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    # Add to database
    db_file = db.add_file(temp_path, tags=["uploaded"])

    return {
        "file_id": db_file.file_id,
        "name": db_file.name,
        "type": db_file.file_type.value
    }

@router.get("/database/search")
async def search(query: str, file_type: Optional[str] = None):
    from app.database.database_manager import FileType

    ft = FileType(file_type) if file_type else None
    results = db.search_files(query=query, file_type=ft)

    return {"results": results}
```

## Dependencies

Install optional dependencies for full functionality:

```bash
# Excel/Spreadsheets
pip install openpyxl pandas

# PDF processing
pip install PyPDF2 pdfplumber PyMuPDF

# Office documents
pip install python-docx python-pptx

# Image processing
pip install Pillow

# Video processing
pip install moviepy

# Audio metadata
pip install mutagen
```

## Configuration

```python
# Custom base path
db = DatabaseManager("/path/to/custom/database")

# Access handlers directly
from app.database import SQLHandler, ExcelHandler

sql = SQLHandler("./my_sql_databases")
excel = ExcelHandler("./my_spreadsheets")
```

## Backup and Recovery

```python
# Files are automatically organized
# Database index is at: {base_path}/index.db

# Backup entire database
import shutil
shutil.copytree("./local_database", "./local_database_backup")

# Restore from backup
shutil.copytree("./local_database_backup", "./local_database")
```

