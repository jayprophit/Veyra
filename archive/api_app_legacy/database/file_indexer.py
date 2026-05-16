"""
File Indexer
Full-text indexing and search for all database files
"""

import sqlite3
import re
from typing import Dict, List, Optional, Any
from pathlib import Path


class FileIndexer:
    """Index file contents for full-text search"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_index_table()
    
    def _init_index_table(self):
        """Initialize search index table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_index (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL,
                file_id TEXT NOT NULL,
                field TEXT,
                position INTEGER,
                FOREIGN KEY (file_id) REFERENCES files(file_id) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_search_word ON search_index(word)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_search_file ON search_index(file_id)
        """)
        
        conn.commit()
        conn.close()
    
    def index_file(self, db_file) -> bool:
        """Index file content for search"""
        try:
            # Extract text to index based on file type
            text_to_index = []
            
            # Index filename
            text_to_index.append(("filename", db_file.name))
            
            # Index description
            if db_file.description:
                text_to_index.append(("description", db_file.description))
            
            # Index preview content
            if db_file.preview:
                text_to_index.append(("content", db_file.preview))
            
            # Index tags
            if db_file.tags:
                text_to_index.append(("tags", " ".join(db_file.tags)))
            
            # Index type-specific content
            if db_file.indexed_content:
                content = db_file.indexed_content
                
                if "text" in content:
                    text_to_index.append(("content", content["text"]))
                
                if "sheets" in content:
                    text_to_index.append(("metadata", str(content["sheets"])))
                
                if "schema" in content:
                    text_to_index.append(("schema", content["schema"]))
            
            # Clear existing index for this file
            self._clear_file_index(db_file.file_id)
            
            # Index all text
            for field, text in text_to_index:
                self._index_text(db_file.file_id, field, text)
            
            return True
            
        except Exception as e:
            print(f"Error indexing file {db_file.file_id}: {e}")
            return False
    
    def _clear_file_index(self, file_id: str):
        """Remove existing index entries for file"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM search_index WHERE file_id = ?", (file_id,))
        
        conn.commit()
        conn.close()
    
    def _index_text(self, file_id: str, field: str, text: str):
        """Index text content"""
        if not text:
            return
        
        # Tokenize and clean text
        words = self._tokenize(text)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert words
        for position, word in enumerate(words):
            # Skip very short words and common stop words
            if len(word) < 2 or word in self._get_stop_words():
                continue
            
            cursor.execute("""
                INSERT INTO search_index (word, file_id, field, position)
                VALUES (?, ?, ?, ?)
            """, (word.lower(), file_id, field, position))
        
        conn.commit()
        conn.close()
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words"""
        # Convert to lowercase and extract words
        words = re.findall(r'\b[a-zA-Z0-9]+\\\b', text.lower())
        return words
    
    def _get_stop_words(self) -> set:
        """Get common stop words to ignore"""
        return {
            'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'must', 'shall', 'can',
            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it',
            'we', 'they', 'my', 'your', 'his', 'her', 'its', 'our', 'their'
        }
    
    def search(self, query: str, file_type: Optional[str] = None,
               limit: int = 50) -> List[Dict]:
        """
        Search indexed files
        
        Args:
            query: Search query
            file_type: Optional filter by file type
            limit: Maximum results
        """
        # Tokenize query
        query_words = self._tokenize(query)
        
        if not query_words:
            return []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build search query
        if len(query_words) == 1:
            # Single word search
            sql = """
                SELECT f.file_id, f.name, f.file_type, f.path, f.preview,
                       COUNT(s.word) as relevance
                FROM search_index s
                JOIN files f ON s.file_id = f.file_id
                WHERE s.word = ?
            """
            params = [query_words[0]]
        else:
            # Multi-word search (AND logic)
            placeholders = ','.join('?' * len(query_words))
            sql = f"""
                SELECT f.file_id, f.name, f.file_type, f.path, f.preview,
                       COUNT(DISTINCT s.word) as relevance,
                       COUNT(s.word) as total_matches
                FROM search_index s
                JOIN files f ON s.file_id = f.file_id
                WHERE s.word IN ({placeholders})
                GROUP BY f.file_id
                HAVING COUNT(DISTINCT s.word) >= {len(query_words) * 0.5}
            """
            params = query_words
        
        # Add file type filter
        if file_type:
            sql += " AND f.file_type = ?"
            params.append(file_type)
        
        # Order by relevance
        sql += " ORDER BY relevance DESC, total_matches DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(sql, params)
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                "file_id": row[0],
                "name": row[1],
                "file_type": row[2],
                "path": row[3],
                "preview": row[4] if row[4] else "",
                "relevance_score": row[5]
            }
            for row in results
        ]
    
    def get_related_files(self, file_id: str, limit: int = 10) -> List[Dict]:
        """Find files related by content similarity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get words from this file
        cursor.execute(
            "SELECT DISTINCT word FROM search_index WHERE file_id = ?",
            (file_id,)
        )
        words = [row[0] for row in cursor.fetchall()]
        
        if not words:
            return []
        
        # Find files with similar words
        placeholders = ','.join('?' * len(words))
        cursor.execute(f"""
            SELECT f.file_id, f.name, f.file_type, f.preview, 
                   COUNT(DISTINCT s.word) as shared_words
            FROM search_index s
            JOIN files f ON s.file_id = f.file_id
            WHERE s.word IN ({placeholders})
            AND s.file_id != ?
            GROUP BY s.file_id
            ORDER BY shared_words DESC
            LIMIT ?
        """, words + [file_id, limit])
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                "file_id": row[0],
                "name": row[1],
                "file_type": row[2],
                "preview": row[3],
                "shared_keywords": row[4]
            }
            for row in results
        ]
    
    def get_search_suggestions(self, partial_word: str, limit: int = 10) -> List[str]:
        """Get autocomplete suggestions for search"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT word, COUNT(*) as frequency
            FROM search_index
            WHERE word LIKE ?
            GROUP BY word
            ORDER BY frequency DESC
            LIMIT ?
        """, (f"{partial_word}%", limit))
        
        results = cursor.fetchall()
        conn.close()
        
        return [row[0] for row in results]
    
    def get_index_stats(self) -> Dict:
        """Get indexing statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total indexed words
        cursor.execute("SELECT COUNT(*) FROM search_index")
        total_words = cursor.fetchone()[0]
        
        # Unique words
        cursor.execute("SELECT COUNT(DISTINCT word) FROM search_index")
        unique_words = cursor.fetchone()[0]
        
        # Files indexed
        cursor.execute("SELECT COUNT(DISTINCT file_id) FROM search_index")
        files_indexed = cursor.fetchone()[0]
        
        # Top words
        cursor.execute("""
            SELECT word, COUNT(*) as freq
            FROM search_index
            GROUP BY word
            ORDER BY freq DESC
            LIMIT 20
        """)
        top_words = cursor.fetchall()
        
        conn.close()
        
        return {
            "total_word_occurrences": total_words,
            "unique_words": unique_words,
            "files_indexed": files_indexed,
            "top_words": [{"word": w[0], "frequency": w[1]} for w in top_words],
            "average_words_per_file": round(total_words / files_indexed, 2) if files_indexed > 0 else 0
        }
    
    def rebuild_index(self):
        """Rebuild the entire search index"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear existing index
        cursor.execute("DELETE FROM search_index")
        
        conn.commit()
        conn.close()
        
        print("Search index cleared. Re-index files as needed.")
