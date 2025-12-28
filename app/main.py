from typing import Optional
from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone
import logging

from .db import Base, engine, get_db
from .models import Reading
from .schemas import ReadingCreate, ReadingOut, PaginatedReadings
from .auth import require_token

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Greenhouse API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/health")
def health():
    return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}

@app.post("/api/v1/readings", response_model=ReadingOut)
def create_reading(
    payload: ReadingCreate,
    db: Session = Depends(get_db),
    _auth=Depends(require_token),
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
def list_readings(
    device_id: Optional[str] = None,
    sensor: Optional[str] = None,
    limit: int = Query(100, ge=1, le=2000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    _auth=Depends(require_token),
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
