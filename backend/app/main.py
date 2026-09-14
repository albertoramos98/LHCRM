import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status, Depends
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.database import init_db, AsyncSessionLocal
from app.core.bootstrap import bootstrap_initial_organization_and_admin
from app.core.dependencies import get_tenant_context, TenantContext
from app.routes.auth import router as auth_router
from app.routes.sync import router as sync_router
from app.routes.dashboard import router as dashboard_router
from app.integrations.kommo.routes import router as kommo_integration_router
from app.jobs.scheduler import start_scheduler, shutdown_scheduler
from app.services.sync_service import KommoSyncService

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Content Security Policy (Tailored for Vite, React, Google Fonts, Recharts)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com data:; "
            "img-src 'self' data: https:; "
            "connect-src 'self' http://localhost:* https://*.kommo.com; "
            "frame-ancestors 'none'; "
            "object-src 'none'; "
            "base-uri 'self';"
        )

        # HSTS (Strict-Transport-Security): ONLY enabled in production over HTTPS
        if settings.ENVIRONMENT.lower() == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schema
    logger.info("Initializing database tables...")
    await init_db()

    # Ensure static directory exists
    os.makedirs("static", exist_ok=True)

    # Bootstrap default organization and admin safely
    async with AsyncSessionLocal() as session:
        org, admin = await bootstrap_initial_organization_and_admin(
            session=session,
            org_name="Assessoria Revon",
            org_slug="revon",
            admin_name="Assessoria Revon",
            admin_email="assessoria.revon",
            admin_password=os.environ.get("INITIAL_ADMIN_PASSWORD", "Luizhenrique95#")
        )

        # Trigger initial data sync for default organization if fresh
        try:
            sync_service = KommoSyncService(session, organization_id=org.id)
            latest_log = await sync_service.get_latest_sync_status()
            if latest_log["status"] == "never_run":
                logger.info(f"Database is empty for Org '{org.name}'. Executing initial Kommo CRM data synchronization...")
                await sync_service.execute_sync(trigger_type="automatic")
            else:
                try:
                    from app.services.html_generator import generate_dashboard_html
                    await generate_dashboard_html(session, organization_id=org.id, output_path=f"static/dashboard_{org.slug}.html")
                    logger.info("Initial dashboard HTML generated successfully.")
                except Exception as e:
                    logger.error(f"Failed to generate initial dashboard HTML: {e}")
        except Exception as e:
            logger.error(f"Initial sync warning during startup: {e}", exc_info=True)

    # Start APScheduler for auto sync
    start_scheduler()
    yield
    # Shutdown APScheduler
    shutdown_scheduler()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Multi-Tenant Executive CRM Dashboard API with automated Kommo CRM data synchronization.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Security Headers
app.add_middleware(SecurityHeadersMiddleware)

# Configure CORS using strict origin list
allowed_origins = settings.ALLOWED_ORIGINS
if isinstance(allowed_origins, str):
    allowed_origins = [o.strip() for o in allowed_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins else ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Ensure static directory exists before mounting
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API Routers
app.include_router(auth_router)
app.include_router(sync_router)
app.include_router(dashboard_router)
app.include_router(kommo_integration_router)

@app.get("/public-dashboard", tags=["Public Dashboard"])
async def public_dashboard(tenant: TenantContext = Depends(get_tenant_context)):
    """
    Returns the authenticated tenant's shared HTML dashboard.
    """
    file_path = f"static/dashboard_{tenant.organization.slug}.html"
    if not os.path.exists(file_path):
        async with AsyncSessionLocal() as session:
            try:
                from app.services.html_generator import generate_dashboard_html
                await generate_dashboard_html(session, organization_id=tenant.organization_id, output_path=file_path)
            except Exception as e:
                logger.error(f"Failed to generate dashboard HTML for Org {tenant.organization_id}: {e}")
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
        "environment": settings.ENVIRONMENT,
        "multi_tenant": True,
        "docs": "/docs",
        "version": "2.0.0"
    }
