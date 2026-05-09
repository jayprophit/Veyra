"""
STACH Schema Integration for Financial Master

This module provides integration with FactSet's STACH schema for:
- Standardized financial data visualization
- Table and chart data structures
- Consistent data formatting
- Cross-platform compatibility
- Enterprise-grade reporting
"""

import json
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, date
from decimal import Decimal
from enum import Enum

logger = logging.getLogger(__name__)


class DataType(Enum):
    """STACH data types"""
    STRING = "string"
    INTEGER = "integer"
    DECIMAL = "decimal"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    TIME = "time"


class ColumnType(Enum):
    """STACH column types"""
    VALUE = "value"
    METRIC = "metric"
    DIMENSION = "dimension"
    ATTRIBUTE = "attribute"


@dataclass
class ColumnDefinition:
    """STACH column definition"""
    id: str
    name: str
    type: DataType
    column_type: ColumnType
    description: Optional[str] = None
    format: Optional[str] = None
    currency: Optional[str] = None
    decimals: Optional[int] = None


@dataclass
class Row:
    """STACH row data"""
    values: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class Table:
    """STACH table structure"""
    id: str
    name: str
    description: Optional[str]
    columns: List[ColumnDefinition]
    rows: List[Row]
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ChartSeries:
    """STACH chart series"""
    id: str
    name: str
    data: List[Dict[str, Any]]
    type: str  # line, bar, candlestick, etc.
    color: Optional[str] = None
    y_axis: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class Chart:
    """STACH chart structure"""
    id: str
    name: str
    title: Optional[str]
    type: str  # line, bar, pie, scatter, etc.
    series: List[ChartSeries]
    x_axis: Dict[str, Any]
    y_axis: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


