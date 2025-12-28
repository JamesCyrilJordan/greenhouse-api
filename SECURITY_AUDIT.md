# Security Audit Report

## Executive Summary

This document identifies security vulnerabilities and recommendations for the Greenhouse API. The API uses FastAPI with SQLAlchemy ORM and Bearer token authentication.

## Critical Security Issues

### 1. ⚠️ **CRITICAL: Overly Permissive CORS Configuration**

**Location**: `app/main.py:25`

**Issue**: 
```python
allow_origins=["*"]  # Allows ANY origin
```

**Risk**: 
- Allows any website to make requests to your API
- Enables Cross-Site Request Forgery (CSRF) attacks
- Allows malicious sites to access authenticated endpoints if user has valid token

**Impact**: High - Could allow unauthorized access to API endpoints

**Recommendation**:
```python
# Production configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://app.yourdomain.com",
        "https://admin.yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)
```

**Fix Priority**: 🔴 **IMMEDIATE** - Must fix before production deployment

---

### 2. ⚠️ **HIGH: No Rate Limiting**

**Location**: All endpoints

**Issue**: No rate limiting implemented on any endpoints

**Risk**:
- Denial of Service (DoS) attacks
- Brute force attacks on authentication
- Resource exhaustion
- API abuse

**Impact**: High - Could make API unavailable or allow brute force attacks

**Recommendation**:
```python
# Install: pip install slowapi
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/v1/readings")
@limiter.limit("10/minute")  # 10 requests per minute
def create_reading(...):
    ...
```

**Fix Priority**: 🟠 **HIGH** - Should be implemented before production

---

### 3. ⚠️ **MEDIUM: Information Disclosure in Error Messages**

**Location**: `app/main.py:56-57, 89-90`

**Issue**: Error messages logged but generic responses sent to clients

**Current State**: ✅ Good - Generic error messages are returned
```python
raise HTTPException(status_code=500, detail="Failed to create reading")
```

**Risk**: Low - Currently handled well, but ensure logs don't expose sensitive data

**Recommendation**: 
- ✅ Keep generic error messages (already done)
- ⚠️ Ensure logs don't contain sensitive information
- Consider adding request IDs for debugging without exposing details

---

### 4. ⚠️ **MEDIUM: Single Shared Token (No Per-Client Authentication)**

**Location**: `app/auth.py`, `app/config.py`

**Issue**: All clients share the same API token

**Risk**:
- Cannot revoke access for individual clients
- If token is compromised, all clients are affected
- No audit trail of which client made which request
- Token rotation requires updating all clients

**Impact**: Medium - Operational security concern

**Recommendation**:
- Consider implementing per-client API keys
- Use a token management system
- Implement token rotation mechanism
- Consider OAuth2 for better security

**Example Improvement**:
```python
# Store tokens in database with client_id, expiration, etc.
class APIToken(Base):
    id: int
    client_id: str
    token_hash: str  # Store hashed token
    expires_at: datetime
    is_active: bool
```

**Fix Priority**: 🟡 **MEDIUM** - Important for production scalability

---

### 5. ⚠️ **MEDIUM: No Request Size Limits**

**Location**: FastAPI application

**Issue**: No maximum request body size configured

**Risk**:
- Large request bodies could cause memory exhaustion
- DoS attacks via large payloads

**Impact**: Medium - Could cause service disruption

**Recommendation**:
```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    if request.method == "POST":
        body = await request.body()
        if len(body) > 1024 * 1024:  # 1MB limit
            return JSONResponse(
                status_code=413,
                content={"detail": "Request body too large"}
            )
    return await call_next(request)
```

Or configure at server level (uvicorn/gunicorn):
```bash
uvicorn app.main:app --limit-max-requests 1000 --limit-concurrency 100
```

**Fix Priority**: 🟡 **MEDIUM**

---

### 6. ⚠️ **MEDIUM: No Input Validation Beyond Pydantic**

**Location**: `app/schemas.py`, `app/main.py`

**Issue**: 
- No validation for device_id format (could allow injection patterns)
- No validation for sensor name (could allow unexpected values)
- No range validation for values (could allow extreme values)

**Risk**: Low-Medium - SQLAlchemy ORM protects against SQL injection, but:
- Could allow data pollution
- Could cause issues with downstream systems
- No business logic validation

**Current Protection**: ✅ SQLAlchemy ORM prevents SQL injection

**Recommendation**:
```python
from pydantic import validator
import re

class ReadingCreate(BaseModel):
    device_id: str = Field(min_length=1, max_length=64)
    
    @validator('device_id')
    def validate_device_id(cls, v):
        # Only allow alphanumeric, hyphens, underscores
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('device_id contains invalid characters')
        return v
    
    sensor: str = Field(min_length=1, max_length=64)
    
    @validator('sensor')
    def validate_sensor(cls, v):
        # Whitelist known sensors or validate format
        allowed_sensors = ['temperature', 'humidity', 'pressure', 'light']
        if v.lower() not in allowed_sensors:
            raise ValueError(f'sensor must be one of: {allowed_sensors}')
        return v.lower()
    
    value: float
    
    @validator('value')
    def validate_value(cls, v):
        # Reasonable range for sensor values
        if not -1000 <= v <= 1000:
            raise ValueError('value must be between -1000 and 1000')
        return v
```

**Fix Priority**: 🟡 **MEDIUM** - Depends on business requirements

---

### 7. ⚠️ **LOW: Health Endpoint Exposes Server Time**

