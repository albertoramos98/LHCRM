import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db, AsyncSessionLocal
from app.routes.auth import router as auth_router
from app.routes.sync import router as sync_router
from app.routes.dashboard import router as dashboard_router
from app.integrations.kommo.routes import router as kommo_integration_router
from app.jobs.scheduler import start_scheduler, shutdown_scheduler
from app.services.sync_service import KommoSyncService

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schema
    logger.info("Initializing database tables...")
    await init_db()

    # Ensure static directory exists
    os.makedirs("static", exist_ok=True)

    # Trigger initial data sync if database is fresh
    async with AsyncSessionLocal() as session:
        sync_service = KommoSyncService(session)
        latest_log = await sync_service.get_latest_sync_status()
        if latest_log["status"] == "never_run":
            logger.info("Database is empty. Executing initial Kommo CRM data synchronization...")
            await sync_service.execute_sync(trigger_type="automatic")
        else:
            # Generate initial dashboard HTML file from current DB
            try:
                from app.services.html_generator import generate_dashboard_html
                await generate_dashboard_html(session)
                logger.info("Initial public dashboard HTML generated successfully.")
            except Exception as e:
                logger.error(f"Failed to generate initial public dashboard HTML: {e}")

    # Start APScheduler for 5-min auto sync
    start_scheduler()
    yield
    # Shutdown APScheduler
    shutdown_scheduler()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Executive Administrative Dashboard API with automated Kommo CRM data sync.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS for decoupled React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files to serve the generated html dashboard
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API Routers
app.include_router(auth_router)
app.include_router(sync_router)
app.include_router(dashboard_router)
app.include_router(kommo_integration_router)

@app.get("/public-dashboard", tags=["Public Dashboard"])
async def public_dashboard():
    """
    Returns the public shared HTML dashboard. If it hasn't been generated yet,
    generates it on the fly.
    """
    file_path = "static/dashboard.html"
    if not os.path.exists(file_path):
        async with AsyncSessionLocal() as session:
            try:
                from app.services.html_generator import generate_dashboard_html
                await generate_dashboard_html(session)
            except Exception as e:
                logger.error(f"Failed to generate dashboard HTML on the fly: {e}")
                return JSONResponse(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    content={"detail": "O dashboard público ainda não foi gerado e não pôde ser criado agora."}
                )
    return FileResponse(file_path)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global unhandled exception on {request.method} {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Erro interno do servidor. Por favor, tente novamente ou contate o suporte."}
    )

@app.get("/", tags=["Health Check"])
async def root():
    return {
        "status": "online",
        "system": settings.PROJECT_NAME,
        "docs": "/docs",
        "api_endpoints": [
            "/api/auth/login",
            "/api/sync/now",
            "/api/sync/status",
            "/api/dashboard/overview",
            "/api/dashboard/funnel",
            "/api/dashboard/revenue",
            "/api/dashboard/followup",
            "/api/dashboard/ranking",
            "/api/dashboard/losses",
            "/api/dashboard/origins",
            "/api/dashboard/tickets",
            "/api/dashboard/performance",
            "/api/dashboard/metrics"
        ]
    }
