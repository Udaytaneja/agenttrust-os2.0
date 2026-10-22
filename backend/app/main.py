import logging
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.agents import router as agents_router
from backend.app.api.ai import router as ai_router
from backend.app.api.applications import router as applications_router
from backend.app.api.audit import router as audit_router
from backend.app.api.auth import router as auth_router
from backend.app.api.bankers import router as bankers_router
from backend.app.api.documents import router as documents_router
from backend.app.api.financial import router as financial_router
from backend.app.api.governance import router as governance_router
from backend.app.api.loans import router as loans_router
from backend.app.api.notifications import router as notifications_router
from backend.app.api.payments import router as payments_router
from backend.app.api.repayments import router as repayments_router
from backend.app.api.trust import router as trust_router
from backend.app.api.underwriting import router as underwriting_router
from backend.app.api.users import router as users_router
from backend.app.core.config import settings
from backend.app.core.database import engine
from backend.app.models import Base

logger = logging.getLogger("agenttrust.startup")
logging.basicConfig(level=logging.INFO)


def get_allowed_origins() -> list[str]:
    raw_origins = set()
    if settings.cors_origins:
        for item in settings.cors_origins.split(","):
            cleaned = item.strip().rstrip("/")
            if cleaned:
                raw_origins.add(cleaned)
    if settings.frontend_url:
        cleaned_frontend = settings.frontend_url.strip().rstrip("/")
        if cleaned_frontend:
            raw_origins.add(cleaned_frontend)
    raw_origins.add("https://agenttrust-20.vercel.app")
    return sorted(list(raw_origins))


@asynccontextmanager
async def lifespan(application: FastAPI):
    # Production Startup Validation (No secrets logged)
    db_type = "SQLite" if settings.database_url.startswith("sqlite") else "PostgreSQL"
    logger.info(f"AgentTrust OS Starting • Environment: {settings.app_env} • Database: {db_type}")
    logger.info(f"Storage Provider: {settings.storage_provider} • YOLO Checkpoint: {settings.yolo_model_path}")
    allowed_origins = get_allowed_origins()
    logger.info(f"Configured Frontend URL: {settings.frontend_url.strip().rstrip('/')}")
    logger.info(f"CORS Allowed Origins Count: {len(allowed_origins)}")
    logger.info(f"CORS contains Vercel origin (https://agenttrust-20.vercel.app): {'https://agenttrust-20.vercel.app' in allowed_origins}")

    if settings.app_env == "production":
        if settings.jwt_secret == "secret-key-1234567890" or len(settings.jwt_secret) < 32:
            logger.warning("SECURITY WARNING: JWT_SECRET should be a strong 32+ character random string in production.")
        if db_type == "SQLite":
            logger.warning("DATABASE NOTICE: Running with SQLite in production; PostgreSQL recommended.")

    if settings.app_env == "development" and settings.database_url.startswith("sqlite"):
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    # Controlled account bootstrap (only runs if BOOTSTRAP_* env vars are provided)
    try:
        from backend.app.core.database import AsyncSessionLocal
        from backend.app.services.bootstrap_service import bootstrap_initial_accounts
        async with AsyncSessionLocal() as session:
            await bootstrap_initial_accounts(session)
    except Exception as exc:
        logger.warning(f"Account bootstrap notice: {exc}")

    yield


app = FastAPI(
    title="AgentTrust OS",
    description="Secure financial trust and intelligence platform",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS dynamically from CORS_ORIGINS & FRONTEND_URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Standard Error Format Handler matching contracts/schemas.md
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        422: "UNPROCESSABLE_ENTITY",
        500: "INTERNAL_SERVER_ERROR",
    }
    error_code = code_map.get(exc.status_code, "ERROR")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": error_code,
                "message": exc.detail,
                "details": None,
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": exc.errors(),
            }
        },
    )


api_v1_router = APIRouter(prefix="/api/v1")


@api_v1_router.get("/health")
async def api_v1_health():
    return {
        "status": "healthy",
        "service": "AgentTrust OS API",
        "version": "1.0.0",
        "environment": settings.app_env,
        "storage": settings.storage_provider,
    }


api_v1_router.include_router(auth_router)
api_v1_router.include_router(users_router)
api_v1_router.include_router(financial_router)
api_v1_router.include_router(trust_router)
api_v1_router.include_router(bankers_router)
api_v1_router.include_router(documents_router)
api_v1_router.include_router(applications_router)
api_v1_router.include_router(loans_router)
api_v1_router.include_router(repayments_router)
api_v1_router.include_router(payments_router)
api_v1_router.include_router(notifications_router)
api_v1_router.include_router(audit_router)
api_v1_router.include_router(ai_router)
api_v1_router.include_router(agents_router)
api_v1_router.include_router(governance_router)
api_v1_router.include_router(underwriting_router)

app.include_router(api_v1_router)

# Root-level fallback for backward compatibility
app.include_router(auth_router)


@app.get("/")
async def root():
    return {
        "message": "AgentTrust OS API is running",
        "environment": settings.app_env,
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.app_env,
    }