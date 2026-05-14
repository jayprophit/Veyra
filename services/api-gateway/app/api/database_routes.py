"""
Database API Routes
REST API endpoints for the Local Database System
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import FileResponse, JSONResponse
from typing import List, Optional, Dict, Any
from pathlib import Path
import tempfile
import shutil

from app.database import DatabaseManager, FileType


router = APIRouter(prefix="/database", tags=["Database"])

# Initialize database manager
db_manager = DatabaseManager()


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    category: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    description: Optional[str] = Form(None)
):
    """
    Upload a file to the database
    
    - **file**: File to upload
    - **category**: Optional subcategory folder
    - **tags**: Comma-separated list of tags
    - **description**: File description
    """
    try:
        # Save uploaded file temporarily
        suffix = Path(file.filename).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        
        # Parse tags
        tag_list = [t.strip() for t in tags.split(",")] if tags else []
        
        # Add to database
        db_file = db_manager.add_file(
            tmp_path,
            category=category,
            tags=tag_list,
            description=description
        )
        
        # Clean up temp file
        Path(tmp_path).unlink(missing_ok=True)
        
        return {
            "success": True,
            "file_id": db_file.file_id,
            "name": db_file.name,
            "file_type": db_file.file_type.value,
            "size_bytes": db_file.size_bytes,
            "preview": db_file.preview[:200] if db_file.preview else ""
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files")
async def list_files(
    file_type: Optional[str] = Query(None, description="Filter by file type"),
    query: Optional[str] = Query(None, description="Search query"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    limit: int = Query(50, ge=1, le=1000)
):
    """
    List and search files in the database
    """
    try:
        # Parse file type
        ft = FileType(file_type) if file_type else None
        
        # Parse tags
        tag_list = [t.strip() for t in tags.split(",")] if tags else None
        
        # Search
        results = db_manager.search_files(
            query=query or "",
            file_type=ft,
            tags=tag_list
        )
        
        # Format response
        files = [
            {
                "file_id": f.file_id,
                "name": f.name,
                "file_type": f.file_type.value,
                "size_mb": round(f.size_bytes / (1024 * 1024), 2),
                "created_at": f.created_at.isoformat(),
                "modified_at": f.modified_at.isoformat(),
                "tags": f.tags,
                "description": f.description,
                "preview": f.preview[:100] if f.preview else ""
            }
            for f in results[:limit]
        ]
        
        return {
            "total": len(results),
            "returned": len(files),
            "files": files
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files/{file_id}")
async def get_file(file_id: str):
    """
    Get file details by ID
    """
    try:
        db_file = db_manager.get_file(file_id)
        
        if not db_file:
            raise HTTPException(status_code=404, detail="File not found")
        
        return {
            "file_id": db_file.file_id,
            "name": db_file.name,
            "file_type": db_file.file_type.value,
            "path": db_file.path,
            "size_bytes": db_file.size_bytes,
            "size_mb": round(db_file.size_bytes / (1024 * 1024), 2),
            "created_at": db_file.created_at.isoformat(),
            "modified_at": db_file.modified_at.isoformat(),
            "checksum": db_file.checksum,
            "tags": db_file.tags,
            "description": db_file.description,
            "preview": db_file.preview,
            "indexed_content": db_file.indexed_content,
            "access_count": db_file.access_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files/{file_id}/download")
async def download_file(file_id: str):
    """
    Download file by ID
    """
    try:
        db_file = db_manager.get_file(file_id)
        
        if not db_file:
            raise HTTPException(status_code=404, detail="File not found")
        
        if not Path(db_file.path).exists():
            raise HTTPException(status_code=404, detail="File not found on disk")
        
        return FileResponse(
            path=db_file.path,
            filename=db_file.name,
            media_type="application/octet-stream"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/files/{file_id}")
async def delete_file(file_id: str):
    """
    Delete file from database
    """
    try:
        success = db_manager.delete_file(file_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="File not found")
        
        return {"success": True, "message": "File deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/files/{file_id}/query-sql")
async def query_sql_database(
    file_id: str,
    query: Dict[str, str] = {"query": "SELECT * FROM sqlite_master"}
):
    """
    Execute SQL query on a database file
    
    Requires file to be a SQL/SQLite database
    """
    try:
        sql_query = query.get("query", "SELECT 1")
        results = db_manager.query_sql_database(file_id, sql_query)
        
        return {
            "file_id": file_id,
            "query": sql_query,
            "results": results,
            "row_count": len(results)
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files/{file_id}/excel")
async def read_excel(
    file_id: str,
    sheet_name: Optional[str] = None
):
    """
    Read Excel spreadsheet data
    
    - **sheet_name**: Optional sheet name (reads first sheet if not specified)
    """
    try:
        data = db_manager.read_excel_sheet(file_id, sheet_name)
        
        return {
            "file_id": file_id,
            "sheet": data.get("sheet", "Unknown"),
            "headers": data.get("headers", []),
            "row_count": data.get("row_count", 0),
            "column_count": data.get("column_count", 0),
            "preview": data.get("data", [])[:20]  # First 20 rows
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files/{file_id}/text")
async def extract_document_text(file_id: str):
    """
    Extract text from PDF, PowerPoint, or Word document
    """
    try:
        text = db_manager.extract_document_text(file_id)
        
        return {
            "file_id": file_id,
            "text": text,
            "char_count": len(text),
            "word_count": len(text.split())
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files/{file_id}/thumbnail")
async def get_image_thumbnail(
    file_id: str,
    width: int = Query(200, ge=50, le=1000),
    height: int = Query(200, ge=50, le=1000)
):
    """
    Generate image thumbnail
    
    Requires file to be an image
    """
    try:
        thumb_path = db_manager.get_image_thumbnail(file_id, size=(width, height))
        
        if thumb_path.startswith("Error") or thumb_path.startswith("Pillow"):
            raise HTTPException(status_code=500, detail=thumb_path)
        
        return FileResponse(
            path=thumb_path,
            filename=f"thumb_{file_id}.jpg",
            media_type="image/jpeg"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files/{file_id}/metadata")
async def get_media_metadata(file_id: str):
    """
    Get media file metadata (images, video, audio)
    """
    try:
        db_file = db_manager.get_file(file_id)
        
        if not db_file:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Get appropriate metadata based on type
        if db_file.file_type == FileType.IMAGE:
            metadata = db_manager.media_handler.get_image_metadata(db_file.path)
        elif db_file.file_type == FileType.VIDEO:
            metadata = db_manager.media_handler.get_video_metadata(db_file.path)
        elif db_file.file_type == FileType.AUDIO:
            metadata = db_manager.media_handler.get_audio_metadata(db_file.path)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Media metadata not supported for type: {db_file.file_type.value}"
            )
        
        return {
            "file_id": file_id,
            "file_type": db_file.file_type.value,
            "metadata": metadata
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_database_stats():
    """
    Get database statistics
    """
    try:
        stats = db_manager.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/types")
async def get_supported_types():
    """
    List supported file types
    """
    return {
        "spreadsheets": ["sql", "excel", "csv"],
        "documents": ["pdf", "powerpoint", "word", "text"],
        "media": ["image", "video", "audio"],
        "data": ["json", "xml", "yaml"],
        "all_types": [t.value for t in FileType]
    }


@router.post("/export-excel")
async def export_to_excel(data: Dict[str, Any]):
    """
    Export data to Excel file
    
    Request body:
    - **data**: List of dictionaries
    - **filename**: Output filename (without extension)
    """
    try:
        records = data.get("data", [])
        filename = data.get("filename", "export")
        
        output_path = db_manager.export_to_excel(records, filename)
        
        # Get the created file info
        file_id = Path(output_path).stem
        
        return {
            "success": True,
            "file_path": output_path,
            "filename": f"{filename}.xlsx",
            "row_count": len(records)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/suggest")
async def search_suggestions(
    partial: str = Query(..., min_length=2),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get search autocomplete suggestions
    """
    try:
        suggestions = db_manager.file_indexer.get_search_suggestions(partial, limit)
        return {"suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files/{file_id}/related")
async def get_related_files(
    file_id: str,
    limit: int = Query(10, ge=1, le=50)
):
    """
    Find related files based on content similarity
    """
    try:
        related = db_manager.file_indexer.get_related_files(file_id, limit)
        return {
            "file_id": file_id,
            "related_count": len(related),
            "related_files": related
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
