"""ETL Data Pipeline for Financial Data Processing."""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import json

logger = logging.getLogger(__name__)

class DataSource(Enum):
    BLOOMBERG = "bloomberg"
    REUTERS = "reuters"
    ALPACA = "alpaca"
    POLYGON = "polygon"
    COINBASE = "coinbase"
    BINANCE = "binance"
    KRAKEN = "kraken"
    CUSTOM = "custom"

class DataType(Enum):
    MARKET_DATA = "market_data"
    NEWS = "news"
    FUNDAMENTALS = "fundamentals"
    ALTERNATIVE = "alternative"
    ONCHAIN = "onchain"

@dataclass
class ETLJob:
    job_id: str
    source: DataSource
    data_type: DataType
    symbol: str
    start_date: datetime
    end_date: datetime
    status: str
    records_processed: int
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

class DataPipeline:
    """
    Enterprise-grade ETL pipeline for financial data ingestion.
    Supports multiple sources, transformations, and loading destinations.
    """
    
    def __init__(self):
        self.active_jobs: Dict[str, ETLJob] = {}
        self.job_history: List[ETLJob] = []
        self.transformers: Dict[str, Callable] = {}
        self.connectors: Dict[DataSource, Any] = {}
        self.data_quality_rules: Dict[str, Callable] = {}
        self.batch_size = 1000
        
        # Data lineage tracking
        self.data_lineage: Dict[str, List[Dict]] = {}
        
    async def register_connector(self, source: DataSource, connector: Any):
        """Register data source connector."""
        self.connectors[source] = connector
        logger.info(f"Connector registered: {source.value}")
    
    async def create_etl_job(self,
                            source: str,
                            data_type: str,
                            symbol: str,
                            start_date: str,
                            end_date: str) -> ETLJob:
        """Create new ETL job."""
        job_id = f"etl_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        job = ETLJob(
            job_id=job_id,
            source=DataSource(source),
            data_type=DataType(data_type),
            symbol=symbol,
            start_date=datetime.fromisoformat(start_date),
            end_date=datetime.fromisoformat(end_date),
            status="pending",
            records_processed=0,
            created_at=datetime.now()
        )
        
        self.active_jobs[job_id] = job
        logger.info(f"ETL job created: {job_id} for {symbol}")
        return job
    
    async def run_etl_job(self, job_id: str) -> ETLJob:
        """Execute ETL job."""
        if job_id not in self.active_jobs:
            raise ValueError(f"Job not found: {job_id}")
        
        job = self.active_jobs[job_id]
        job.status = "running"
        
        try:
            # Extract
            raw_data = await self._extract(job)
            
            # Validate data quality
            quality_check = await self._validate_quality(raw_data)
            if not quality_check['passed']:
                job.status = "failed"
                job.error_message = f"Data quality check failed: {quality_check['issues']}"
                return job
            
            # Transform
            transformed_data = await self._transform(raw_data, job.data_type)
            
            # Load
            records_loaded = await self._load(transformed_data, job)
            
            job.records_processed = records_loaded
            job.status = "completed"
            job.completed_at = datetime.now()
            
            # Track lineage
            self._track_lineage(job, raw_data, transformed_data)
            
            logger.info(f"ETL job completed: {job_id} - {records_loaded} records")
            
        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            logger.error(f"ETL job failed: {job_id} - {e}")
        
        self.job_history.append(job)
        return job
    
    async def _extract(self, job: ETLJob) -> List[Dict]:
        """Extract data from source."""
        # Simulate data extraction
        # In production, use actual API connectors
        
        days = (job.end_date - job.start_date).days
        records = []
        
        for i in range(days):
            date = job.start_date + timedelta(days=i)
            records.append({
                'symbol': job.symbol,
                'date': date.isoformat(),
                'open': 100.0 + i * 0.1,
                'high': 101.0 + i * 0.1,
                'low': 99.0 + i * 0.1,
                'close': 100.5 + i * 0.1,
                'volume': 1000000 + i * 1000,
                'source': job.source.value
            })
        
        return records
    
    async def _validate_quality(self, data: List[Dict]) -> Dict[str, Any]:
        """Validate data quality."""
        issues = []
        
        for record in data:
            # Check for missing values
            for key, value in record.items():
                if value is None or value == '':
                    issues.append(f"Missing {key} in {record.get('date', 'unknown')}")
            
            # Check for outliers
            if 'volume' in record and record['volume'] < 0:
                issues.append(f"Negative volume in {record.get('date', 'unknown')}")
            
            if 'close' in record:
                if record['close'] <= 0:
                    issues.append(f"Invalid close price in {record.get('date', 'unknown')}")
        
        return {
            'passed': len(issues) == 0,
            'issues': issues[:10],  # Limit issues reported
            'total_records': len(data)
        }
    
    async def _transform(self, data: List[Dict], data_type: DataType) -> List[Dict]:
        """Transform data based on type."""
        transformed = []
        
        for record in data:
            # Standard transformation
            transformed_record = {
                'symbol': record['symbol'],
                'timestamp': record['date'],
                'open': float(record['open']),
                'high': float(record['high']),
                'low': float(record['low']),
                'close': float(record['close']),
                'volume': int(record['volume']),
                'vwap': (record['high'] + record['low'] + record['close']) / 3,
                'range': record['high'] - record['low'],
                'processed_at': datetime.now().isoformat()
            }
            
            # Calculate returns
            if len(transformed) > 0:
                prev_close = transformed[-1]['close']
                transformed_record['return'] = (transformed_record['close'] - prev_close) / prev_close
            else:
                transformed_record['return'] = 0.0
            
            transformed.append(transformed_record)
        
        return transformed
    
    async def _load(self, data: List[Dict], job: ETLJob) -> int:
        """Load data to destination."""
        # In production: load to timeseries database
        logger.info(f"Loading {len(data)} records to database")
        return len(data)
    
    def _track_lineage(self, job: ETLJob, raw: List[Dict], transformed: List[Dict]):
        """Track data lineage."""
        self.data_lineage[job.job_id] = [{
            'stage': 'extract',
            'records': len(raw),
            'timestamp': datetime.now().isoformat()
        }, {
            'stage': 'transform',
            'records': len(transformed),
            'timestamp': datetime.now().isoformat()
        }]
    
    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get ETL job status."""
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
        else:
            job = next((j for j in self.job_history if j.job_id == job_id), None)
        
        if not job:
            return {'error': 'Job not found'}
        
        return {
            'job_id': job.job_id,
            'status': job.status,
            'symbol': job.symbol,
            'source': job.source.value,
            'data_type': job.data_type.value,
            'records_processed': job.records_processed,
            'created_at': job.created_at.isoformat(),
            'completed_at': job.completed_at.isoformat() if job.completed_at else None,
            'error_message': job.error_message,
            'lineage': self.data_lineage.get(job_id, [])
        }
    
    async def list_jobs(self, status: Optional[str] = None) -> List[Dict]:
        """List ETL jobs with optional filtering."""
        jobs = list(self.active_jobs.values()) + self.job_history
        
        if status:
            jobs = [j for j in jobs if j.status == status]
        
        return [{
            'job_id': j.job_id,
            'status': j.status,
            'symbol': j.symbol,
            'records_processed': j.records_processed
        } for j in jobs[-50:]]  # Return last 50

etl_pipeline = DataPipeline()