**Location**: `app/main.py:33`

**Issue**: Health endpoint returns server timestamp

**Risk**: Low - Could be used for timing attacks or reconnaissance

**Current State**:
```python
return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}
```

**Recommendation**: 
- Consider removing timestamp or making it less precise
- Or require authentication for detailed health info

**Fix Priority**: 🟢 **LOW** - Minor information disclosure

---

### 8. ⚠️ **LOW: No Database Connection Pooling Limits**

**Location**: `app/db.py:9`

**Issue**: No connection pool size limits configured

**Risk**: Low-Medium - Could exhaust database connections under load

**Recommendation**:
```python
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_size=10,          # Number of connections to maintain
    max_overflow=20,       # Additional connections allowed
    pool_pre_ping=True,    # Verify connections before using
    pool_recycle=3600,     # Recycle connections after 1 hour
)
```

**Fix Priority**: 🟡 **MEDIUM** - Important for production stability

---

### 9. ⚠️ **LOW: Logging May Contain Sensitive Data**

**Location**: `app/main.py:52`

**Issue**: Logs contain device_id and sensor names

**Current State**:
```python
logger.info(f"Created reading: device_id={payload.device_id}, sensor={payload.sensor}")
```

**Risk**: Low - Device IDs and sensor names are likely not sensitive, but:
- Could expose business information
- Could be used for reconnaissance

**Recommendation**:
- Review what information is logged
- Ensure no tokens or sensitive data in logs
- Consider log sanitization
- Use structured logging with log levels

**Fix Priority**: 🟢 **LOW** - Review and adjust as needed

---

### 10. ✅ **GOOD: SQL Injection Protection**

**Status**: ✅ **SECURE**

**Location**: All database queries

**Protection**: Using SQLAlchemy ORM with parameterized queries
```python
q = q.filter(Reading.device_id == device_id)  # Safe - uses parameterized queries
```

**No raw SQL queries found** - All queries use ORM

---

### 11. ✅ **GOOD: Timing Attack Protection**

**Status**: ✅ **SECURE**

**Location**: `app/auth.py:13`

**Protection**: Using `hmac.compare_digest()` for constant-time comparison
```python
if not hmac.compare_digest(token.encode('utf-8'), API_TOKEN.encode('utf-8')):
```

---

### 12. ✅ **GOOD: Input Validation**

**Status**: ✅ **SECURE**

**Location**: `app/schemas.py`

**Protection**: 
- Pydantic models validate all inputs
- Field length constraints
- Type validation
- Required field validation

---

## Additional Security Recommendations

### 1. **HTTPS Enforcement**
- Ensure HTTPS is used in production
- Consider HSTS headers
- Use secure cookies if implementing session management

### 2. **Security Headers**
```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
)
```

### 3. **API Versioning**
- ✅ Already implemented (`/api/v1/`)
- Consider deprecation strategy

### 4. **Monitoring and Alerting**
- Monitor for suspicious activity
- Alert on authentication failures
- Track rate limit violations

### 5. **Dependency Security**
- Regularly update dependencies
- Use `pip-audit` or `safety` to check for vulnerabilities
- Keep requirements.txt pinned to specific versions

### 6. **Environment Variable Security**
- ✅ `.env` file is in `.gitignore` (good)
- Ensure `.env` file permissions are restricted (600)
- Use secrets management in production (AWS Secrets Manager, HashiCorp Vault, etc.)

### 7. **Database Security**
- Use connection encryption (SSL/TLS) for production databases
- Restrict database access to application servers only
- Use least-privilege database users
- Regular backups with encryption

### 8. **Error Handling**
- ✅ Generic error messages (good)
- Consider adding request IDs for debugging
- Log errors server-side without exposing to clients

---

## Security Checklist

### Before Production Deployment:

- [ ] **CRITICAL**: Fix CORS configuration - restrict to specific origins
- [ ] **HIGH**: Implement rate limiting
- [ ] **MEDIUM**: Add request size limits
- [ ] **MEDIUM**: Configure database connection pooling
- [ ] **MEDIUM**: Review and enhance input validation
- [ ] **LOW**: Review logging for sensitive data
- [ ] **LOW**: Remove or secure health endpoint timestamp
- [ ] Enable HTTPS/TLS
- [ ] Add security headers (HSTS, CSP, etc.)
- [ ] Set up monitoring and alerting
- [ ] Review and update all dependencies
- [ ] Perform penetration testing
- [ ] Set up log aggregation and analysis
- [ ] Document incident response procedures

---

## Summary

### Security Strengths ✅
1. SQL injection protection (SQLAlchemy ORM)
2. Timing attack protection (hmac.compare_digest)
3. Input validation (Pydantic)
4. Generic error messages
5. Bearer token authentication
6. Environment variables properly excluded from git

### Critical Issues 🔴
1. **CORS allows all origins** - Must fix before production
2. **No rate limiting** - Should implement before production

### Medium Priority Issues 🟡
1. Single shared token (no per-client auth)
2. No request size limits
3. Limited input validation
4. No database connection pool limits

### Low Priority Issues 🟢
1. Health endpoint timestamp exposure
2. Logging review needed

---

## Risk Assessment

**Overall Risk Level**: 🟡 **MEDIUM-HIGH**

The API has good foundational security (SQL injection protection, timing attack protection, input validation), but has critical configuration issues (CORS, rate limiting) that must be addressed before production deployment.

**Recommended Action**: Address critical and high-priority issues before production deployment.

