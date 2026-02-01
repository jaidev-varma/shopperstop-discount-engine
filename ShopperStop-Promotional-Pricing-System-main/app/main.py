import logging
import uuid
import time
from fastapi import FastAPI, Request
from app.api.endpoints import router as bill_router
from app.api.promotions import router as promo_router
from app.api.tiers import router as tier_router

# 1. Structured Logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - [Correlation-ID: %(correlation_id)s] - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("api")

app = FastAPI(
    title="ShopperStop Promotional Pricing Engine",
    description="API-driven discount engine for retail operations",
    version="1.1.0"
)

# 2. Middleware for Audit & Correlation ID
@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    # Generate or extract Correlation ID
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    
    start_time = time.time()
    
    # Audit Log: Request Start
    logger.info(
        f"AUDIT: Request Started: {request.method} {request.url}", 
        extra={'correlation_id': correlation_id}
    )
    
    # --- FIX IS HERE ---
    # We must AWAIT the call_next function to get the actual Response object
    response = await call_next(request)
    # -------------------
    
    process_time = time.time() - start_time
    
    # Inject Correlation ID into Response Headers
    response.headers["X-Correlation-ID"] = correlation_id
    
    # Audit Log: Request End
    logger.info(
        f"AUDIT: Request Completed: Status {response.status_code} - Took {process_time:.4f}s", 
        extra={'correlation_id': correlation_id}
    )
    return response

# 3. Health Check
@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.1.0", "service": "PPE"}

# Register Routes
app.include_router(bill_router, prefix="/api/v1/bills", tags=["Bills"])
app.include_router(promo_router, prefix="/api/v1/promotions", tags=["Promotions"])
app.include_router(tier_router, prefix="/api/v1/customer-tiers", tags=["Customer Tiers"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)