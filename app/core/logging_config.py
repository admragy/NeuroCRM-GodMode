"""
📊 OmniCRM Ultimate - Advanced Logging & Monitoring System
===========================================================
✅ Structured JSON Logging
✅ Performance Tracking
✅ Error Tracking (Sentry Integration)
✅ Business Metrics
✅ Request/Response Logging
✅ Audit Trail
✅ Real-Time Alerts
"""

import logging
import sys
import time
import traceback
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path
import json
from contextvars import ContextVar
from functools import wraps

# Context variables for request tracking
request_id_var: ContextVar[str] = ContextVar('request_id', default='')
user_id_var: ContextVar[str] = ContextVar('user_id', default='')
org_id_var: ContextVar[str] = ContextVar('org_id', default='')


class JSONFormatter(logging.Formatter):
    """Format logs as JSON for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add context
        request_id = request_id_var.get()
        if request_id:
            log_data["request_id"] = request_id
        
        user_id = user_id_var.get()
        if user_id:
            log_data["user_id"] = user_id
        
        org_id = org_id_var.get()
        if org_id:
            log_data["org_id"] = org_id
        
        # Add exception info
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields
        if hasattr(record, 'extra'):
            log_data.update(record.extra)
        
        return json.dumps(log_data)


class PerformanceLogger:
    """Track API performance metrics"""
    
    def __init__(self):
        self.logger = logging.getLogger("performance")
    
    def log_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        user_id: Optional[str] = None,
        org_id: Optional[str] = None
    ):
        """Log API request performance"""
        self.logger.info(
            f"API Request",
            extra={
                "event": "api_request",
                "method": method,
                "path": path,
                "status_code": status_code,
                "duration_ms": round(duration_ms, 2),
                "user_id": user_id,
                "org_id": org_id,
                "slow_request": duration_ms > 1000  # Flag slow requests
            }
        )
    
    def log_db_query(
        self,
        query: str,
        duration_ms: float,
        rows_affected: int = 0
    ):
        """Log database query performance"""
        self.logger.debug(
            f"DB Query",
            extra={
                "event": "db_query",
                "query": query[:200],  # Truncate long queries
                "duration_ms": round(duration_ms, 2),
                "rows_affected": rows_affected,
                "slow_query": duration_ms > 500
            }
        )
    
    def log_cache_operation(
        self,
        operation: str,
        key: str,
        hit: bool,
        duration_ms: float
    ):
        """Log cache operation"""
        self.logger.debug(
            f"Cache {operation}",
            extra={
                "event": "cache_operation",
                "operation": operation,
                "key": key,
                "hit": hit,
                "duration_ms": round(duration_ms, 2)
            }
        )


class AuditLogger:
    """Log security and business audit events"""
    
    def __init__(self):
        self.logger = logging.getLogger("audit")
    
    def log_login(
        self,
        user_id: str,
        email: str,
        success: bool,
        ip_address: str,
        user_agent: str
    ):
        """Log authentication attempts"""
        self.logger.info(
            f"Login {'successful' if success else 'failed'}: {email}",
            extra={
                "event": "login",
                "user_id": user_id if success else None,
                "email": email,
                "success": success,
                "ip_address": ip_address,
                "user_agent": user_agent
            }
        )
    
    def log_data_access(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        action: str,
        org_id: Optional[str] = None
    ):
        """Log data access for GDPR compliance"""
        self.logger.info(
            f"Data access: {action} {resource_type} {resource_id}",
            extra={
                "event": "data_access",
                "user_id": user_id,
                "org_id": org_id,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "action": action
            }
        )
    
    def log_permission_denied(
        self,
        user_id: str,
        resource: str,
        required_permission: str
    ):
        """Log authorization failures"""
        self.logger.warning(
            f"Permission denied: {user_id} attempted {required_permission} on {resource}",
            extra={
                "event": "permission_denied",
                "user_id": user_id,
                "resource": resource,
                "required_permission": required_permission
            }
        )
    
    def log_data_change(
        self,
        user_id: str,
        org_id: str,
        table: str,
        record_id: str,
        action: str,
        changes: Dict[str, Any]
    ):
        """Log data modifications for audit trail"""
        self.logger.info(
            f"Data change: {action} {table}/{record_id}",
            extra={
                "event": "data_change",
                "user_id": user_id,
                "org_id": org_id,
                "table": table,
                "record_id": record_id,
                "action": action,
                "changes": changes
            }
        )


class BusinessMetricsLogger:
    """Log business KPIs and metrics"""
    
    def __init__(self):
        self.logger = logging.getLogger("metrics")
    
    def log_revenue_event(
        self,
        org_id: str,
        amount: float,
        currency: str = "USD",
        source: str = "sale"
    ):
        """Log revenue generation"""
        self.logger.info(
            f"Revenue: {amount} {currency}",
            extra={
                "event": "revenue",
                "org_id": org_id,
                "amount": amount,
                "currency": currency,
                "source": source
            }
        )
    
    def log_conversion(
        self,
        org_id: str,
        customer_id: str,
        funnel_stage: str,
        value: Optional[float] = None
    ):
        """Log customer conversions"""
        self.logger.info(
            f"Conversion: {funnel_stage}",
            extra={
                "event": "conversion",
                "org_id": org_id,
                "customer_id": customer_id,
                "funnel_stage": funnel_stage,
                "value": value
            }
        )
    
    def log_campaign_performance(
        self,
        org_id: str,
        campaign_id: str,
        metric: str,
        value: float
    ):
        """Log marketing campaign metrics"""
        self.logger.info(
            f"Campaign {metric}: {value}",
            extra={
                "event": "campaign_metric",
                "org_id": org_id,
                "campaign_id": campaign_id,
                "metric": metric,
                "value": value
            }
        )


def setup_logging(
    log_level: str = "INFO",
    log_dir: str = "./logs",
    enable_json: bool = True
):
    """Configure application logging"""
    
    # Create logs directory
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    if enable_json:
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        )
    
    root_logger.addHandler(console_handler)
    
    # File handlers
    file_handlers = {
        "app": logging.FileHandler(log_path / "app.log"),
        "error": logging.FileHandler(log_path / "error.log"),
        "audit": logging.FileHandler(log_path / "audit.log"),
        "performance": logging.FileHandler(log_path / "performance.log"),
    }
    
    for handler_name, handler in file_handlers.items():
        handler.setLevel(logging.INFO if handler_name != "error" else logging.ERROR)
        handler.setFormatter(JSONFormatter() if enable_json else logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        
        if handler_name == "error":
            root_logger.addHandler(handler)
        else:
            logger = logging.getLogger(handler_name)
            logger.addHandler(handler)
    
    # Suppress noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


# Performance tracking decorator
def track_performance(operation: str):
    """Decorator to track function performance"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            perf_logger = PerformanceLogger()
            
            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                perf_logger.logger.debug(
                    f"Operation: {operation}",
                    extra={
                        "event": "operation",
                        "operation": operation,
                        "duration_ms": round(duration_ms, 2),
                        "success": True
                    }
                )
                
                return result
                
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                
                perf_logger.logger.error(
                    f"Operation failed: {operation}",
                    extra={
                        "event": "operation",
                        "operation": operation,
                        "duration_ms": round(duration_ms, 2),
                        "success": False,
                        "error": str(e)
                    }
                )
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            perf_logger = PerformanceLogger()
            
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                perf_logger.logger.debug(
                    f"Operation: {operation}",
                    extra={
                        "event": "operation",
                        "operation": operation,
                        "duration_ms": round(duration_ms, 2),
                        "success": True
                    }
                )
                
                return result
                
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                
                perf_logger.logger.error(
                    f"Operation failed: {operation}",
                    extra={
                        "event": "operation",
                        "operation": operation,
                        "duration_ms": round(duration_ms, 2),
                        "success": False,
                        "error": str(e)
                    }
                )
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Sentry integration (optional)
def setup_sentry(dsn: Optional[str] = None):
    """Initialize Sentry for error tracking"""
    if not dsn:
        return
    
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        
        sentry_sdk.init(
            dsn=dsn,
            traces_sample_rate=0.1,  # 10% of transactions
            profiles_sample_rate=0.1,
            integrations=[
                FastApiIntegration(),
                SqlalchemyIntegration(),
            ],
            environment="production",
            release="omnicrm-v7.0.0"
        )
        
        logging.info("✅ Sentry initialized")
        
    except ImportError:
        logging.warning("⚠️ Sentry SDK not installed")


# Initialize loggers
import asyncio
performance_logger = PerformanceLogger()
audit_logger = AuditLogger()
metrics_logger = BusinessMetricsLogger()
