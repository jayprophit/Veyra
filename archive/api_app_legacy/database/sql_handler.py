"""
SQL Database Handler
Manages SQLite and SQL database files
"""

import sqlite3
from typing import Dict, List, Optional, Any
from pathlib import Path


class SQLHandler:
    """Handle SQL database operations"""
    
    def __init__(self, base_path: Path):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def execute_query(self, db_path: str, query: str) -> List[Dict]:
        """Execute SQL query on database"""
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute(query)
            
            # If SELECT, return results
            if query.strip().upper().startswith("SELECT"):
                rows = cursor.fetchall()
                result = [dict(row) for row in rows]
            else:
                conn.commit()
                result = [{"affected_rows": cursor.rowcount}]
            
            return result
            
        except sqlite3.Error as e:
            return [{"error": str(e)}]
        finally:
            conn.close()
    
    def get_schema_summary(self, db_path: str) -> str:
        """Get database schema summary"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        schema_parts = []
        
        # Get tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            schema_parts.append(f"\nTable: {table_name}")
            
            # Get columns
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            for col in columns:
                schema_parts.append(f"  - {col[1]} ({col[2]})")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            schema_parts.append(f"  Rows: {count}")
        
        conn.close()
        
        return "\n".join(schema_parts)
    
    def get_tables(self, db_path: str) -> List[str]:
        """Get list of tables in database"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return tables
    
    def get_table_data(self, db_path: str, table_name: str, limit: int = 100) -> Dict:
        """Get table data with columns info"""
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get columns
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Get data
        cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
        rows = cursor.fetchall()
        
        conn.close()
        
        return {
            "table": table_name,
            "columns": columns,
            "data": [dict(row) for row in rows],
            "row_count": len(rows)
        }
    
    def create_database(self, name: str) -> str:
        """Create new SQLite database"""
        db_path = self.base_path / f"{name}.db"
        
        # Create empty database
        conn = sqlite3.connect(db_path)
        conn.close()
        
        return str(db_path)
    
    def import_csv_to_table(self, db_path: str, csv_path: str, table_name: str) -> bool:
        """Import CSV file into SQL table"""
        import csv
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Get columns from first row
                first_row = next(reader)
                columns = list(first_row.keys())
                
                # Create table
                col_defs = ", ".join([f"{col} TEXT" for col in columns])
                cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({col_defs})")
                
                # Insert first row
                placeholders = ", ".join(["?" for _ in columns])
                cursor.execute(
                    f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})",
                    list(first_row.values())
                )
                
                # Insert remaining rows
                for row in reader:
                    cursor.execute(
                        f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})",
                        list(row.values())
                    )
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Import error: {e}")
            return False
        finally:
            conn.close()