class STACHSchemaProcessor:
    """Main STACH schema processor for Financial Master"""
    
    def __init__(self):
        self.schema_version = "1.0"
        self.default_currency = "USD"
    
    def create_table_from_market_data(self, market_data: List[Dict[str, Any]], 
                                    table_name: str = "market_data") -> Table:
        """Create STACH table from market data"""
        if not market_data:
            return Table(id=table_name, name=table_name, description="Empty market data table", 
                      columns=[], rows=[])
        
        # Define columns based on market data structure
        columns = [
            ColumnDefinition(
                id="symbol",
                name="Symbol",
                type=DataType.STRING,
                column_type=ColumnType.DIMENSION,
                description="Trading symbol"
            ),
            ColumnDefinition(
                id="timestamp",
                name="Timestamp",
                type=DataType.DATETIME,
                column_type=ColumnType.DIMENSION,
                description="Data timestamp"
            ),
            ColumnDefinition(
                id="price",
                name="Price",
                type=DataType.DECIMAL,
                column_type=ColumnType.VALUE,
                description="Last price",
                currency=self.default_currency,
                decimals=4
            ),
            ColumnDefinition(
                id="volume",
                name="Volume",
                type=DataType.INTEGER,
                column_type=ColumnType.VALUE,
                description="Trading volume"
            ),
            ColumnDefinition(
                id="bid",
                name="Bid",
                type=DataType.DECIMAL,
                column_type=ColumnType.VALUE,
                description="Bid price",
                currency=self.default_currency,
                decimals=4
            ),
            ColumnDefinition(
                id="ask",
                name="Ask",
                type=DataType.DECIMAL,
                column_type=ColumnType.VALUE,
                description="Ask price",
                currency=self.default_currency,
                decimals=4
            ),
            ColumnDefinition(
                id="high",
                name="High",
                type=DataType.DECIMAL,
                column_type=ColumnType.VALUE,
                description="Daily high",
                currency=self.default_currency,
                decimals=4
            ),
            ColumnDefinition(
                id="low",
                name="Low",
                type=DataType.DECIMAL,
                column_type=ColumnType.VALUE,
                description="Daily low",
                currency=self.default_currency,
                decimals=4
            )
        ]
        
        # Create rows
        rows = []
        for data_point in market_data:
            row_values = {
                "symbol": data_point.get("symbol", ""),
                "timestamp": data_point.get("timestamp", datetime.now()),
                "price": self._convert_to_decimal(data_point.get("price", 0)),
                "volume": int(data_point.get("volume", 0)),
                "bid": self._convert_to_decimal(data_point.get("bid", 0)),
                "ask": self._convert_to_decimal(data_point.get("ask", 0)),
                "high": self._convert_to_decimal(data_point.get("high", 0)),
                "low": self._convert_to_decimal(data_point.get("low", 0))
            }
            rows.append(Row(values=row_values))
        
        return Table(
            id=table_name,
            name=table_name,
            description="Market data table with OHLCV information",
            columns=columns,
            rows=rows,
            metadata={
                "schema_version": self.schema_version,
                "created_at": datetime.now().isoformat(),
                "currency": self.default_currency
            }
        )
    
    def create_table_from_portfolio_analytics(self, analytics_data: Dict[str, Any], 
                                           table_name: str = "portfolio_analytics") -> Table:
        """Create STACH table from portfolio analytics data"""
        columns = [
            ColumnDefinition(
                id="metric",
                name="Metric",
                type=DataType.STRING,
                column_type=ColumnType.DIMENSION,
                description="Portfolio metric name"
            ),
            ColumnDefinition(
                id="value",
                name="Value",
                type=DataType.DECIMAL,
                column_type=ColumnType.VALUE,
                description="Metric value",
                decimals=4
            ),
            ColumnDefinition(
                id="benchmark",
                name="Benchmark",
                type=DataType.DECIMAL,
                column_type=ColumnType.VALUE,
                description="Benchmark value",
                decimals=4
            ),
            ColumnDefinition(
                id="difference",
                name="Difference",
                type=DataType.DECIMAL,
                column_type=ColumnType.VALUE,
                description="Difference from benchmark",
                decimals=4
            )
        ]
        
        rows = []
        for metric_name, metric_data in analytics_data.items():
            if isinstance(metric_data, dict):
                value = metric_data.get("value", 0)
                benchmark = metric_data.get("benchmark", 0)
                difference = value - benchmark
            else:
                value = metric_data
                benchmark = 0
                difference = value
            
            row_values = {
                "metric": metric_name,
                "value": self._convert_to_decimal(value),
                "benchmark": self._convert_to_decimal(benchmark),
                "difference": self._convert_to_decimal(difference)
            }
            rows.append(Row(values=row_values))
        
        return Table(
            id=table_name,
            name=table_name,
            description="Portfolio analytics metrics",
            columns=columns,
            rows=rows,
            metadata={
                "schema_version": self.schema_version,
                "created_at": datetime.now().isoformat()
            }
        )
    
    def create_chart_from_timeseries(self, timeseries_data: List[Dict[str, Any]], 
                                   chart_name: str = "timeseries_chart") -> Chart:
        """Create STACH chart from time series data"""
        # Extract series data
        series_data = {}
        for data_point in timeseries_data:
            timestamp = data_point.get("timestamp")
            if timestamp:
                for key, value in data_point.items():
                    if key != "timestamp":
                        if key not in series_data:
                            series_data[key] = []
                        series_data[key].append({
                            "x": timestamp,
                            "y": self._convert_to_decimal(value)
                        })
        
        # Create chart series
        series = []
        colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
        for i, (series_name, data) in enumerate(series_data.items()):
            chart_series = ChartSeries(
                id=f"series_{i}",
                name=series_name,
                data=data,
                type="line",
                color=colors[i % len(colors)]
            )
            series.append(chart_series)
        
        return Chart(
            id=chart_name,
            name=chart_name,
            title="Time Series Chart",
            type="line",
            series=series,
            x_axis={
                "type": "datetime",
                "label": "Time"
            },
            y_axis={
                "type": "linear",
                "label": "Value"
            },
            metadata={
                "schema_version": self.schema_version,
                "created_at": datetime.now().isoformat()
            }
        )
    
    def create_chart_from_portfolio_allocation(self, allocation_data: Dict[str, float], 
                                           chart_name: str = "allocation_chart") -> Chart:
        """Create STACH pie chart from portfolio allocation data"""
        series_data = [
            {
                "x": category,
                "y": self._convert_to_decimal(percentage)
            }
            for category, percentage in allocation_data.items()
        ]
        
        series = [
            ChartSeries(
                id="allocation_series",
                name="Portfolio Allocation",
                data=series_data,
                type="pie"
            )
        ]
        
        return Chart(
            id=chart_name,
            name=chart_name,
            title="Portfolio Allocation",
            type="pie",
            series=series,
            x_axis={
                "type": "category",
                "label": "Category"
            },
            y_axis={
                "type": "percentage",
                "label": "Allocation"
            },
            metadata={
                "schema_version": self.schema_version,
                "created_at": datetime.now().isoformat()
            }
        )
    
    def table_to_json(self, table: Table) -> Dict[str, Any]:
        """Convert STACH table to JSON format"""
        return {
            "id": table.id,
            "name": table.name,
            "description": table.description,
            "schema_version": self.schema_version,
            "columns": [
                {
                    "id": col.id,
                    "name": col.name,
                    "type": col.type.value,
                    "column_type": col.column_type.value,
                    "description": col.description,
                    "format": col.format,
                    "currency": col.currency,
                    "decimals": col.decimals
                }
                for col in table.columns
            ],
            "rows": [
                {
                    "values": row.values,
                    "metadata": row.metadata
                }
                for row in table.rows
            ],
            "metadata": table.metadata
        }
    
    def chart_to_json(self, chart: Chart) -> Dict[str, Any]:
        """Convert STACH chart to JSON format"""
        return {
            "id": chart.id,
            "name": chart.name,
            "title": chart.title,
            "type": chart.type,
            "schema_version": self.schema_version,
            "series": [
                {
                    "id": series.id,
                    "name": series.name,
                    "data": series.data,
                    "type": series.type,
                    "color": series.color,
                    "y_axis": series.y_axis,
                    "metadata": series.metadata
                }
                for series in chart.series
            ],
            "x_axis": chart.x_axis,
            "y_axis": chart.y_axis,
            "metadata": chart.metadata
        }
    
    def validate_table(self, table: Table) -> List[str]:
        """Validate STACH table structure"""
        errors = []
        
        # Check required fields
        if not table.id:
            errors.append("Table ID is required")
        
        if not table.name:
            errors.append("Table name is required")
        
        if not table.columns:
            errors.append("Table must have at least one column")
        
        # Validate columns
        column_ids = set()
        for col in table.columns:
            if not col.id:
                errors.append("Column ID is required")
            elif col.id in column_ids:
                errors.append(f"Duplicate column ID: {col.id}")
            else:
                column_ids.add(col.id)
            
            if not col.name:
                errors.append("Column name is required")
            
            if not isinstance(col.type, DataType):
                errors.append(f"Invalid data type for column {col.id}")
        
        # Validate rows
        for row in table.rows:
            if not row.values:
                errors.append("Row values are required")
                continue
            
            # Check that all required columns have values
            for col in table.columns:
                if col.id not in row.values:
                    errors.append(f"Missing value for column {col.id} in row")
        
        return errors
    
    def validate_chart(self, chart: Chart) -> List[str]:
        """Validate STACH chart structure"""
        errors = []
        
        # Check required fields
        if not chart.id:
            errors.append("Chart ID is required")
        
        if not chart.name:
            errors.append("Chart name is required")
        
        if not chart.type:
            errors.append("Chart type is required")
        
        if not chart.series:
            errors.append("Chart must have at least one series")
        
        # Validate series
        series_ids = set()
        for series in chart.series:
            if not series.id:
                errors.append("Series ID is required")
            elif series.id in series_ids:
                errors.append(f"Duplicate series ID: {series.id}")
            else:
                series_ids.add(series.id)
            
            if not series.name:
                errors.append("Series name is required")
            
            if not series.data:
                errors.append(f"Series {series.id} must have data")
        
        return errors
    
    def _convert_to_decimal(self, value: Any) -> Decimal:
        """Convert value to Decimal for precision"""
        if isinstance(value, Decimal):
            return value
        try:
            return Decimal(str(value))
        except (ValueError, TypeError):
            return Decimal('0')
    
    def merge_tables(self, tables: List[Table], merged_table_name: str = "merged_table") -> Table:
        """Merge multiple STACH tables"""
        if not tables:
            return Table(id=merged_table_name, name=merged_table_name, 
                      description="Empty merged table", columns=[], rows=[])
        
        # Merge columns (avoid duplicates)
        all_columns = {}
        for table in tables:
            for col in table.columns:
                if col.id not in all_columns:
                    all_columns[col.id] = col
        
        # Merge rows
        all_rows = []
        for table in tables:
            all_rows.extend(table.rows)
        
        return Table(
            id=merged_table_name,
            name=merged_table_name,
            description=f"Merged table from {len(tables)} sources",
            columns=list(all_columns.values()),
            rows=all_rows,
            metadata={
                "schema_version": self.schema_version,
                "created_at": datetime.now().isoformat(),
                "source_tables": [table.id for table in tables]
            }
        )


# Singleton instance
_stach_processor = None

def get_stach_processor() -> STACHSchemaProcessor:
    """Get or create STACH schema processor singleton"""
    global _stach_processor
    if _stach_processor is None:
        _stach_processor = STACHSchemaProcessor()
    return _stach_processor
