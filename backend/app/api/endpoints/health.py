from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
import sys
import os
import psutil

from app.db.session import get_sync_db
from app.core.logging import logger

router = APIRouter()

@router.get("/health")
async def health_check(db: Session = Depends(get_sync_db)) -> Dict[str, Any]:
    """
    Comprehensive health check endpoint for monitoring and debugging
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "checks": {}
    }
    
    overall_healthy = True
    
    # 1. Database connectivity check
    try:
        result = db.execute(text("SELECT 1")).scalar()
        if result == 1:
            health_status["checks"]["database"] = {
                "status": "healthy",
                "message": "Database connection successful"
            }
        else:
            health_status["checks"]["database"] = {
                "status": "unhealthy",
                "message": "Database query returned unexpected result"
            }
            overall_healthy = False
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }
        overall_healthy = False
    
    # 2. Memory usage check
    try:
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        if memory_percent < 80:
            memory_status = "healthy"
        elif memory_percent < 90:
            memory_status = "warning"
        else:
            memory_status = "critical"
            overall_healthy = False
            
        health_status["checks"]["memory"] = {
            "status": memory_status,
            "usage_percent": memory_percent,
            "available_gb": round(memory.available / (1024**3), 2),
            "total_gb": round(memory.total / (1024**3), 2)
        }
    except Exception as e:
        health_status["checks"]["memory"] = {
            "status": "unknown",
            "message": f"Memory check failed: {str(e)}"
        }
    
    # 3. Disk space check
    try:
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        
        if disk_percent < 80:
            disk_status = "healthy"
        elif disk_percent < 90:
            disk_status = "warning"
        else:
            disk_status = "critical"
            overall_healthy = False
            
        health_status["checks"]["disk"] = {
            "status": disk_status,
            "usage_percent": round(disk_percent, 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "total_gb": round(disk.total / (1024**3), 2)
        }
    except Exception as e:
        health_status["checks"]["disk"] = {
            "status": "unknown",
            "message": f"Disk check failed: {str(e)}"
        }
    
    # 4. Environment variables check
    required_env_vars = ['DATABASE_URL', 'SECRET_KEY']
    missing_vars = []
    
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        health_status["checks"]["environment"] = {
            "status": "unhealthy",
            "message": f"Missing environment variables: {', '.join(missing_vars)}"
        }
        overall_healthy = False
    else:
        health_status["checks"]["environment"] = {
            "status": "healthy",
            "message": "All required environment variables present"
        }
    
    # 5. Python version and dependencies
    health_status["checks"]["runtime"] = {
        "status": "healthy",
        "python_version": sys.version,
        "platform": sys.platform
    }
    
    # Set overall status
    if not overall_healthy:
        health_status["status"] = "unhealthy"
    
    # Return appropriate HTTP status
    if health_status["status"] == "healthy":
        return health_status
    else:
        logger.warning(f"Health check failed: {health_status}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=health_status
        )

@router.get("/health/database")
async def database_health(db: Session = Depends(get_sync_db)) -> Dict[str, Any]:
    """
    Detailed database health check
    """
    try:
        # Test basic connectivity
        db.execute(text("SELECT 1"))
        
        # Check key tables exist
        tables_to_check = ['user', 'meeting', 'agenda_item', 'presentation_assignments']
        table_status = {}
        
        for table in tables_to_check:
            try:
                result = db.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                table_status[table] = {
                    "exists": True,
                    "row_count": result
                }
            except Exception as e:
                table_status[table] = {
                    "exists": False,
                    "error": str(e)
                }
        
        # Get database size
        try:
            db_size = db.execute(text(
                "SELECT pg_size_pretty(pg_database_size(current_database()))"
            )).scalar()
        except Exception:
            db_size = "unknown"
        
        return {
            "status": "healthy",
            "connection": "successful",
            "tables": table_status,
            "database_size": db_size,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

@router.get("/health/migrations")
async def migration_health(db: Session = Depends(get_sync_db)) -> Dict[str, Any]:
    """
    Check migration status
    """
    try:
        # Check if alembic_version table exists
        result = db.execute(text(
            "SELECT EXISTS(SELECT FROM information_schema.tables WHERE table_name = 'alembic_version')"
        )).scalar()
        
        if not result:
            return {
                "status": "warning",
                "message": "Alembic version table not found - migrations may not be initialized",
                "current_revision": None
            }
        
        # Get current revision
        current_revision = db.execute(text(
            "SELECT version_num FROM alembic_version ORDER BY version_num DESC LIMIT 1"
        )).scalar()
        
        return {
            "status": "healthy",
            "current_revision": current_revision,
            "migrations_initialized": True,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Migration health check failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/health/ready")
async def readiness_check(db: Session = Depends(get_sync_db)) -> Dict[str, Any]:
    """
    Kubernetes-style readiness probe
    """
    try:
        # Quick database check
        db.execute(text("SELECT 1"))
        
        # Check critical environment variables
        if not os.getenv('DATABASE_URL'):
            raise Exception("DATABASE_URL not configured")
        
        return {
            "status": "ready",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "not_ready",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

@router.get("/health/live")
async def liveness_check() -> Dict[str, Any]:
    """
    Kubernetes-style liveness probe
    """
    return {
        "status": "alive",
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": int((datetime.now() - datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds())
    }