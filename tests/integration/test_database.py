"""
Database Module Integration Tests
Tests for Local Database System
"""

import pytest
import tempfile
import json
from pathlib import Path
from datetime import datetime

from app.database import DatabaseManager, FileType, SQLHandler, ExcelHandler


class TestDatabaseManager:
    """Test DatabaseManager functionality"""
    
    @pytest.fixture
    def db(self):
        """Create temporary database for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield DatabaseManager(tmpdir)
    
    def test_add_and_retrieve_file(self, db):
        """Test adding and retrieving a file"""
        # Create a test text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test content for database")
            test_path = f.name
        
        try:
            # Add file
            db_file = db.add_file(
                test_path,
                category="test",
                tags=["test", "integration"],
                description="Test file"
            )
            
            assert db_file.name == Path(test_path).name
            assert db_file.file_type == FileType.TEXT
            assert "test" in db_file.tags
            assert db_file.description == "Test file"
            
            # Retrieve file
            retrieved = db.get_file(db_file.file_id)
            assert retrieved is not None
            assert retrieved.file_id == db_file.file_id
            
        finally:
            Path(test_path).unlink(missing_ok=True)
    
    def test_file_type_detection(self, db):
        """Test automatic file type detection"""
        test_cases = [
            ("data.db", FileType.SQL),
            ("report.xlsx", FileType.EXCEL),
            ("data.csv", FileType.CSV),
            ("doc.pdf", FileType.PDF),
            ("slides.pptx", FileType.POWERPOINT),
            ("document.docx", FileType.WORD),
            ("notes.txt", FileType.TEXT),
            ("photo.jpg", FileType.IMAGE),
            ("video.mp4", FileType.VIDEO),
            ("audio.mp3", FileType.AUDIO),
            ("config.json", FileType.JSON),
            ("data.xml", FileType.XML),
            ("config.yaml", FileType.YAML),
        ]
        
        for filename, expected_type in test_cases:
            detected = db.detect_file_type(filename)
            assert detected == expected_type, f"Failed for {filename}: got {detected}, expected {expected_type}"
    
    def test_search_files(self, db):
        """Test file search functionality"""
        # Create and add test files
        files = []
        
        for i in range(3):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(f"Financial report {i} content")
                test_path = f.name
            
            db_file = db.add_file(test_path, tags=["2024", f"Q{i+1}"])
            files.append(db_file)
            Path(test_path).unlink(missing_ok=True)
        
        # Search by query
        results = db.search_files(query="Financial")
        assert len(results) == 3
        
        # Search by type
        results = db.search_files(file_type=FileType.TEXT)
        assert len(results) == 3
        
        # Search by tags
        results = db.search_files(tags=["Q1"])
        assert len(results) == 1
    
    def test_delete_file(self, db):
        """Test file deletion"""
        # Create and add file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Delete me")
            test_path = f.name
        
        try:
            db_file = db.add_file(test_path)
            file_id = db_file.file_id
            
            # Verify file exists
            assert db.get_file(file_id) is not None
            
            # Delete file
            success = db.delete_file(file_id)
            assert success is True
            
            # Verify file is gone
            assert db.get_file(file_id) is None
            
        finally:
            Path(test_path).unlink(missing_ok=True)
    
    def test_database_stats(self, db):
        """Test statistics retrieval"""
        # Add some files
        for ext in ['.txt', '.csv', '.json']:
            with tempfile.NamedTemporaryFile(mode='w', suffix=ext, delete=False) as f:
                f.write("Test content")
                test_path = f.name
            
            db.add_file(test_path)
            Path(test_path).unlink(missing_ok=True)
        
        stats = db.get_stats()
        
        assert stats["total_files"] == 3
        assert stats["total_size_mb"] > 0
        assert len(stats["by_type"]) > 0


class TestSQLHandler:
    """Test SQL database operations"""
    
    @pytest.fixture
    def sql_handler(self):
        """Create temporary SQL handler"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield SQLHandler(tmpdir)
    
    def test_create_database(self, sql_handler):
        """Test database creation"""
        db_path = sql_handler.create_database("test_db")
        assert Path(db_path).exists()
    
    def test_execute_query(self, sql_handler):
        """Test SQL query execution"""
        db_path = sql_handler.create_database("test_query")
        
        # Create table
        sql_handler.execute_query(
            db_path,
            "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)"
        )
        
        # Insert data
        sql_handler.execute_query(
            db_path,
            "INSERT INTO users (name) VALUES ('Alice'), ('Bob')"
        )
        
        # Select data
        results = sql_handler.execute_query(
            db_path,
            "SELECT * FROM users"
        )
        
        assert len(results) == 2
        assert results[0]["name"] == "Alice"
    
    def test_get_schema_summary(self, sql_handler):
        """Test schema summary extraction"""
        db_path = sql_handler.create_database("test_schema")
        
        # Create tables
        sql_handler.execute_query(db_path, "CREATE TABLE trades (id INTEGER, symbol TEXT)")
        sql_handler.execute_query(db_path, "CREATE TABLE accounts (id INTEGER, balance REAL)")
        
        schema = sql_handler.get_schema_summary(db_path)
        
        assert "trades" in schema
        assert "accounts" in schema
    
    def test_import_csv(self, sql_handler):
        """Test CSV import"""
        # Create test CSV
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("name,age,city\n")
            f.write("Alice,30,NYC\n")
            f.write("Bob,25,LA\n")
            csv_path = f.name
        
        try:
            db_path = sql_handler.create_database("test_import")
            
            success = sql_handler.import_csv_to_table(db_path, csv_path, "people")
            assert success is True
            
            # Verify import
            results = sql_handler.execute_query(db_path, "SELECT * FROM people")
            assert len(results) == 2
            assert results[0]["name"] == "Alice"
            
        finally:
            Path(csv_path).unlink(missing_ok=True)


