#!/usr/bin/env python3
"""
Database Module Demo
Quick examples of using the Local Database System
"""

import json
import tempfile
from pathlib import Path
from datetime import datetime

from app.database import DatabaseManager, FileType


def demo_basic_usage():
    """Demonstrate basic database operations"""
    print("=" * 60)
    print("DATABASE MODULE DEMO")
    print("=" * 60)
    
    # Initialize database
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"\n1. Initializing database at: {tmpdir}")
        db = DatabaseManager(tmpdir)
        
        # Add some files
        print("\n2. Adding files to database...")
        
        # Create sample files
        files_created = []
        
        # Text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Veyra - Automated Trading Platform\n")
            f.write("Features: Multi-broker, AI predictions, Portfolio management\n")
            text_path = f.name
        
        db_file = db.add_file(
            text_path,
            category="documentation",
            tags=["overview", "features"],
            description="Platform overview document"
        )
        print(f"   ✓ Added: {db_file.name} (ID: {db_file.file_id})")
        files_created.append(text_path)
        
        # JSON data
        portfolio_data = {
            "portfolio": [
                {"symbol": "AAPL", "shares": 100, "value": 17500},
                {"symbol": "MSFT", "shares": 50, "value": 15000},
                {"symbol": "GOOGL", "shares": 25, "value": 3500}
            ],
            "total_value": 36000,
            "last_updated": datetime.utcnow().isoformat()
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(portfolio_data, f, indent=2)
            json_path = f.name
        
        db_file = db.add_file(
            json_path,
            category="data",
            tags=["portfolio", "2024"],
            description="Current portfolio holdings"
        )
        print(f"   ✓ Added: {db_file.name} (ID: {db_file.file_id})")
        files_created.append(json_path)
        
        # CSV data
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("symbol,date,open,high,low,close,volume\n")
            f.write("AAPL,2024-01-15,185.5,188.0,184.2,187.5,55000000\n")
            f.write("AAPL,2024-01-16,187.5,190.0,186.8,189.2,48000000\n")
            f.write("MSFT,2024-01-15,395.0,398.5,393.2,397.8,25000000\n")
            f.write("MSFT,2024-01-16,397.8,400.0,396.5,399.5,22000000\n")
            csv_path = f.name
        
        db_file = db.add_file(
            csv_path,
            category="market_data",
            tags=["stocks", "prices", "2024"],
            description="Daily stock prices for AAPL and MSFT"
        )
        print(f"   ✓ Added: {db_file.name} (ID: {db_file.file_id})")
        files_created.append(csv_path)
        
        # Show statistics
        print("\n3. Database Statistics:")
        stats = db.get_stats()
        print(f"   Total files: {stats['total_files']}")
        print(f"   Total size: {stats['total_size_mb']:.2f} MB")
        print("   By type:")
        for item in stats['by_type']:
            print(f"      - {item['type']}: {item['count']} files")
        
        # Search functionality
        print("\n4. Searching files...")
        
        # Search by text
        results = db.search_files(query="portfolio")
        print(f"   Search 'portfolio': {len(results)} result(s)")
        for r in results:
            print(f"      - {r.name}: {r.description}")
        
        # Search by type
        results = db.search_files(file_type=FileType.JSON)
        print(f"   Search type=JSON: {len(results)} result(s)")
        
        # Search by tags
        results = db.search_files(tags=["2024"])
        print(f"   Search tags=['2024']: {len(results)} result(s)")
        
        # Retrieve and read files
        print("\n5. Reading file content...")
        
        # Get all files and read the CSV
        files = db.search_files()
        csv_file = [f for f in files if f.file_type == FileType.CSV][0]
        
        print(f"   Reading CSV: {csv_file.name}")
        csv_data = db.excel_handler.read_csv(csv_file.path)
        print(f"   Rows: {csv_data['row_count']}, Columns: {len(csv_data['headers'])}")
        print(f"   Headers: {', '.join(csv_data['headers'])}")
        
        # Export data
        print("\n6. Exporting data to Excel...")
        
        export_data = [
            {"Symbol": "AAPL", "Quantity": 100, "Current Price": 187.50, "Value": 18750},
            {"Symbol": "MSFT", "Quantity": 50, "Current Price": 399.50, "Value": 19975},
            {"Symbol": "GOOGL", "Quantity": 25, "Current Price": 140.00, "Value": 3500}
        ]
        
        output_path = db.export_to_excel(export_data, "portfolio_export")
        print(f"   ✓ Exported to: {output_path}")
        
        # Verify export
        exported_file = db.add_file(output_path, tags=["export", "generated"])
        print(f"   ✓ Added to database: {exported_file.file_id}")
        
        # Full-text search
        print("\n7. Full-text search (indexed content)...")
        
        # Index content is searchable
        index_results = db.file_indexer.search("AAPL")
        print(f"   Search 'AAPL' in index: {len(index_results)} result(s)")
        
        # Get search suggestions
        suggestions = db.file_indexer.get_search_suggestions("port", limit=5)
        print(f"   Suggestions for 'port': {suggestions}")
        
        # Cleanup
        print("\n8. Cleanup...")
        for file_path in files_created:
            Path(file_path).unlink(missing_ok=True)
        
        print("\n" + "=" * 60)
        print("DEMO COMPLETE")
        print("=" * 60)


def demo_sql_operations():
    """Demonstrate SQL database operations"""
    print("\n" + "=" * 60)
    print("SQL DATABASE OPERATIONS DEMO")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db = DatabaseManager(tmpdir)
        
        # Create a SQLite database
        print("\n1. Creating SQLite database...")
        
        sql_path = db.sql_handler.create_database("trades_db")
        print(f"   Created: {sql_path}")
        
        # Create table
        print("\n2. Creating trades table...")
        db.sql_handler.execute_query(
            sql_path,
            """
            CREATE TABLE trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                timestamp TEXT NOT NULL
            )
            """
        )
        print("   ✓ Table created")
        
        # Insert sample data
        print("\n3. Inserting sample trades...")
        trades = [
            ("AAPL", "buy", 100, 175.50, "2024-01-15T10:30:00Z"),
            ("AAPL", "sell", 50, 180.00, "2024-01-16T14:20:00Z"),
            ("MSFT", "buy", 75, 395.00, "2024-01-17T09:15:00Z"),
            ("GOOGL", "buy", 25, 138.50, "2024-01-18T11:00:00Z"),
        ]
        
        for trade in trades:
            db.sql_handler.execute_query(
                sql_path,
                f"INSERT INTO trades (symbol, side, quantity, price, timestamp) VALUES ('{trade[0]}', '{trade[1]}', {trade[2]}, {trade[3]}, '{trade[4]}')"
            )
        
        print(f"   ✓ Inserted {len(trades)} trades")
        
        # Add to database
        db_file = db.add_file(sql_path, tags=["trades", "database"], description="Trading history database")
        print(f"   ✓ Added to database manager: {db_file.file_id}")
        
        # Query data
        print("\n4. Querying trades...")
        
        # All trades
        results = db.query_sql_database(db_file.file_id, "SELECT * FROM trades ORDER BY timestamp DESC")
        print(f"   All trades ({len(results)}):")
        for r in results:
            print(f"      {r['timestamp'][:10]} | {r['symbol']:<6} | {r['side']:<4} | {r['quantity']:>4} @ ${r['price']}")
        
        # Filtered query
        print("\n5. Filtered query (AAPL only)...")
        results = db.query_sql_database(db_file.file_id, "SELECT * FROM trades WHERE symbol='AAPL'")
        print(f"   AAPL trades: {len(results)}")
        
        # Aggregation
        print("\n6. Aggregation query...")
        results = db.query_sql_database(
            db_file.file_id,
            "SELECT symbol, COUNT(*) as trade_count, SUM(quantity) as total_qty FROM trades GROUP BY symbol"
        )
        print("   Summary by symbol:")
        for r in results:
            print(f"      {r['symbol']}: {r['trade_count']} trades, {r['total_qty']} shares")
        
        print("\n" + "=" * 60)
        print("SQL DEMO COMPLETE")
        print("=" * 60)


def demo_excel_operations():
    """Demonstrate Excel operations"""
    print("\n" + "=" * 60)
    print("EXCEL OPERATIONS DEMO")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db = DatabaseManager(tmpdir)
        
        print("\n1. Creating Excel from data...")
        
        # Portfolio data
        portfolio = [
            {"Symbol": "AAPL", "Name": "Apple Inc.", "Sector": "Technology", "Shares": 100, "Price": 187.50, "Value": 18750, "Weight": 0.45},
            {"Symbol": "MSFT", "Name": "Microsoft Corp.", "Sector": "Technology", "Shares": 50, "Price": 399.50, "Value": 19975, "Weight": 0.48},
            {"Symbol": "JPM", "Name": "JPMorgan Chase", "Sector": "Financial", "Shares": 75, "Price": 165.20, "Value": 12390, "Weight": 0.30},
            {"Symbol": "JNJ", "Name": "Johnson & Johnson", "Sector": "Healthcare", "Shares": 40, "Price": 155.80, "Value": 6232, "Weight": 0.15},
        ]
        
        excel_path = db.excel_handler.create_excel(portfolio, str(Path(tmpdir) / "portfolio.xlsx"))
        print(f"   ✓ Created: {excel_path}")
        
        # Add to database
        db_file = db.add_file(excel_path, tags=["portfolio", "excel"], description="Portfolio holdings spreadsheet")
        print(f"   ✓ Added to database: {db_file.file_id}")
        
        # Read Excel
        print("\n2. Reading Excel file...")
        data = db.read_excel_sheet(db_file.file_id)
        print(f"   Sheet: {data['sheet']}")
        print(f"   Headers: {', '.join(data['headers'])}")
        print(f"   Rows: {data['row_count']}")
        
        # Query data
        print("\n3. Querying with filters...")
        filtered = db.excel_handler.query_data(db_file.path, {"Sector": "Technology"})
        print(f"   Technology stocks: {len(filtered)}")
        for stock in filtered:
            print(f"      {stock['Symbol']}: {stock['Name']} - ${stock['Value']:,.2f}")
        
        # Export to CSV
        print("\n4. Converting to CSV...")
        csv_path = db.excel_handler.export_sheet_to_csv(db_file.path, data['sheet'], str(Path(tmpdir) / "portfolio.csv"))
        print(f"   ✓ Exported to: {csv_path}")
        
        # Add CSV to database
        db.add_file(csv_path, tags=["portfolio", "csv", "export"])
        print("   ✓ CSV added to database")
        
        print("\n" + "=" * 60)
        print("EXCEL DEMO COMPLETE")
        print("=" * 60)


def demo_api_usage():
    """Show API usage examples"""
    print("\n" + "=" * 60)
    print("API USAGE EXAMPLES")
    print("=" * 60)
    
    examples = """
# Upload a file
curl -X POST "http://localhost:8000/database/upload" \\
  -F "file=@/path/to/data.xlsx" \\
  -F "category=financial" \\
  -F "tags=2024,Q1" \\
  -F "description=Q1 Financial Report"

# Search files
curl "http://localhost:8000/database/files?query=revenue&type=excel"

# Get file details
curl "http://localhost:8000/database/files/{file_id}"

# Download file
curl "http://localhost:8000/database/files/{file_id}/download" -o file.xlsx

# Query SQL database
curl -X POST "http://localhost:8000/database/files/{file_id}/query-sql" \\
  -H "Content-Type: application/json" \\
  -d '{"query": "SELECT * FROM trades WHERE symbol=\\'AAPL\\'"}'

# Read Excel
curl "http://localhost:8000/database/files/{file_id}/excel?sheet=Sheet1"

# Extract document text
curl "http://localhost:8000/database/files/{file_id}/text"

# Get image thumbnail
curl "http://localhost:8000/database/files/{file_id}/thumbnail?width=300&height=300"

# Get database stats
curl "http://localhost:8000/database/stats"

# Export data to Excel
curl -X POST "http://localhost:8000/database/export-excel" \\
  -H "Content-Type: application/json" \\
  -d '{
    "data": [
      {"Symbol": "AAPL", "Price": 150},
      {"Symbol": "MSFT", "Price": 300}
    ],
    "filename": "stock_prices"
  }'
    """
    
    print(examples)
    
    print("=" * 60)


def main():
    """Run all demos"""
    demo_basic_usage()
    demo_sql_operations()
    demo_excel_operations()
    demo_api_usage()


if __name__ == '__main__':
    main()
