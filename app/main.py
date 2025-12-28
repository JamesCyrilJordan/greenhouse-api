from typing import Optional
from fastapi import FastAPI, Depends, Query, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone
import logging

from .db import Base, engine, get_db
from .models import Reading
from .schemas import ReadingCreate, ReadingOut, PaginatedReadings
from .auth import require_token
from .config import CORS_ORIGINS, RATE_LIMIT_ENABLED, RATE_LIMIT_PER_MINUTE, MAX_REQUEST_SIZE

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Greenhouse API", version="1.0.0")

# Add CORS middleware with configurable origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Add rate limiting if enabled
limiter = None

if RATE_LIMIT_ENABLED:
    try:
        from slowapi import Limiter, _rate_limit_exceeded_handler
        from slowapi.util import get_remote_address
        from slowapi.errors import RateLimitExceeded
        
        limiter = Limiter(key_func=get_remote_address)
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
        logger.info(f"Rate limiting enabled: {RATE_LIMIT_PER_MINUTE} requests per minute")
    except ImportError:
        logger.warning("slowapi not installed. Rate limiting disabled. Install with: pip install slowapi")
        limiter = None
else:
    logger.info("Rate limiting disabled via configuration")

# Create rate limit decorator
if limiter:
    def rate_limit(func):
        """Apply rate limiting to a function."""
        return limiter.limit(f"{RATE_LIMIT_PER_MINUTE}/minute")(func)
else:
    def rate_limit(func):
        """No-op decorator when rate limiting is disabled."""
        return func

# Add request size limiting middleware
@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    """Limit request body size to prevent DoS attacks."""
    if request.method in ["POST", "PUT", "PATCH"]:
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                if size > MAX_REQUEST_SIZE:
                    return JSONResponse(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        content={"detail": f"Request body too large. Maximum size: {MAX_REQUEST_SIZE} bytes"}
                    )
            except ValueError:
                # Invalid content-length header, let it through but log it
                logger.warning(f"Invalid content-length header: {content_length}")
    
    response = await call_next(request)
    return response

@app.get("/api/v1/health")
def health():
    return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}

@app.post("/api/v1/readings", response_model=ReadingOut)
@rate_limit
def create_reading(
    payload: ReadingCreate,
    db: Session = Depends(get_db),
    _auth=Depends(require_token),
    request: Request = None,
):
    try:
        r = Reading(
            device_id=payload.device_id,
            sensor=payload.sensor,
            value=payload.value,
            unit=payload.unit or "",
            recorded_at=payload.recorded_at or datetime.now(timezone.utc),
        )
        db.add(r)
        db.commit()
        db.refresh(r)
        logger.info(f"Created reading: device_id={payload.device_id}, sensor={payload.sensor}")
        return r
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating reading: {e}")
        raise HTTPException(status_code=500, detail="Failed to create reading")
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error creating reading: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/v1/readings", response_model=PaginatedReadings)
@rate_limit
def list_readings(
    device_id: Optional[str] = None,
    sensor: Optional[str] = None,
    limit: int = Query(100, ge=1, le=2000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    _auth=Depends(require_token),
    request: Request = None,
):
    try:
        q = db.query(Reading).order_by(Reading.recorded_at.desc())
        if device_id:
            q = q.filter(Reading.device_id == device_id)
        if sensor:
            q = q.filter(Reading.sensor == sensor)
        
        total = q.count()
        results = q.offset(offset).limit(limit).all()
        
        return PaginatedReadings(
            items=results,
            total=total,
            limit=limit,
            offset=offset
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error listing readings: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve readings")
    except Exception as e:
        logger.error(f"Unexpected error listing readings: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
