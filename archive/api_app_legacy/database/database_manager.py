"""
Database Manager - Unified Local Database System
Handles SQL, Excel, Documents, PDF, Images, Video, and other files
"""

import os
import sqlite3
import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from enum import Enum
import hashlib
import mimetypes


class FileType(Enum):
    """Supported file types"""
    # Spreadsheets
    SQL = "sql"
    EXCEL = "excel"
    CSV = "csv"
    
    # Documents
    PDF = "pdf"
    POWERPOINT = "powerpoint"
    WORD = "word"
    TEXT = "text"
    
    # Media
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    
    # Data
    JSON = "json"
    XML = "xml"
    YAML = "yaml"
    
    # Other
    UNKNOWN = "unknown"


@dataclass
class DatabaseFile:
    """Represents a file in the database"""
    file_id: str
    name: str
    file_type: FileType
    path: str
    size_bytes: int
    created_at: datetime
    modified_at: datetime
    
    # Metadata
    checksum: str = ""
    tags: List[str] = field(default_factory=list)
    description: str = ""
    
    # Content preview/index
    preview: str = ""
    indexed_content: Dict = field(default_factory=dict)
    
    # Access tracking
    last_accessed: Optional[datetime] = None
    access_count: int = 0


class DatabaseManager:
    """
    Unified Local Database Manager
    
    Features:
    - SQL database operations (SQLite)
    - Excel/CSV spreadsheet handling
    - Document processing (PDF, PowerPoint, Word)
    - Media file management (Images, Video, Audio)
    - Full-text indexing and search
    - File versioning and backup
    - Cross-file querying
    """
    
    def __init__(self, base_path: str = "./local_database"):
        self.base_path = Path(base_path)
        self.db_path = self.base_path / "index.db"
        
        # Create directory structure
        self._init_directories()
        
        # Initialize SQLite index
        self._init_database()
        
        # Import handlers
        from .sql_handler import SQLHandler
        from .excel_handler import ExcelHandler
        from .document_handler import DocumentHandler
        from .media_handler import MediaHandler
        from .file_indexer import FileIndexer
        
        self.sql_handler = SQLHandler(self.base_path / "sql")
        self.excel_handler = ExcelHandler(self.base_path / "spreadsheets")
        self.document_handler = DocumentHandler(self.base_path / "documents")
        self.media_handler = MediaHandler(self.base_path / "media")
        self.file_indexer = FileIndexer(self.db_path)
    
    def _init_directories(self):
        """Create folder structure for database"""
        directories = [
            "sql",
            "spreadsheets",
            "documents",
            "media/images",
            "media/video",
            "media/audio",
            "data/json",
            "data/xml",
            "backups",
            "temp"
        ]
        
        for dir_name in directories:
            (self.base_path / dir_name).mkdir(parents=True, exist_ok=True)
    
    def _init_database(self):
        """Initialize SQLite index database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Files index table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS files (
                file_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                file_type TEXT NOT NULL,
                path TEXT NOT NULL,
                size_bytes INTEGER,
                created_at TIMESTAMP,
                modified_at TIMESTAMP,
                checksum TEXT,
                tags TEXT,
                description TEXT,
                preview TEXT,
                indexed_content TEXT,
                last_accessed TIMESTAMP,
                access_count INTEGER DEFAULT 0
            )
        """)
        
        # Search index table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_index (
                word TEXT,
                file_id TEXT,
                field TEXT,
                position INTEGER,
                FOREIGN KEY (file_id) REFERENCES files(file_id)
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_type ON files(file_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_name ON files(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_search_word ON search_index(word)")
        
        conn.commit()
        conn.close()
    
    def detect_file_type(self, file_path: str) -> FileType:
        """Detect file type from extension and content"""
        path = Path(file_path)
        ext = path.suffix.lower()
        
        type_mapping = {
            # SQL
            '.sql': FileType.SQL,
            '.db': FileType.SQL,
            '.sqlite': FileType.SQL,
            '.sqlite3': FileType.SQL,
            
            # Spreadsheets
            '.xlsx': FileType.EXCEL,
            '.xls': FileType.EXCEL,
            '.csv': FileType.CSV,
            '.ods': FileType.EXCEL,
            
            # Documents
            '.pdf': FileType.PDF,
            '.pptx': FileType.POWERPOINT,
            '.ppt': FileType.POWERPOINT,
            '.docx': FileType.WORD,
            '.doc': FileType.WORD,
            '.txt': FileType.TEXT,
            '.md': FileType.TEXT,
            
            # Media
            '.jpg': FileType.IMAGE,
            '.jpeg': FileType.IMAGE,
            '.png': FileType.IMAGE,
            '.gif': FileType.IMAGE,
            '.bmp': FileType.IMAGE,
            '.svg': FileType.IMAGE,
            '.mp4': FileType.VIDEO,
            '.avi': FileType.VIDEO,
            '.mov': FileType.VIDEO,
            '.mkv': FileType.VIDEO,
            '.mp3': FileType.AUDIO,
            '.wav': FileType.AUDIO,
            '.flac': FileType.AUDIO,
            
            # Data
            '.json': FileType.JSON,
            '.xml': FileType.XML,
            '.yaml': FileType.YAML,
            '.yml': FileType.YAML
        }
        
        return type_mapping.get(ext, FileType.UNKNOWN)
    
    def add_file(self, source_path: str, category: Optional[str] = None,
                 tags: List[str] = None, description: str = "") -> DatabaseFile:
        """
        Add a file to the database
        
        Args:
            source_path: Path to source file
            category: Optional subcategory folder
            tags: List of tags for the file
            description: File description
        """
        source = Path(source_path)
        if not source.exists():
            raise FileNotFoundError(f"File not found: {source_path}")
        
        # Detect file type
        file_type = self.detect_file_type(source_path)
        
        # Determine target directory
        target_dir = self._get_target_directory(file_type, category)
        
        # Generate unique ID and copy file
        file_id = self._generate_file_id(source)
        target_path = target_dir / f"{file_id}_{source.name}"
        
        # Copy file to database
        import shutil
        shutil.copy2(source_path, target_path)
        
        # Calculate checksum
        checksum = self._calculate_checksum(target_path)
        
        # Create database record
        db_file = DatabaseFile(
            file_id=file_id,
            name=source.name,
            file_type=file_type,
            path=str(target_path),
            size_bytes=target_path.stat().st_size,
            created_at=datetime.fromtimestamp(target_path.stat().st_ctime),
            modified_at=datetime.fromtimestamp(target_path.stat().st_mtime),
            checksum=checksum,
            tags=tags or [],
            description=description
        )
        
        # Index content based on file type
        self._index_file_content(db_file)
        
        # Save to database
        self._save_file_record(db_file)
        
        return db_file
    
    def _get_target_directory(self, file_type: FileType, category: Optional[str]) -> Path:
        """Determine target directory based on file type"""
        type_dirs = {
            FileType.SQL: "sql",
            FileType.EXCEL: "spreadsheets",
            FileType.CSV: "spreadsheets",
            FileType.PDF: "documents",
            FileType.POWERPOINT: "documents",
            FileType.WORD: "documents",
            FileType.TEXT: "documents",
            FileType.IMAGE: "media/images",
            FileType.VIDEO: "media/video",
            FileType.AUDIO: "media/audio",
            FileType.JSON: "data/json",
            FileType.XML: "data/xml",
            FileType.YAML: "data/json"
        }
        
        base_dir = type_dirs.get(file_type, "other")
        
        if category:
            target = self.base_path / base_dir / category
        else:
            target = self.base_path / base_dir
        
        target.mkdir(parents=True, exist_ok=True)
        return target
    
    def _generate_file_id(self, path: Path) -> str:
        """Generate unique file ID"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        hash_suffix = hashlib.md5(str(path).encode()).hexdigest()[:8]
        return f"{timestamp}_{hash_suffix}"
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate MD5 checksum of file"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _index_file_content(self, db_file: DatabaseFile):
        """Index file content based on type"""
        try:
            if db_file.file_type == FileType.SQL:
                content = self.sql_handler.get_schema_summary(db_file.path)
                db_file.preview = content[:500]
                db_file.indexed_content = {"schema": content}
                
            elif db_file.file_type == FileType.EXCEL:
                sheets = self.excel_handler.get_sheet_names(db_file.path)
                preview = self.excel_handler.get_preview(db_file.path)
                db_file.preview = str(preview)[:500]
                db_file.indexed_content = {"sheets": sheets, "preview": preview}
                
            elif db_file.file_type in [FileType.PDF, FileType.POWERPOINT, FileType.WORD]:
                text = self.document_handler.extract_text(db_file.path)
                db_file.preview = text[:500]
                db_file.indexed_content = {"text": text}
                
            elif db_file.file_type == FileType.IMAGE:
                meta = self.media_handler.get_image_metadata(db_file.path)
                db_file.preview = f"Image: {meta.get('width')}x{meta.get('height')}"
                db_file.indexed_content = meta
                
            elif db_file.file_type == FileType.VIDEO:
                meta = self.media_handler.get_video_metadata(db_file.path)
                db_file.preview = f"Video: {meta.get('duration')}s, {meta.get('resolution')}"
                db_file.indexed_content = meta
                
            elif db_file.file_type == FileType.JSON:
                with open(db_file.path, 'r') as f:
                    data = json.load(f)
                db_file.preview = json.dumps(data)[:500]
                db_file.indexed_content = {"data": data}
                
        except Exception as e:
            db_file.preview = f"Error indexing: {str(e)}"
    
    def _save_file_record(self, db_file: DatabaseFile):
        """Save file record to SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO files 
            (file_id, name, file_type, path, size_bytes, created_at, modified_at,
             checksum, tags, description, preview, indexed_content, access_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            db_file.file_id,
            db_file.name,
            db_file.file_type.value,
            db_file.path,
            db_file.size_bytes,
            db_file.created_at.isoformat(),
            db_file.modified_at.isoformat(),
            db_file.checksum,
            json.dumps(db_file.tags),
            db_file.description,
            db_file.preview,
            json.dumps(db_file.indexed_content),
            db_file.access_count
        ))
        
        conn.commit()
        conn.close()
        
        # Index for search
        self.file_indexer.index_file(db_file)
    
    def get_file(self, file_id: str) -> Optional[DatabaseFile]:
        """Get file by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM files WHERE file_id = ?", (file_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_file(row)
        return None
    
    def search_files(self, query: str = "", file_type: Optional[FileType] = None,
                     tags: List[str] = None) -> List[DatabaseFile]:
        """
        Search files by query, type, and tags
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        sql = "SELECT * FROM files WHERE 1=1"
        params = []
        
        if query:
            sql += " AND (name LIKE ? OR preview LIKE ? OR description LIKE ?)"
            params.extend([f"%{query}%", f"%{query}%", f"%{query}%"])
        
        if file_type:
            sql += " AND file_type = ?"
            params.append(file_type.value)
        
        sql += " ORDER BY modified_at DESC"
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_file(row) for row in rows]
    
    def _row_to_file(self, row) -> DatabaseFile:
        """Convert database row to DatabaseFile"""
        return DatabaseFile(
            file_id=row[0],
            name=row[1],
            file_type=FileType(row[2]),
            path=row[3],
            size_bytes=row[4],
            created_at=datetime.fromisoformat(row[5]),
            modified_at=datetime.fromisoformat(row[6]),
            checksum=row[7],
            tags=json.loads(row[8]) if row[8] else [],
            description=row[9] or "",
            preview=row[10] or "",
            indexed_content=json.loads(row[11]) if row[11] else {},
            last_accessed=datetime.fromisoformat(row[12]) if row[12] else None,
            access_count=row[13] or 0
        )
    
    def delete_file(self, file_id: str) -> bool:
        """Delete file from database"""
        file_info = self.get_file(file_id)
        if not file_info:
            return False
        
        # Delete physical file
        try:
            Path(file_info.path).unlink()
        except:
            pass
        
        # Delete from database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM files WHERE file_id = ?", (file_id,))
        cursor.execute("DELETE FROM search_index WHERE file_id = ?", (file_id,))
        conn.commit()
        conn.close()
        
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total files
        cursor.execute("SELECT COUNT(*) FROM files")
        total_files = cursor.fetchone()[0]
        
        # By type
        cursor.execute("SELECT file_type, COUNT(*), SUM(size_bytes) FROM files GROUP BY file_type")
        by_type = cursor.fetchall()
        
        # Total size
        cursor.execute("SELECT SUM(size_bytes) FROM files")
        total_size = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            "total_files": total_files,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "by_type": [{"type": t[0], "count": t[1], "size_mb": round(t[2] / (1024 * 1024), 2)} for t in by_type],
            "database_path": str(self.base_path)
        }
    
    # === Specialized Query Methods ===
    
    def query_sql_database(self, file_id: str, query: str) -> List[Dict]:
        """Execute SQL query on a stored SQL database file"""
        file_info = self.get_file(file_id)
        if not file_info or file_info.file_type != FileType.SQL:
            raise ValueError("Invalid SQL database file")
        
        return self.sql_handler.execute_query(file_info.path, query)
    
    def read_excel_sheet(self, file_id: str, sheet_name: Optional[str] = None) -> Dict:
        """Read Excel spreadsheet data"""
        file_info = self.get_file(file_id)
        if not file_info or file_info.file_type != FileType.EXCEL:
            raise ValueError("Invalid Excel file")
        
        return self.excel_handler.read_sheet(file_info.path, sheet_name)
    
    def extract_document_text(self, file_id: str) -> str:
        """Extract text from PDF, PowerPoint, or Word document"""
        file_info = self.get_file(file_id)
        if not file_info or file_info.file_type not in [FileType.PDF, FileType.POWERPOINT, FileType.WORD]:
            raise ValueError("Invalid document file")
        
        return self.document_handler.extract_text(file_info.path)
    
    def get_image_thumbnail(self, file_id: str, size: tuple = (200, 200)) -> str:
        """Generate image thumbnail"""
        file_info = self.get_file(file_id)
        if not file_info or file_info.file_type != FileType.IMAGE:
            raise ValueError("Invalid image file")
        
        return self.media_handler.create_thumbnail(file_info.path, size)
    
    def export_to_excel(self, data: List[Dict], output_name: str) -> str:
        """Export data to new Excel file in database"""
        output_path = self.base_path / "spreadsheets" / f"{output_name}.xlsx"
        return self.excel_handler.create_excel(data, str(output_path))
