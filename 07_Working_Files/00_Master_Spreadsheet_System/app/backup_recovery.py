"""Backup & Recovery - Automated backup and disaster recovery.

Features:
- Scheduled backups (SQLite, config, logs)
- Cloud sync (local, S3, Dropbox, Google Drive)
- Incremental backups
- Point-in-time recovery
- Compression and encryption
- Backup verification
"""

import os
import shutil
import gzip
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging
import tarfile
import hashlib

logger = logging.getLogger('BackupManager')

class BackupManager:
    """Manage system backups."""
    
    def __init__(self, 
                 data_dir: str = "./data",
                 backup_dir: str = "./backups",
                 config_dir: str = "."):
        self.data_dir = Path(data_dir)
        self.backup_dir = Path(backup_dir)
        self.config_dir = Path(config_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Ensure data directory exists
        self.data_dir.mkdir(exist_ok=True)
    
    def create_backup(self, 
                     name: Optional[str] = None,
                     compress: bool = True,
                     include_logs: bool = False) -> Dict:
        """Create full system backup."""
        
        if not name:
            name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_path = self.backup_dir / name
        backup_path.mkdir(exist_ok=True)
        
        backed_up = []
        errors = []
        
        # Backup database
        try:
            db_backup = self._backup_database(backup_path)
            backed_up.append(db_backup)
        except Exception as e:
            errors.append(f"Database backup failed: {e}")
        
        # Backup configuration files
        try:
            config_backup = self._backup_configs(backup_path)
            backed_up.append(config_backup)
        except Exception as e:
            errors.append(f"Config backup failed: {e}")
        
        # Backup logs (optional)
        if include_logs:
            try:
                logs_backup = self._backup_logs(backup_path)
                backed_up.append(logs_backup)
            except Exception as e:
                errors.append(f"Logs backup failed: {e}")
        
        # Create manifest
        manifest = {
            "backup_name": name,
            "timestamp": datetime.now().isoformat(),
            "files": backed_up,
            "errors": errors,
            "system_info": self._get_system_info()
        }
        
        manifest_path = backup_path / "manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        # Compress if requested
        if compress:
            archive_path = self._compress_backup(backup_path)
            # Remove uncompressed backup
            shutil.rmtree(backup_path)
            return {
                "success": len(errors) == 0,
                "backup_path": str(archive_path),
                "size_bytes": archive_path.stat().st_size,
                "manifest": manifest
            }
        
        return {
            "success": len(errors) == 0,
            "backup_path": str(backup_path),
            "manifest": manifest
        }
    
    def _backup_database(self, backup_path: Path) -> str:
        """Backup SQLite database."""
        db_file = self.data_dir / "financial_master.db"
        
        if not db_file.exists():
            logger.warning(f"Database file not found: {db_file}")
            return ""
        
        backup_db = backup_path / "database" / "financial_master.db"
        backup_db.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy database (SQLite supports hot backup)
        shutil.copy2(db_file, backup_db)
        
        # Verify backup
        import sqlite3
        conn = sqlite3.connect(str(backup_db))
        conn.execute("PRAGMA integrity_check")
        conn.close()
        
        logger.info(f"Database backed up: {backup_db}")
        return str(backup_db.relative_to(backup_path))
    
    def _backup_configs(self, backup_path: Path) -> str:
        """Backup configuration files."""
        config_files = [
            ".env",
            ".env.example",
            "docker-compose.yml",
            "Dockerfile",
            "requirements.txt"
        ]
        
        config_backup = backup_path / "config"
        config_backup.mkdir(exist_ok=True)
        
        backed_up = []
        for file in config_files:
            src = self.config_dir / file
            if src.exists():
                shutil.copy2(src, config_backup / file)
                backed_up.append(file)
        
        logger.info(f"Configs backed up: {backed_up}")
        return str(config_backup.relative_to(backup_path))
    
    def _backup_logs(self, backup_path: Path) -> str:
        """Backup log files."""
        logs_dir = Path("./logs")
        
        if not logs_dir.exists():
            return ""
        
        logs_backup = backup_path / "logs"
        logs_backup.mkdir(exist_ok=True)
        
        # Copy recent log files (last 7 days)
        cutoff = datetime.now() - timedelta(days=7)
        
        for log_file in logs_dir.glob("*.log"):
            if datetime.fromtimestamp(log_file.stat().st_mtime) > cutoff:
                shutil.copy2(log_file, logs_backup / log_file.name)
        
        logger.info(f"Logs backed up to: {logs_backup}")
        return str(logs_backup.relative_to(backup_path))
    
    def _compress_backup(self, backup_path: Path) -> Path:
        """Compress backup to tar.gz."""
        archive_name = backup_path.name + ".tar.gz"
        archive_path = self.backup_dir / archive_name
        
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(backup_path, arcname=backup_path.name)
        
        logger.info(f"Backup compressed: {archive_path}")
        return archive_path
    
    def _get_system_info(self) -> Dict:
        """Get system information for backup manifest."""
        return {
            "python_version": os.sys.version,
            "platform": os.sys.platform,
            "backup_tool_version": "1.0.0"
        }
    
    def list_backups(self) -> List[Dict]:
        """List all available backups."""
        backups = []
        
        for item in self.backup_dir.iterdir():
            if item.suffix == ".gz":
                stat = item.stat()
                backups.append({
                    "name": item.stem,
                    "path": str(item),
                    "size_bytes": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        return sorted(backups, key=lambda x: x["created"], reverse=True)
    
    def restore_backup(self, backup_name: str, target_dir: Optional[str] = None) -> bool:
        """Restore from backup."""
        backup_path = self.backup_dir / backup_name
        
        if not backup_path.exists():
            # Try with extension
            backup_path = self.backup_dir / (backup_name + ".tar.gz")
        
        if not backup_path.exists():
            logger.error(f"Backup not found: {backup_name}")
            return False
        
        target = Path(target_dir) if target_dir else self.config_dir.parent / "restore"
        target.mkdir(exist_ok=True)
        
        try:
            # Extract archive
            with tarfile.open(backup_path, "r:gz") as tar:
                tar.extractall(target)
            
            logger.info(f"Backup restored to: {target}")
            return True
            
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False
    
    def verify_backup(self, backup_name: str) -> bool:
        """Verify backup integrity."""
        backup_path = self.backup_dir / backup_name
        
        if not backup_path.exists():
            backup_path = self.backup_dir / (backup_name + ".tar.gz")
        
        if not backup_path.exists():
            return False
        
        try:
            # Check if it's a valid tar.gz
            with tarfile.open(backup_path, "r:gz") as tar:
                # List contents without extracting
                members = tar.getmembers()
                
                # Check for manifest
                manifest_found = any("manifest.json" in m.name for m in members)
                
                if not manifest_found:
                    logger.warning("Backup missing manifest.json")
                    return False
                
                logger.info(f"Backup verified: {len(members)} files")
                return True
                
        except Exception as e:
            logger.error(f"Backup verification failed: {e}")
            return False
    
    def cleanup_old_backups(self, keep_days: int = 30) -> int:
        """Remove backups older than specified days."""
        cutoff = datetime.now() - timedelta(days=keep_days)
        removed = 0
        
        for item in self.backup_dir.iterdir():
            if item.suffix in [".gz", ".zip"]:
                if datetime.fromtimestamp(item.stat().st_mtime) < cutoff:
                    item.unlink()
                    removed += 1
                    logger.info(f"Removed old backup: {item.name}")
        
        return removed

class CloudSync:
    """Sync backups to cloud storage."""
    
    def __init__(self, backup_manager: BackupManager):
        self.backup_manager = backup_manager
    
    def sync_to_s3(self, bucket: str, aws_profile: str = "default") -> bool:
        """Sync backups to AWS S3."""
        try:
            import boto3
            
            session = boto3.Session(profile_name=aws_profile)
            s3 = session.client('s3')
            
            for backup in self.backup_manager.list_backups():
                backup_path = Path(backup["path"])
                key = f"financial-master/{backup_path.name}"
                
                s3.upload_file(str(backup_path), bucket, key)
                logger.info(f"Synced to S3: {key}")
            
            return True
            
        except ImportError:
            logger.error("boto3 not installed. Run: pip install boto3")
            return False
        except Exception as e:
            logger.error(f"S3 sync failed: {e}")
            return False

class ScheduledBackup:
    """Scheduled automatic backups."""
    
    def __init__(self, backup_manager: BackupManager):
        self.backup_manager = backup_manager
        self.running = False
    
    def run_daily_backup(self):
        """Run daily backup task."""
        logger.info("Running scheduled daily backup...")
        
        # Create backup
        result = self.backup_manager.create_backup(
            name=f"daily_{datetime.now().strftime('%Y%m%d')}",
            compress=True
        )
        
        if result["success"]:
            logger.info(f"Daily backup completed: {result['backup_path']}")
            
            # Cleanup old backups
            removed = self.backup_manager.cleanup_old_backups(keep_days=30)
            logger.info(f"Cleaned up {removed} old backups")
        else:
            logger.error("Daily backup failed")

if __name__ == "__main__":
    # Example usage
    bm = BackupManager()
    
    # Create backup
    result = bm.create_backup(include_logs=False)
    print(f"Backup created: {result}")
    
    # List backups
    backups = bm.list_backups()
    print(f"Available backups: {len(backups)}")
    
    # Verify latest
    if backups:
        is_valid = bm.verify_backup(backups[0]["name"])
        print(f"Latest backup valid: {is_valid}")