class TestExcelHandler:
    """Test Excel/Spreadsheet operations"""
    
    @pytest.fixture
    def excel_handler(self):
        """Create temporary Excel handler"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield ExcelHandler(tmpdir)
    
    def test_create_and_read_csv(self, excel_handler):
        """Test CSV creation and reading"""
        data = [
            {"Symbol": "AAPL", "Price": 150.00, "Volume": 1000000},
            {"Symbol": "MSFT", "Price": 300.00, "Volume": 2000000}
        ]
        
        output_path = str(Path(excel_handler.base_path) / "test.csv")
        
        # Create CSV
        result = excel_handler.create_csv(data, output_path)
        assert Path(result).exists()
        
        # Read CSV
        read_data = excel_handler.read_csv(result)
        assert len(read_data["data"]) == 2
        assert read_data["headers"] == ["Symbol", "Price", "Volume"]
    
    def test_query_data(self, excel_handler):
        """Test data querying with filters"""
        # Create test data
        data = [
            {"Category": "A", "Value": 100},
            {"Category": "B", "Value": 200},
            {"Category": "A", "Value": 300}
        ]
        
        csv_path = str(Path(excel_handler.base_path) / "query_test.csv")
        excel_handler.create_csv(data, csv_path)
        
        # Query with filter
        results = excel_handler.query_data(csv_path, {"Category": "A"})
        assert len(results) == 2


class TestFileIndexer:
    """Test file indexing and search"""
    
    @pytest.fixture
    def db_with_indexer(self):
        """Create database with indexer"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield DatabaseManager(tmpdir)
    
    def test_index_and_search(self, db_with_indexer):
        """Test file indexing and search"""
        # Create and add text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Financial analysis report for Q1 2024")
            test_path = f.name
        
        try:
            db_file = db_with_indexer.add_file(test_path, tags=["finance"])
            
            # Search via indexer
            results = db_with_indexer.file_indexer.search("Financial")
            assert len(results) >= 1
            
            # Search for specific word
            results = db_with_indexer.file_indexer.search("analysis")
            assert len(results) >= 1
            
        finally:
            Path(test_path).unlink(missing_ok=True)
    
    def test_search_suggestions(self, db_with_indexer):
        """Test autocomplete suggestions"""
        # Add file with content
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Revenue growth analysis")
            test_path = f.name
        
        try:
            db_with_indexer.add_file(test_path)
            
            # Get suggestions
            suggestions = db_with_indexer.file_indexer.get_search_suggestions("rev", limit=5)
            assert "revenue" in [s.lower() for s in suggestions]
            
        finally:
            Path(test_path).unlink(missing_ok=True)


class TestDocumentHandler:
    """Test document processing"""
    
    @pytest.fixture
    def db_with_docs(self):
        """Create database for document tests"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield DatabaseManager(tmpdir)
    
    def test_extract_text_from_text_file(self, db_with_docs):
        """Test text extraction from plain text"""
        content = "This is a test document for extraction."
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            test_path = f.name
        
        try:
            db_file = db_with_docs.add_file(test_path)
            
            # Extract text
            text = db_with_docs.extract_document_text(db_file.file_id)
            assert content in text
            
        finally:
            Path(test_path).unlink(missing_ok=True)


class TestMediaHandler:
    """Test media file operations"""
    
    @pytest.fixture
    def db_with_media(self):
        """Create database for media tests"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield DatabaseManager(tmpdir)
    
    def test_image_metadata(self, db_with_media):
        """Test image metadata extraction"""
        try:
            from PIL import Image
            
            # Create test image
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                img = Image.new('RGB', (100, 200), color='red')
                img.save(f.name)
                test_path = f.name
            
            db_file = db_with_media.add_file(test_path)
            
            # Get metadata
            metadata = db_with_media.media_handler.get_image_metadata(db_file.path)
            
            assert metadata.get("width") == 100
            assert metadata.get("height") == 200
            assert metadata.get("format") == "PNG"
            
        except ImportError:
            pytest.skip("Pillow not installed")
        finally:
            Path(test_path).unlink(missing_ok=True)


