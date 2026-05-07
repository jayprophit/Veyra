"""
MLOps Pipeline
=============
Kubeflow-style machine learning operations pipeline for financial models
"""

import asyncio
import json
import yaml
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging
import joblib
import pickle
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient

logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Model types"""
    LINEAR_REGRESSION = "linear_regression"
    RIDGE_REGRESSION = "ridge_regression"
    LASSO_REGRESSION = "lasso_regression"
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    XGBOOST = "xgboost"
    NEURAL_NETWORK = "neural_network"
    LSTM = "lstm"
    TRANSFORMER = "transformer"


class PipelineStage(Enum):
    """Pipeline stages"""
    DATA_INGESTION = "data_ingestion"
    DATA_VALIDATION = "data_validation"
    DATA_PREPROCESSING = "data_preprocessing"
    FEATURE_ENGINEERING = "feature_engineering"
    MODEL_TRAINING = "model_training"
    MODEL_VALIDATION = "model_validation"
    MODEL_DEPLOYMENT = "model_deployment"
    MONITORING = "monitoring"


@dataclass
class ModelMetrics:
    """Model performance metrics"""
    mse: float
    mae: float
    rmse: float
    r2: float
    mape: float
    training_time: float
    inference_time: float
    model_size: float
    accuracy_score: Optional[float] = None
    precision_score: Optional[float] = None
    recall_score: Optional[float] = None
    f1_score: Optional[float] = None


@dataclass
class ModelMetadata:
    """Model metadata"""
    model_id: str
    model_type: ModelType
    version: str
    created_at: datetime
    trained_at: datetime
    metrics: ModelMetrics
    hyperparameters: Dict[str, Any]
    feature_importance: Dict[str, float]
    training_data_shape: Tuple[int, int]
    validation_data_shape: Tuple[int, int]
    model_path: str
    is_deployed: bool = False
    deployment_endpoint: Optional[str] = None


@dataclass
class PipelineConfig:
    """Pipeline configuration"""
    name: str
    description: str
    schedule: str  # cron expression
    data_sources: List[str]
    target_column: str
    feature_columns: List[str]
    model_types: List[ModelType]
    validation_split: float
    test_split: float
    cross_validation_folds: int
    hyperparameter_tuning: bool
    feature_selection: bool
    monitoring_enabled: bool
    auto_deployment: bool


class MLOpsPipeline:
    """Enterprise MLOps pipeline for financial models"""
    
    def __init__(self, mlflow_tracking_uri: str = "http://localhost:5000"):
        self.mlflow_tracking_uri = mlflow_tracking_uri
        self.mlflow_client = MlflowClient(mlflow_tracking_uri)
        self.pipeline_configs: Dict[str, PipelineConfig] = {}
        self.models: Dict[str, ModelMetadata] = {}
        self.feature_store: Dict[str, pd.DataFrame] = {}
        self.experiments: Dict[str, str] = {}
        
        # Initialize MLflow
        mlflow.set_tracking_uri(mlflow_tracking_uri)
        
        # Initialize default pipeline configs
        self._initialize_default_configs()
        
    def _initialize_default_configs(self):
        """Initialize default pipeline configurations"""
        self.pipeline_configs = {
            "stock_price_prediction": PipelineConfig(
                name="Stock Price Prediction",
                description="Predict stock prices using historical data",
                schedule="0 2 * * *",  # Daily at 2 AM
                data_sources=["market_data", "technical_indicators", "sentiment_data"],
                target_column="price_change",
                feature_columns=["volume", "rsi", "macd", "bollinger_upper", "bollinger_lower", "sentiment_score"],
                model_types=[ModelType.LINEAR_REGRESSION, ModelType.RANDOM_FOREST, ModelType.GRADIENT_BOOSTING],
                validation_split=0.2,
                test_split=0.2,
                cross_validation_folds=5,
                hyperparameter_tuning=True,
                feature_selection=True,
                monitoring_enabled=True,
                auto_deployment=False
            ),
            "portfolio_optimization": PipelineConfig(
                name="Portfolio Optimization",
                description="Optimize portfolio allocation using ML",
                schedule="0 3 * * 1",  # Weekly on Monday at 3 AM
                data_sources=["portfolio_data", "market_data", "risk_factors"],
                target_column="optimal_weight",
                feature_columns=["volatility", "correlation", "beta", "sharpe_ratio", "max_drawdown"],
                model_types=[ModelType.GRADIENT_BOOSTING, ModelType.XGBOOST],
                validation_split=0.15,
                test_split=0.15,
                cross_validation_folds=3,
                hyperparameter_tuning=True,
                feature_selection=True,
                monitoring_enabled=True,
                auto_deployment=True
            ),
            "risk_assessment": PipelineConfig(
                name="Risk Assessment",
                description="Assess portfolio risk using ML models",
                schedule="0 1 * * *",  # Daily at 1 AM
                data_sources=["portfolio_data", "market_data", "macro_data"],
                target_column="risk_score",
                feature_columns=["var", "volatility", "beta", "correlation", "leverage", "liquidity"],
                model_types=[ModelType.RANDOM_FOREST, ModelType.GRADIENT_BOOSTING],
                validation_split=0.25,
                test_split=0.25,
                cross_validation_folds=5,
                hyperparameter_tuning=True,
                feature_selection=True,
                monitoring_enabled=True,
                auto_deployment=True
            )
        }
        
    async def run_pipeline(self, pipeline_name: str) -> Dict[str, Any]:
        """Run complete MLOps pipeline"""
        try:
            config = self.pipeline_configs.get(pipeline_name)
            if not config:
                raise ValueError(f"Pipeline configuration not found: {pipeline_name}")
                
            logger.info(f"Starting MLOps pipeline: {pipeline_name}")
            
            # Set up MLflow experiment
            experiment_name = f"financial_master_{pipeline_name}"
            if experiment_name not in self.experiments:
                experiment = mlflow.get_experiment_by_name(experiment_name)
                if not experiment:
                    experiment_id = mlflow.create_experiment(experiment_name)
                else:
                    experiment_id = experiment.experiment_id
                self.experiments[experiment_name] = experiment_id
            else:
                experiment_id = self.experiments[experiment_name]
                
            with mlflow.start_run(experiment_id=experiment_id, run_name=f"{pipeline_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}") as run:
                # Stage 1: Data Ingestion
                data = await self._stage_data_ingestion(config)
                mlflow.log_param("data_shape", data.shape)
                
                # Stage 2: Data Validation
                validated_data = await self._stage_data_validation(data, config)
                mlflow.log_param("validated_data_shape", validated_data.shape)
                
                # Stage 3: Data Preprocessing
                preprocessed_data = await self._stage_data_preprocessing(validated_data, config)
                mlflow.log_param("preprocessed_data_shape", preprocessed_data.shape)
                
                # Stage 4: Feature Engineering
                features = await self._stage_feature_engineering(preprocessed_data, config)
                mlflow.log_param("features_shape", features.shape)
                
                # Stage 5: Model Training
                trained_models = await self._stage_model_training(features, config)
                
                # Stage 6: Model Validation
                validated_models = await self._stage_model_validation(trained_models, features, config)
                
                # Stage 7: Model Deployment (if enabled)
                if config.auto_deployment:
                    deployed_models = await self._stage_model_deployment(validated_models, config)
                else:
                    deployed_models = validated_models
                    
                # Stage 8: Monitoring Setup
                if config.monitoring_enabled:
                    await self._stage_monitoring_setup(deployed_models, config)
                    
                # Log results
                results = {
                    "pipeline_name": pipeline_name,
                    "run_id": run.info.run_id,
                    "experiment_id": experiment_id,
                    "models_deployed": len(deployed_models),
                    "best_model": self._get_best_model(validated_models),
                    "training_time": datetime.now().isoformat(),
                    "status": "completed"
                }
                
                mlflow.log_dict(results, "pipeline_results")
                
                logger.info(f"MLOps pipeline completed: {pipeline_name}")
                return results
                
        except Exception as e:
            logger.error(f"Error running pipeline {pipeline_name}: {e}")
            raise
            
    async def _stage_data_ingestion(self, config: PipelineConfig) -> pd.DataFrame:
        """Stage 1: Data Ingestion"""
        try:
            logger.info("Stage 1: Data Ingestion")
            
            # Mock data ingestion - in production would connect to actual data sources
            data_parts = []
            
            for source in config.data_sources:
                if source == "market_data":
                    # Generate mock market data
                    dates = pd.date_range(start="2020-01-01", end="2023-12-31", freq="D")
                    market_data = pd.DataFrame({
                        "date": dates,
                        "open": np.random.uniform(100, 500, len(dates)),
                        "high": np.random.uniform(100, 500, len(dates)),
                        "low": np.random.uniform(100, 500, len(dates)),
                        "close": np.random.uniform(100, 500, len(dates)),
                        "volume": np.random.randint(1000000, 10000000, len(dates)),
                        "price_change": np.random.uniform(-0.1, 0.1, len(dates))
                    })
                    data_parts.append(market_data)
                    
                elif source == "technical_indicators":
                    # Generate mock technical indicators
                    indicators = pd.DataFrame({
                        "rsi": np.random.uniform(0, 100, len(dates)),
                        "macd": np.random.uniform(-5, 5, len(dates)),
                        "bollinger_upper": np.random.uniform(100, 500, len(dates)),
                        "bollinger_lower": np.random.uniform(100, 500, len(dates)),
                        "sentiment_score": np.random.uniform(-1, 1, len(dates))
                    })
                    data_parts.append(indicators)
                    
                elif source == "portfolio_data":
                    # Generate mock portfolio data
                    portfolio_data = pd.DataFrame({
                        "volatility": np.random.uniform(0.1, 0.5, len(dates)),
                        "correlation": np.random.uniform(-1, 1, len(dates)),
                        "beta": np.random.uniform(0.5, 2.0, len(dates)),
                        "sharpe_ratio": np.random.uniform(0.5, 3.0, len(dates)),
                        "max_drawdown": np.random.uniform(-0.3, -0.05, len(dates)),
                        "risk_score": np.random.uniform(0.1, 1.0, len(dates))
                    })
                    data_parts.append(portfolio_data)
                    
            # Combine all data
            if data_parts:
                combined_data = pd.concat(data_parts, axis=1)
                # Remove duplicate columns
                combined_data = combined_data.loc[:, ~combined_data.columns.duplicated()]
                return combined_data
            else:
                raise ValueError("No data sources available")
                
        except Exception as e:
            logger.error(f"Error in data ingestion: {e}")
            raise
            
    async def _stage_data_validation(self, data: pd.DataFrame, config: PipelineConfig) -> pd.DataFrame:
        """Stage 2: Data Validation"""
        try:
            logger.info("Stage 2: Data Validation")
            
            # Check for missing values
            missing_values = data.isnull().sum()
            if missing_values.sum() > 0:
                logger.warning(f"Missing values found: {missing_values[missing_values > 0].to_dict()}")
                
            # Check data types
            invalid_types = []
            for col in data.columns:
                if data[col].dtype == "object":
                    try:
                        pd.to_numeric(data[col])
                    except ValueError:
                        invalid_types.append(col)
                        
            if invalid_types:
                logger.warning(f"Invalid data types found: {invalid_types}")
                
            # Check for outliers
            numeric_columns = data.select_dtypes(include=[np.number]).columns
            outliers = {}
            for col in numeric_columns:
                Q1 = data[col].quantile(0.25)
                Q3 = data[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outlier_count = ((data[col] < lower_bound) | (data[col] > upper_bound)).sum()
                if outlier_count > 0:
                    outliers[col] = outlier_count
                    
            if outliers:
                logger.warning(f"Outliers detected: {outliers}")
                
            # Validate target column exists
            if config.target_column not in data.columns:
                raise ValueError(f"Target column '{config.target_column}' not found in data")
                
            # Validate feature columns exist
            missing_features = [col for col in config.feature_columns if col not in data.columns]
            if missing_features:
                logger.warning(f"Missing feature columns: {missing_features}")
                
            # Log validation results
            validation_results = {
                "total_rows": len(data),
                "total_columns": len(data.columns),
                "missing_values": missing_values.sum(),
                "outliers": sum(outliers.values()),
                "invalid_types": len(invalid_types)
            }
            mlflow.log_dict(validation_results, "data_validation")
            
            return data
            
        except Exception as e:
            logger.error(f"Error in data validation: {e}")
            raise
            
    async def _stage_data_preprocessing(self, data: pd.DataFrame, config: PipelineConfig) -> pd.DataFrame:
        """Stage 3: Data Preprocessing"""
        try:
            logger.info("Stage 3: Data Preprocessing")
            
            processed_data = data.copy()
            
            # Handle missing values
            numeric_columns = processed_data.select_dtypes(include=[np.number]).columns
            for col in numeric_columns:
                if processed_data[col].isnull().sum() > 0:
                    # Fill missing values with median
                    processed_data[col].fillna(processed_data[col].median(), inplace=True)
                    
            # Remove outliers (optional)
            for col in numeric_columns:
                Q1 = processed_data[col].quantile(0.25)
                Q3 = processed_data[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                processed_data[col] = processed_data[col].clip(lower_bound, upper_bound)
                
            # Feature scaling
            from sklearn.preprocessing import StandardScaler, MinMaxScaler
            
            # Use StandardScaler for most features
            scaler = StandardScaler()
            scaled_features = processed_data[config.feature_columns]
            scaled_features = scaler.fit_transform(scaled_features)
            processed_data[config.feature_columns] = scaled_features
            
            # Store scaler for later use
            self.feature_store[f"{config.name}_scaler"] = scaler
            
            # Log preprocessing results
            preprocessing_results = {
                "features_scaled": len(config.feature_columns),
                "missing_values_handled": True,
                "outliers_removed": True
            }
            mlflow.log_dict(preprocessing_results, "data_preprocessing")
            
            return processed_data
            
        except Exception as e:
            logger.error(f"Error in data preprocessing: {e}")
            raise
            
    async def _stage_feature_engineering(self, data: pd.DataFrame, config: PipelineConfig) -> pd.DataFrame:
        """Stage 4: Feature Engineering"""
        try:
            logger.info("Stage 4: Feature Engineering")
            
            engineered_data = data.copy()
            
            # Create interaction features
            if len(config.feature_columns) >= 2:
                for i in range(min(5, len(config.feature_columns))):
                    for j in range(i+1, min(5, len(config.feature_columns))):
                        col1 = config.feature_columns[i]
                        col2 = config.feature_columns[j]
                        if col1 in engineered_data.columns and col2 in engineered_data.columns:
                            engineered_data[f"{col1}_x_{col2}"] = engineered_data[col1] * engineered_data[col2]
                            
            # Create polynomial features for important features
            important_features = config.feature_columns[:3]  # Top 3 features
            for col in important_features:
                if col in engineered_data.columns:
                    engineered_data[f"{col}_squared"] = engineered_data[col] ** 2
                    engineered_data[f"{col}_cubed"] = engineered_data[col] ** 3
                    
            # Create lag features for time series data
            if "date" in engineered_data.columns:
                engineered_data = engineered_data.sort_values("date")
                for col in config.feature_columns[:5]:  # Top 5 features
                    if col in engineered_data.columns:
                        engineered_data[f"{col}_lag_1"] = engineered_data[col].shift(1)
                        engineered_data[f"{col}_lag_7"] = engineered_data[col].shift(7)
                        
            # Create rolling features
            for col in config.feature_columns[:3]:  # Top 3 features
                if col in engineered_data.columns:
                    engineered_data[f"{col}_rolling_mean_7"] = engineered_data[col].rolling(window=7).mean()
                    engineered_data[f"{col}_rolling_std_7"] = engineered_data[col].rolling(window=7).std()
                    
            # Remove rows with NaN values created by lag/rolling features
            engineered_data.dropna(inplace=True)
            
            # Update feature columns
            all_feature_columns = [col for col in engineered_data.columns if col != config.target_column]
            
            # Log feature engineering results
            feature_engineering_results = {
                "original_features": len(config.feature_columns),
                "engineered_features": len(all_feature_columns),
                "interaction_features": len([col for col in engineered_data.columns if "_x_" in col]),
                "polynomial_features": len([col for col in engineered_data.columns if "_squared" in col]),
                "lag_features": len([col for col in engineered_data.columns if "_lag_" in col]),
                "rolling_features": len([col for col in engineered_data.columns if "_rolling_" in col])
            }
            mlflow.log_dict(feature_engineering_results, "feature_engineering")
            
            return engineered_data
            
        except Exception as e:
            logger.error(f"Error in feature engineering: {e}")
            raise
            
    async def _stage_model_training(self, data: pd.DataFrame, config: PipelineConfig) -> List[ModelMetadata]:
        """Stage 5: Model Training"""
        try:
            logger.info("Stage 5: Model Training")
            
            # Prepare data
            X = data.drop(columns=[config.target_column])
            y = data[config.target_column]
            
            # Split data
            X_train, X_temp, y_train, y_temp = train_test_split(
                X, y, test_size=config.validation_split + config.test_split, random_state=42
            )
            X_val, X_test, y_val, y_test = train_test_split(
                X_temp, y_temp, test_size=config.test_split / (config.validation_split + config.test_split), random_state=42
            )
            
            trained_models = []
            
            for model_type in config.model_types:
                logger.info(f"Training {model_type.value} model")
                
                with mlflow.start_run(nested=True, run_name=f"{model_type.value}_training"):
                    # Get model and hyperparameters
                    model, hyperparameters = self._get_model_and_hyperparameters(model_type)
                    
                    # Hyperparameter tuning if enabled
                    if config.hyperparameter_tuning:
                        model = self._hyperparameter_tuning(model, hyperparameters, X_train, y_train)
                        
                    # Train model
                    start_time = datetime.now()
                    model.fit(X_train, y_train)
                    training_time = (datetime.now() - start_time).total_seconds()
                    
                    # Calculate metrics
                    y_pred = model.predict(X_val)
                    metrics = self._calculate_metrics(y_val, y_pred, training_time, model)
                    
                    # Feature importance
                    feature_importance = self._get_feature_importance(model, X.columns)
                    
                    # Create model metadata
                    model_metadata = ModelMetadata(
                        model_id=f"{config.name}_{model_type.value}_{int(datetime.now().timestamp())}",
                        model_type=model_type,
                        version="1.0",
                        created_at=datetime.now(),
                        trained_at=datetime.now(),
                        metrics=metrics,
                        hyperparameters=hyperparameters,
                        feature_importance=feature_importance,
                        training_data_shape=X_train.shape,
                        validation_data_shape=X_val.shape,
                        model_path=f"models/{config.name}/{model_type.value}.pkl"
                    )
                    
                    # Log to MLflow
                    mlflow.log_params(hyperparameters)
                    mlflow.log_metrics({
                        "mse": metrics.mse,
                        "mae": metrics.mae,
                        "rmse": metrics.rmse,
                        "r2": metrics.r2,
                        "training_time": metrics.training_time
                    })
                    
                    # Save model
                    model_path = f"models/{config.name}/{model_type.value}.pkl"
                    joblib.dump(model, model_path)
                    
                    trained_models.append(model_metadata)
                    
            return trained_models
            
        except Exception as e:
            logger.error(f"Error in model training: {e}")
            raise
            
    def _get_model_and_hyperparameters(self, model_type: ModelType) -> Tuple[Any, Dict[str, Any]]:
        """Get model and hyperparameters"""
        if model_type == ModelType.LINEAR_REGRESSION:
            return LinearRegression(), {"fit_intercept": True}
        elif model_type == ModelType.RIDGE_REGRESSION:
            return Ridge(), {"alpha": [0.1, 1.0, 10.0]}
        elif model_type == ModelType.LASSO_REGRESSION:
            return Lasso(), {"alpha": [0.1, 1.0, 10.0]}
        elif model_type == ModelType.RANDOM_FOREST:
            return RandomForestRegressor(random_state=42), {
                "n_estimators": [100, 200],
                "max_depth": [10, 20, None],
                "min_samples_split": [2, 5]
            }
        elif model_type == ModelType.GRADIENT_BOOSTING:
            return GradientBoostingRegressor(random_state=42), {
                "n_estimators": [100, 200],
                "learning_rate": [0.01, 0.1],
                "max_depth": [3, 5, 7]
            }
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
            
    def _hyperparameter_tuning(self, model: Any, hyperparameters: Dict[str, Any], X_train: pd.DataFrame, y_train: pd.Series) -> Any:
        """Perform hyperparameter tuning"""
        try:
            # Convert hyperparameters to GridSearchCV format
            param_grid = {}
            for key, value in hyperparameters.items():
                if isinstance(value, list) and len(value) > 1:
                    param_grid[key] = value
                    
            if param_grid:
                grid_search = GridSearchCV(
                    model, param_grid, cv=3, scoring="neg_mean_squared_error", n_jobs=-1
                )
                grid_search.fit(X_train, y_train)
                return grid_search.best_estimator_
            else:
                return model
                
        except Exception as e:
            logger.error(f"Error in hyperparameter tuning: {e}")
            return model
            
    def _calculate_metrics(self, y_true: np.ndarray, y_pred: np.ndarray, training_time: float, model: Any) -> ModelMetrics:
        """Calculate model metrics"""
        try:
            mse = mean_squared_error(y_true, y_pred)
            mae = mean_absolute_error(y_true, y_pred)
            rmse = np.sqrt(mse)
            r2 = r2_score(y_true, y_pred)
            
            # Calculate MAPE (Mean Absolute Percentage Error)
            mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
            
            # Calculate inference time
            start_time = datetime.now()
            _ = model.predict(y_true[:1].reshape(1, -1))  # Single prediction
            inference_time = (datetime.now() - start_time).total_seconds()
            
            # Calculate model size
            model_size = len(pickle.dumps(model)) / (1024 * 1024)  # MB
            
            return ModelMetrics(
                mse=mse,
                mae=mae,
                rmse=rmse,
                r2=r2,
                mape=mape,
                training_time=training_time,
                inference_time=inference_time,
                model_size=model_size
            )
            
        except Exception as e:
            logger.error(f"Error calculating metrics: {e}")
            raise
            
    def _get_feature_importance(self, model: Any, feature_names: List[str]) -> Dict[str, float]:
        """Get feature importance"""
        try:
            if hasattr(model, 'feature_importances_'):
                importances = model.feature_importances_
                return dict(zip(feature_names, importances))
            elif hasattr(model, 'coef_'):
                coefficients = np.abs(model.coef_)
                return dict(zip(feature_names, coefficients))
            else:
                return {}
        except Exception as e:
            logger.error(f"Error getting feature importance: {e}")
            return {}
            
    async def _stage_model_validation(self, models: List[ModelMetadata], features: pd.DataFrame, config: PipelineConfig) -> List[ModelMetadata]:
        """Stage 6: Model Validation"""
        try:
            logger.info("Stage 6: Model Validation")
            
            # Prepare test data
            X = features.drop(columns=[config.target_column])
            y = features[config.target_column]
            
            _, _, X_test, y_test = train_test_split(
                X, y, test_size=config.test_split, random_state=42
            )
            
            validated_models = []
            
            for model_metadata in models:
                # Load model
                model = joblib.load(model_metadata.model_path)
                
                # Predict on test set
                y_pred = model.predict(X_test)
                
                # Calculate test metrics
                test_metrics = self._calculate_metrics(y_test, y_pred, 0, model)
                
                # Update model metadata with test metrics
                model_metadata.metrics = test_metrics
                
                # Log test metrics
                mlflow.log_metrics({
                    f"test_mse": test_metrics.mse,
                    f"test_mae": test_metrics.mae,
                    f"test_rmse": test_metrics.rmse,
                    f"test_r2": test_metrics.r2
                })
                
                validated_models.append(model_metadata)
                
            return validated_models
            
        except Exception as e:
            logger.error(f"Error in model validation: {e}")
            raise
            
    async def _stage_model_deployment(self, models: List[ModelMetadata], config: PipelineConfig) -> List[ModelMetadata]:
        """Stage 7: Model Deployment"""
        try:
            logger.info("Stage 7: Model Deployment")
            
            # Select best model
            best_model = self._get_best_model(models)
            
            # Deploy best model
            best_model.is_deployed = True
            best_model.deployment_endpoint = f"/api/v1/models/{best_model.model_id}/predict"
            
            # Store deployed model
            self.models[best_model.model_id] = best_model
            
            # Log deployment
            mlflow.log_dict({
                "deployed_model": best_model.model_id,
                "deployment_endpoint": best_model.deployment_endpoint,
                "deployment_time": datetime.now().isoformat()
            }, "model_deployment")
            
            return [best_model]
            
        except Exception as e:
            logger.error(f"Error in model deployment: {e}")
            raise
            
    async def _stage_monitoring_setup(self, models: List[ModelMetadata], config: PipelineConfig):
        """Stage 8: Monitoring Setup"""
        try:
            logger.info("Stage 8: Monitoring Setup")
            
            # Set up monitoring for deployed models
            for model in models:
                if model.is_deployed:
                    # Create monitoring configuration
                    monitoring_config = {
                        "model_id": model.model_id,
                        "metrics_to_track": ["mse", "mae", "rmse", "r2"],
                        "alert_thresholds": {
                            "mse": model.metrics.mse * 1.5,
                            "r2": model.metrics.r2 * 0.8
                        },
                        "monitoring_frequency": "hourly",
                        "data_drift_detection": True,
                        "model_performance_tracking": True
                    }
                    
                    # Store monitoring config
                    mlflow.log_dict(monitoring_config, f"monitoring_{model.model_id}")
                    
            logger.info("Monitoring setup completed")
            
        except Exception as e:
            logger.error(f"Error in monitoring setup: {e}")
            raise
            
    def _get_best_model(self, models: List[ModelMetadata]) -> ModelMetadata:
        """Get best model based on metrics"""
        if not models:
            raise ValueError("No models provided")
            
        # Sort by R2 score (higher is better)
        best_model = max(models, key=lambda m: m.metrics.r2)
        return best_model
        
    def get_pipeline_status(self, pipeline_name: str) -> Dict[str, Any]:
        """Get pipeline status"""
        config = self.pipeline_configs.get(pipeline_name)
        if not config:
            return {"error": f"Pipeline not found: {pipeline_name}"}
            
        deployed_models = [m for m in self.models.values() if m.model_id.startswith(pipeline_name) and m.is_deployed]
        
        return {
            "pipeline_name": pipeline_name,
            "config": asdict(config),
            "deployed_models": len(deployed_models),
            "last_run": datetime.now().isoformat(),
            "status": "active"
        }
        
    def get_model_predictions(self, model_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get predictions from deployed model"""
        try:
            model_metadata = self.models.get(model_id)
            if not model_metadata or not model_metadata.is_deployed:
                raise ValueError(f"Model not found or not deployed: {model_id}")
                
            # Load model
            model = joblib.load(model_metadata.model_path)
            
            # Prepare input data
            input_df = pd.DataFrame([input_data])
            
            # Apply preprocessing
            scaler = self.feature_store.get(f"{model_metadata.model_id.split('_')[0]}_scaler")
            if scaler:
                input_df[model_metadata.feature_importance.keys()] = scaler.transform(input_df[model_metadata.feature_importance.keys()])
                
            # Make prediction
            prediction = model.predict(input_df)[0]
            
            return {
                "model_id": model_id,
                "prediction": float(prediction),
                "timestamp": datetime.now().isoformat(),
                "confidence": 0.95  # Mock confidence score
            }
            
        except Exception as e:
            logger.error(f"Error getting predictions: {e}")
            raise


# Global MLOps pipeline instance
_mlops_pipeline = None

def get_mlops_pipeline() -> MLOpsPipeline:
    """Get the global MLOps pipeline instance"""
    global _mlops_pipeline
    if _mlops_pipeline is None:
        _mlops_pipeline = MLOpsPipeline()
    return _mlops_pipeline
