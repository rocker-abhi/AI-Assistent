import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logger import logger
from app.websockets.route import router as websocket_router

def create_app() -> FastAPI:
    """Factory to create and configure the FastAPI application."""
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
    )

    # Set up CORS middleware to ensure the React/Vite frontend can communicate
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Attach the WebSocket routes we created
    application.include_router(websocket_router)

    # Lifecycle hooks for our logger
    @application.on_event("startup")
    async def startup_event():
        logger.info(f"🚀 {settings.PROJECT_NAME} backend starting up...")
        logger.info(f"CORS enabled for origins: {settings.CORS_ORIGINS}")

    @application.on_event("shutdown")
    async def shutdown_event():
        logger.info(f"🛑 {settings.PROJECT_NAME} backend shutting down...")

    # Standard health check endpoint
    @application.get("/")
    async def health_check():
        logger.debug("Health check endpoint pinged.")
        return {"status": "online", "project": settings.PROJECT_NAME, "version": settings.VERSION}

    return application

app = create_app()

if __name__ == "__main__":
    logger.info(f"Starting uvicorn development server on {settings.HOST}:{settings.PORT}")
    # Run uvicorn server mapping strictly to the HOST and PORT from our config.py
    uvicorn.run(
        "main:app", 
        host=settings.HOST, 
        port=settings.PORT, 
        reload=True  # Auto-reloads the server when you save Python files
    )