class TestDatabaseAPI:
    """Test API endpoints"""
    
    def test_api_upload_endpoint(self, client):
        """Test file upload via API"""
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        
        # Create test file
        test_content = b"Test file content"
        
        response = client.post(
            "/database/upload",
            files={"file": ("test.txt", test_content, "text/plain")},
            data={"category": "test", "tags": "tag1,tag2"}
        )
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "file_id" in response.json()
    
    def test_api_search_endpoint(self, client):
        """Test search via API"""
        response = client.get("/database/files?query=test")
        
        assert response.status_code == 200
        assert "files" in response.json()
    
    def test_api_stats_endpoint(self, client):
        """Test stats endpoint"""
        response = client.get("/database/stats")
        
        assert response.status_code == 200
        assert "total_files" in response.json()


# Test data fixtures
@pytest.fixture
def sample_portfolio_data():
    """Sample portfolio data for tests"""
    return [
        {"symbol": "AAPL", "quantity": 100, "avg_price": 150.00, "current_price": 175.00},
        {"symbol": "MSFT", "quantity": 50, "avg_price": 250.00, "current_price": 300.00},
        {"symbol": "GOOGL", "quantity": 25, "avg_price": 120.00, "current_price": 140.00}
    ]


@pytest.fixture
def sample_trades_data():
    """Sample trades data for tests"""
    return [
        {"symbol": "AAPL", "side": "buy", "quantity": 100, "price": 150.00, "timestamp": "2024-01-15T10:30:00Z"},
        {"symbol": "AAPL", "side": "sell", "quantity": 50, "price": 160.00, "timestamp": "2024-01-16T14:20:00Z"},
        {"symbol": "MSFT", "side": "buy", "quantity": 50, "price": 250.00, "timestamp": "2024-01-17T09:15:00Z"}
    ]


def test_export_portfolio_to_excel(db, sample_portfolio_data):
    """Test exporting portfolio data to Excel"""
    output_path = db.export_to_excel(sample_portfolio_data, "test_portfolio")
    
    assert Path(output_path).exists()
    
    # Read it back
    import pandas as pd
    df = pd.read_excel(output_path)
    assert len(df) == 3
    assert list(df.columns) == ["symbol", "quantity", "avg_price", "current_price"]


def test_export_trades_to_csv(db, sample_trades_data):
    """Test exporting trades to CSV"""
    output_path = str(Path(db.base_path) / "trades.csv")
    result = db.excel_handler.create_csv(sample_trades_data, output_path)
    
    assert Path(result).exists()
    
    # Read back
    data = db.excel_handler.read_csv(result)
    assert len(data["data"]) == 3


def test_database_performance_benchmark(db):
    """Benchmark database operations"""
    import time
    
    # Benchmark file addition
    start = time.time()
    
    for i in range(100):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(f"Test content {i}")
            test_path = f.name
        
        db.add_file(test_path, tags=[f"tag_{i}"])
        Path(test_path).unlink(missing_ok=True)
    
    duration = time.time() - start
    
    # Should complete in reasonable time (< 30 seconds for 100 files)
    assert duration < 30.0
    
    # Verify all files were added
    stats = db.get_stats()
    assert stats["total_files"] == 100


def test_concurrent_access():
    """Test database handles concurrent access"""
    import threading
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db = DatabaseManager(tmpdir)
        errors = []
        
        def add_files(thread_id):
            try:
                for i in range(10):
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                        f.write(f"Thread {thread_id} file {i}")
                        test_path = f.name
                    
                    db.add_file(test_path, tags=[f"thread_{thread_id}"])
                    Path(test_path).unlink(missing_ok=True)
                    time.sleep(0.01)  # Small delay
            except Exception as e:
                errors.append(e)
        
        # Run concurrent threads
        threads = []
        for i in range(5):
            t = threading.Thread(target=add_files, args=(i,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # No errors should occur
        assert len(errors) == 0, f"Concurrent access errors: {errors}"
        
        # All files should be added
        stats = db.get_stats()
        assert stats["total_files"] == 50
