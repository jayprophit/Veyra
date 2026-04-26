"""
Local Database System
Unified interface for SQL, Excel, Documents, PDF, Images, Video, and other files
"""

from .database_manager import DatabaseManager
from .sql_handler import SQLHandler
from .excel_handler import ExcelHandler
from .document_handler import DocumentHandler
from .media_handler import MediaHandler
from .file_indexer import FileIndexer

__all__ = [
    "DatabaseManager",
    "SQLHandler",
    "ExcelHandler", 
    "DocumentHandler",
    "MediaHandler",
    "FileIndexer"
]
