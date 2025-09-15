from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
import os
from services.config import settings
from api.stories import router as stories_router
from api.newsletters import router as newsletters_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure data directories exist
os.makedirs(settings.data_dir, exist_ok=True)
os.makedirs(settings.logs_dir, exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 AI Marketing News System starting...")
    logger.info(f"Data directory: {settings.data_dir}")
    logger.info(f"Logs directory: {settings.logs_dir}")
    
    # Start scheduler
    from services.scheduler import scheduler
    scheduler.start()
    
    yield
    
    # Shutdown
    logger.info("👋 AI Marketing News System shutting down...")
    scheduler.stop()

app = FastAPI(
    title="AI Marketing News System",
    description="Automated AI news monitoring and newsletter generation for marketers",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(stories_router)
app.include_router(newsletters_router)

@app.get("/")
async def root():
    return {"message": "AI Marketing News System", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "data_dir": settings.data_dir,
        "logs_dir": settings.logs_dir,
        "openai_configured": bool(settings.openai_api_key and settings.openai_api_key != "your_openai_api_key_here")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)