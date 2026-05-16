#!/usr/bin/env python3
"""
Database CLI Tool
Command-line interface for Local Database System
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from app.database import DatabaseManager, FileType


def main():
    parser = argparse.ArgumentParser(
        description="Veyra Local Database CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s add data.xlsx --tags "2024,Q1" --desc "Financial report"
  %(prog)s search "revenue" --type excel
  %(prog)s list --type pdf
  %(prog)s stats
  %(prog)s query-sql FILE_ID "SELECT * FROM trades"
  %(prog)s read-excel FILE_ID --sheet "Sheet1"
        """
    )
    
    parser.add_argument(
        '--db-path',
        default='./local_database',
        help='Database directory path (default: ./local_database)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add file to database')
    add_parser.add_argument('file', help='Path to file to add')
    add_parser.add_argument('--category', help='Category folder')
    add_parser.add_argument('--tags', help='Comma-separated tags')
    add_parser.add_argument('--desc', '--description', help='File description')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search files')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--type', help='Filter by file type')
    search_parser.add_argument('--tags', help='Filter by tags')
    search_parser.add_argument('--limit', type=int, default=20, help='Max results')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List files')
    list_parser.add_argument('--type', help='Filter by file type')
    list_parser.add_argument('--limit', type=int, default=50, help='Max results')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show database statistics')
    
    # Get command
    get_parser = subparsers.add_parser('get', help='Get file details')
    get_parser.add_argument('file_id', help='File ID')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete file')
    delete_parser.add_argument('file_id', help='File ID')
    
    # Query SQL command
    sql_parser = subparsers.add_parser('query-sql', help='Query SQL database')
    sql_parser.add_argument('file_id', help='SQL file ID')
    sql_parser.add_argument('query', help='SQL query string')
    
    # Read Excel command
    excel_parser = subparsers.add_parser('read-excel', help='Read Excel file')
    excel_parser.add_argument('file_id', help='Excel file ID')
    excel_parser.add_argument('--sheet', help='Sheet name (default: first sheet)')
    
    # Extract text command
    text_parser = subparsers.add_parser('extract-text', help='Extract text from document')
    text_parser.add_argument('file_id', help='Document file ID')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export data to Excel')
    export_parser.add_argument('json_file', help='JSON file with data')
    export_parser.add_argument('output_name', help='Output filename')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialize database
    db = DatabaseManager(args.db_path)
    
    try:
        if args.command == 'add':
            cmd_add(db, args)
        elif args.command == 'search':
            cmd_search(db, args)
        elif args.command == 'list':
            cmd_list(db, args)
        elif args.command == 'stats':
            cmd_stats(db, args)
        elif args.command == 'get':
            cmd_get(db, args)
        elif args.command == 'delete':
            cmd_delete(db, args)
        elif args.command == 'query-sql':
            cmd_query_sql(db, args)
        elif args.command == 'read-excel':
            cmd_read_excel(db, args)
        elif args.command == 'extract-text':
            cmd_extract_text(db, args)
        elif args.command == 'export':
            cmd_export(db, args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_add(db: DatabaseManager, args):
    """Add file to database"""
    if not Path(args.file).exists():
        print(f"Error: File not found: {args.file}")
        sys.exit(1)
    
    tags = [t.strip() for t in args.tags.split(',')] if args.tags else []
    
    db_file = db.add_file(
        args.file,
        category=args.category,
        tags=tags,
        description=args.desc
    )
    
    print(f"✓ Added file: {db_file.file_id}")
    print(f"  Name: {db_file.name}")
    print(f"  Type: {db_file.file_type.value}")
    print(f"  Size: {db_file.size_bytes:,} bytes")
    print(f"  Tags: {', '.join(db_file.tags) if db_file.tags else 'None'}")


def cmd_search(db: DatabaseManager, args):
    """Search files"""
    ft = FileType(args.type) if args.type else None
    tags = [t.strip() for t in args.tags.split(',')] if args.tags else None
    
    results = db.search_files(
        query=args.query,
        file_type=ft,
        tags=tags
    )
    
    print(f"Found {len(results)} result(s):\n")
    
    for i, f in enumerate(results[:args.limit], 1):
        print(f"{i}. {f.name}")
        print(f"   ID: {f.file_id}")
        print(f"   Type: {f.file_type.value}")
        print(f"   Modified: {f.modified_at.strftime('%Y-%m-%d %H:%M')}")
        if f.preview:
            preview = f.preview[:60].replace('\n', ' ')
            print(f"   Preview: {preview}...")
        print()


def cmd_list(db: DatabaseManager, args):
    """List files"""
    ft = FileType(args.type) if args.type else None
    results = db.search_files(file_type=ft)
    
    print(f"{'ID':<20} {'Name':<30} {'Type':<12} {'Size':<12} {'Modified'}")
    print("=" * 100)
    
    for f in results[:args.limit]:
        size_mb = f.size_bytes / (1024 * 1024)
        size_str = f"{size_mb:.2f} MB" if size_mb >= 1 else f"{f.size_bytes:,} B"
        name = f.name[:28] + ".." if len(f.name) > 30 else f.name
        print(f"{f.file_id:<20} {name:<30} {f.file_type.value:<12} {size_str:<12} {f.modified_at.strftime('%Y-%m-%d')}")
    
    print(f"\nShowing {min(len(results), args.limit)} of {len(results)} file(s)")


def cmd_stats(db: DatabaseManager, args):
    """Show database statistics"""
    stats = db.get_stats()
    
    print("Database Statistics")
    print("=" * 40)
    print(f"Total Files: {stats['total_files']:,}")
    print(f"Total Size: {stats['total_size_mb']:.2f} MB")
    print(f"\nBy Type:")
    print("-" * 40)
    
    for item in stats['by_type']:
        print(f"  {item['type']:<15} {item['count']:,} files ({item['size_mb']:.2f} MB)")
    
    print(f"\nDatabase Path: {stats['database_path']}")


def cmd_get(db: DatabaseManager, args):
    """Get file details"""
    f = db.get_file(args.file_id)
    
    if not f:
        print(f"Error: File not found: {args.file_id}")
        sys.exit(1)
    
    print(f"File Details")
    print("=" * 40)
    print(f"ID: {f.file_id}")
    print(f"Name: {f.name}")
    print(f"Type: {f.file_type.value}")
    print(f"Path: {f.path}")
    print(f"Size: {f.size_bytes:,} bytes ({f.size_bytes / (1024 * 1024):.2f} MB)")
    print(f"Created: {f.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Modified: {f.modified_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Checksum: {f.checksum}")
    print(f"Tags: {', '.join(f.tags) if f.tags else 'None'}")
    print(f"Description: {f.description or 'None'}")
    print(f"Access Count: {f.access_count}")
    
    if f.preview:
        print(f"\nPreview:")
        print("-" * 40)
        print(f.preview[:200])


def cmd_delete(db: DatabaseManager, args):
    """Delete file"""
    f = db.get_file(args.file_id)
    
    if not f:
        print(f"Error: File not found: {args.file_id}")
        sys.exit(1)
    
    confirm = input(f"Delete '{f.name}'? (yes/no): ")
    
    if confirm.lower() == 'yes':
        db.delete_file(args.file_id)
        print(f"✓ Deleted file: {args.file_id}")
    else:
        print("Cancelled")


def cmd_query_sql(db: DatabaseManager, args):
    """Query SQL database"""
    try:
        results = db.query_sql_database(args.file_id, args.query)
        
        if not results:
            print("No results")
            return
        
        if isinstance(results[0], dict) and 'error' in results[0]:
            print(f"Error: {results[0]['error']}")
            return
        
        # Print as table
        if results and isinstance(results[0], dict):
            headers = list(results[0].keys())
            
            # Calculate column widths
            widths = {h: len(h) for h in headers}
            for row in results:
                for h in headers:
                    val = str(row.get(h, ''))
                    widths[h] = max(widths[h], len(val))
            
            # Print header
            print(' | '.join(h.ljust(widths[h]) for h in headers))
            print('-' * (sum(widths.values()) + 3 * (len(headers) - 1)))
            
            # Print rows
            for row in results[:50]:  # Limit to 50 rows
                print(' | '.join(str(row.get(h, '')).ljust(widths[h]) for h in headers))
            
            if len(results) > 50:
                print(f"\n... and {len(results) - 50} more row(s)")
        else:
            for row in results:
                print(row)
                
    except Exception as e:
        print(f"Error: {e}")


def cmd_read_excel(db: DatabaseManager, args):
    """Read Excel file"""
    try:
        data = db.read_excel_sheet(args.file_id, args.sheet)
        
        print(f"Sheet: {data.get('sheet', 'Unknown')}")
        print(f"Rows: {data.get('row_count', 0)}")
        print(f"Columns: {data.get('column_count', 0)}")
        print(f"Headers: {', '.join(data.get('headers', []))}")
        print()
        
        # Print data preview
        rows = data.get('data', [])
        for i, row in enumerate(rows[:20], 1):
            print(f"{i}. {row}")
        
        if len(rows) > 20:
            print(f"\n... and {len(rows) - 20} more row(s)")
            
    except Exception as e:
        print(f"Error: {e}")


def cmd_extract_text(db: DatabaseManager, args):
    """Extract text from document"""
    try:
        text = db.extract_document_text(args.file_id)
        
        print(f"Extracted Text ({len(text)} characters, {len(text.split())} words):")
        print("=" * 60)
        print(text[:2000])  # Print first 2000 chars
        
        if len(text) > 2000:
            print(f"\n... ({len(text) - 2000} more characters)")
            
    except Exception as e:
        print(f"Error: {e}")


def cmd_export(db: DatabaseManager, args):
    """Export JSON data to Excel"""
    import json
    
    if not Path(args.json_file).exists():
        print(f"Error: File not found: {args.json_file}")
        sys.exit(1)
    
    with open(args.json_file) as f:
        data = json.load(f)
    
    output_path = db.export_to_excel(data, args.output_name)
    
    print(f"✓ Exported to: {output_path}")
    print(f"  Records: {len(data)}")


if __name__ == '__main__':
    main()
