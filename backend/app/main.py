import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
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

    # Trigger initial data sync if database is fresh
    async with AsyncSessionLocal() as session:
        sync_service = KommoSyncService(session)
        latest_log = await sync_service.get_latest_sync_status()
        if latest_log["status"] == "never_run":
            logger.info("Database is empty. Executing initial Kommo CRM data synchronization...")
            await sync_service.execute_sync(trigger_type="automatic")

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

# Include API Routers
app.include_router(auth_router)
app.include_router(sync_router)
app.include_router(dashboard_router)
app.include_router(kommo_integration_router)

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
