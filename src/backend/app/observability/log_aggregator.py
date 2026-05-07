"""
Enterprise Log Aggregator
==========================
Centralized log aggregation with ELK stack compatibility
"""

import asyncio
import json
import gzip
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import deque
import aiohttp
import aiofiles
from pathlib import Path

logger = logging.getLogger(__name__)


class LogLevel(Enum):
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    FATAL = "FATAL"


@dataclass
class LogEntry:
    timestamp: datetime
    level: LogLevel
    message: str
    service: str
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    source_file: Optional[str] = None
    source_line: Optional[int] = None
    function_name: Optional[str] = None
    exception: Optional[str] = None
    stack_trace: Optional[str] = None
    tags: Optional[Dict[str, str]] = None
    fields: Optional[Dict[str, Any]] = None


class LogAggregator:
    """Enterprise log aggregator with multiple output support"""
    
    def __init__(self, service_name: str = "financial-master"):
        self.service_name = service_name
        self.logs: deque = deque(maxlen=100000)  # Keep last 100k logs
        self.buffer_size = 1000
        self.flush_interval = 30  # seconds
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self.outputs = []
        
    def add_output(self, output: 'LogOutput'):
        """Add a log output destination"""
        self.outputs.append(output)
        
    async def start(self):
        """Start log aggregation"""
        if self._running:
            return
            
        self._running = True
        self._task = asyncio.create_task(self._flush_loop())
        logger.info("Log aggregation started")
        
    async def stop(self):
        """Stop log aggregation"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        # Flush remaining logs
        await self._flush_logs()
        logger.info("Log aggregation stopped")
        
    async def log(self, level: LogLevel, message: str, **kwargs):
        """Add a log entry"""
        entry = LogEntry(
            timestamp=datetime.utcnow(),
            level=level,
            message=message,
            service=self.service_name,
            **kwargs
        )
        
        self.logs.append(entry)
        
        # Auto-flush if buffer is full
        if len(self.logs) >= self.buffer_size:
            await self._flush_logs()
            
    async def _flush_loop(self):
        """Background flush loop"""
        while self._running:
            try:
                await asyncio.sleep(self.flush_interval)
                await self._flush_logs()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in log flush loop: {e}")
                await asyncio.sleep(5)
                
    async def _flush_logs(self):
        """Flush logs to all outputs"""
        if not self.logs:
            return
            
        # Get logs to flush
        logs_to_flush = list(self.logs)
        self.logs.clear()
        
        # Send to all outputs
        for output in self.outputs:
            try:
                await output.write(logs_to_flush)
            except Exception as e:
                logger.error(f"Error flushing logs to {output.__class__.__name__}: {e}")
                
    def query_logs(self, level: Optional[LogLevel] = None,
                  service: Optional[str] = None,
                  trace_id: Optional[str] = None,
                  user_id: Optional[str] = None,
                  since: Optional[datetime] = None,
                  until: Optional[datetime] = None,
                  limit: int = 100) -> List[LogEntry]:
        """Query logs with filters"""
        results = []
        
        for entry in reversed(list(self.logs)):  # Most recent first
            if level and entry.level != level:
                continue
            if service and entry.service != service:
                continue
            if trace_id and entry.trace_id != trace_id:
                continue
            if user_id and entry.user_id != user_id:
                continue
            if since and entry.timestamp < since:
                continue
            if until and entry.timestamp > until:
                continue
                
            results.append(entry)
            
            if len(results) >= limit:
                break
                
        return results


class LogOutput:
    """Base class for log outputs"""
    
    async def write(self, logs: List[LogEntry]):
        """Write logs to output"""
        raise NotImplementedError


class ConsoleOutput(LogOutput):
    """Console log output"""
    
    def __init__(self, colored: bool = True):
        self.colored = colored
        self.colors = {
            LogLevel.TRACE: "\033[37m",    # White
            LogLevel.DEBUG: "\033[36m",    # Cyan
            LogLevel.INFO: "\033[32m",     # Green
            LogLevel.WARN: "\033[33m",     # Yellow
            LogLevel.ERROR: "\033[31m",    # Red
            LogLevel.FATAL: "\033[35m",    # Magenta
        }
        self.reset = "\033[0m"
        
    async def write(self, logs: List[LogEntry]):
        """Write logs to console"""
        for entry in logs:
            color = self.colors.get(entry.level, "") if self.colored else ""
            reset = self.reset if self.colored else ""
            
            line = f"{color}[{entry.timestamp.isoformat()}] {entry.level.value:5} [{entry.service}] {entry.message}{reset}"
            
            if entry.trace_id:
                line += f" [trace:{entry.trace_id[:8]}]"
            if entry.user_id:
                line += f" [user:{entry.user_id[:8]}]"
            if entry.exception:
                line += f"\nException: {entry.exception}"
            if entry.stack_trace:
                line += f"\nStack trace:\n{entry.stack_trace}"
                
            print(line)


class FileOutput(LogOutput):
    """File log output with rotation"""
    
    def __init__(self, file_path: str, max_size_mb: int = 100, backup_count: int = 5):
        self.file_path = Path(file_path)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.backup_count = backup_count
        self._ensure_directory()
        
    def _ensure_directory(self):
        """Ensure log directory exists"""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        
    async def write(self, logs: List[LogEntry]):
        """Write logs to file"""
        if not logs:
            return
            
        # Check if rotation is needed
        if self.file_path.exists() and self.file_path.stat().st_size > self.max_size_bytes:
            await self._rotate_files()
            
        # Write logs
        async with aiofiles.open(self.file_path, 'a') as f:
            for entry in logs:
                log_data = asdict(entry)
                log_data['timestamp'] = entry.timestamp.isoformat()
                log_data['level'] = entry.level.value
                
                await f.write(json.dumps(log_data) + '\n')
                
    async def _rotate_files(self):
        """Rotate log files"""
        if not self.file_path.exists():
            return
            
        # Remove oldest backup if needed
        oldest_backup = self.file_path.with_suffix(f".{self.backup_count}")
        if oldest_backup.exists():
            oldest_backup.unlink()
            
        # Rotate existing backups
        for i in range(self.backup_count - 1, 0, -1):
            current_backup = self.file_path.with_suffix(f".{i}")
            next_backup = self.file_path.with_suffix(f".{i + 1}")
            if current_backup.exists():
                current_backup.rename(next_backup)
                
        # Move current file to .1
        self.file_path.rename(self.file_path.with_suffix(".1"))


class ElasticsearchOutput(LogOutput):
    """Elasticsearch log output"""
    
    def __init__(self, endpoint: str = "http://localhost:9200",
                 index_prefix: str = "financial-master-logs",
                 max_batch_size: int = 100):
        self.endpoint = endpoint
        self.index_prefix = index_prefix
        self.max_batch_size = max_batch_size
        
    async def write(self, logs: List[LogEntry]):
        """Write logs to Elasticsearch"""
        if not logs:
            return
            
        # Create index name with date
        today = datetime.utcnow().strftime("%Y.%m.%d")
        index_name = f"{self.index_prefix}-{today}"
        
        # Prepare bulk request
        bulk_body = []
        for entry in logs:
            # Index action
            bulk_body.append({
                "index": {
                    "_index": index_name,
                    "_id": f"{entry.timestamp.isoformat()}-{entry.service}-{hash(entry.message)}"
                }
            })
            
            # Document
            doc = asdict(entry)
            doc['timestamp'] = entry.timestamp.isoformat()
            doc['level'] = entry.level.value
            bulk_body.append(doc)
            
        # Send bulk request
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.endpoint}/_bulk",
                    data="\n".join(json.dumps(item) for item in bulk_body) + "\n",
                    headers={"Content-Type": "application/x-ndjson"}
                ) as response:
                    if response.status not in [200, 201]:
                        error_text = await response.text()
                        logger.error(f"Failed to write logs to Elasticsearch: {response.status} - {error_text}")
                        
        except Exception as e:
            logger.error(f"Error writing logs to Elasticsearch: {e}")


class LokiOutput(LogOutput):
    """Grafana Loki log output"""
    
    def __init__(self, endpoint: str = "http://localhost:3100/loki/api/v1/push",
                 max_batch_size: int = 100):
        self.endpoint = endpoint
        self.max_batch_size = max_batch_size
        
    async def write(self, logs: List[LogEntry]):
        """Write logs to Loki"""
        if not logs:
            return
            
        # Group logs by stream labels
        streams = {}
        for entry in logs:
            labels = {
                "service": entry.service,
                "level": entry.level.value
            }
            if entry.trace_id:
                labels["trace_id"] = entry.trace_id
            if entry.user_id:
                labels["user_id"] = entry.user_id
                
            label_str = ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
            
            if label_str not in streams:
                streams[label_str] = []
                
            streams[label_str].append({
                "timestamp": int(entry.timestamp.timestamp() * 1000000000),  # nanoseconds
                "line": entry.message
            })
            
        # Prepare Loki request
        loki_data = {
            "streams": [
                {
                    "stream": dict(label.split("=") for label in label_str.split(",")),
                    "values": [[str(entry["timestamp"]), entry["line"]] for entry in entries]
                }
                for label_str, entries in streams.items()
            ]
        }
        
        # Send to Loki
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.endpoint,
                    json=loki_data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status not in [200, 204]:
                        error_text = await response.text()
                        logger.error(f"Failed to write logs to Loki: {response.status} - {error_text}")
                        
        except Exception as e:
            logger.error(f"Error writing logs to Loki: {e}")


# Global log aggregator instance
_log_aggregator = None

def get_log_aggregator() -> LogAggregator:
    """Get the global log aggregator instance"""
    global _log_aggregator
    if _log_aggregator is None:
        _log_aggregator = LogAggregator()
        # Add default outputs
        _log_aggregator.add_output(ConsoleOutput())
        try:
            _log_aggregator.add_output(FileOutput("logs/financial-master.log"))
        except Exception:
            pass
        try:
            _log_aggregator.add_output(ElasticsearchOutput())
        except Exception:
            pass
        try:
            _log_aggregator.add_output(LokiOutput())
        except Exception:
            pass
    return _log_aggregator


# Custom logging handler for integration
class StructuredLoggingHandler(logging.Handler):
    """Custom logging handler that writes to log aggregator"""
    
    def __init__(self, level: int = logging.NOTSET):
        super().__init__(level)
        self.log_aggregator = get_log_aggregator()
        
    def emit(self, record: logging.LogRecord):
        """Emit a log record"""
        try:
            # Convert log level
            level_map = {
                logging.DEBUG: LogLevel.DEBUG,
                logging.INFO: LogLevel.INFO,
                logging.WARNING: LogLevel.WARN,
                logging.ERROR: LogLevel.ERROR,
                logging.CRITICAL: LogLevel.FATAL
            }
            level = level_map.get(record.levelno, LogLevel.INFO)
            
            # Extract additional fields
            fields = {}
            for key, value in record.__dict__.items():
                if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                              'filename', 'module', 'lineno', 'funcName', 'created', 
                              'msecs', 'relativeCreated', 'thread', 'threadName', 
                              'processName', 'process', 'getMessage', 'exc_info', 
                              'exc_text', 'stack_info']:
                    fields[key] = value
                    
            # Create asyncio task for async logging
            asyncio.create_task(self.log_aggregator.log(
                level=level,
                message=record.getMessage(),
                source_file=record.pathname,
                source_line=record.lineno,
                function_name=record.funcName,
                exception=self._format_exception(record),
                stack_trace=self._format_stack_trace(record),
                fields=fields
            ))
            
        except Exception as e:
            # Fallback to standard logging
            print(f"Error in structured logging handler: {e}")
            
    def _format_exception(self, record: logging.LogRecord) -> Optional[str]:
        """Format exception from log record"""
        if record.exc_info:
            return f"{record.exc_info[0].__name__}: {record.exc_info[1]}"
        return None
        
    def _format_stack_trace(self, record: logging.LogRecord) -> Optional[str]:
        """Format stack trace from log record"""
        if record.exc_info:
            import traceback
            return "".join(traceback.format_exception(*record.exc_info))
        return None


# Convenience functions for structured logging
async def log_trace(message: str, **kwargs):
    """Log a trace message"""
    await get_log_aggregator().log(LogLevel.TRACE, message, **kwargs)
    
async def log_debug(message: str, **kwargs):
    """Log a debug message"""
    await get_log_aggregator().log(LogLevel.DEBUG, message, **kwargs)
    
async def log_info(message: str, **kwargs):
    """Log an info message"""
    await get_log_aggregator().log(LogLevel.INFO, message, **kwargs)
    
async def log_warn(message: str, **kwargs):
    """Log a warning message"""
    await get_log_aggregator().log(LogLevel.WARN, message, **kwargs)
    
async def log_error(message: str, **kwargs):
    """Log an error message"""
    await get_log_aggregator().log(LogLevel.ERROR, message, **kwargs)
    
async def log_fatal(message: str, **kwargs):
    """Log a fatal message"""
    await get_log_aggregator().log(LogLevel.FATAL, message, **kwargs)
