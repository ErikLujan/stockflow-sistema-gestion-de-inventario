"""
Módulo principal de la aplicación para el Sistema de Gestión de Inventario.
Inicializa la aplicación FastAPI, configura middlewares, seguridad y enrutadores.
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.rate_limit import limiter
from app.core.scheduler import start_scheduler
from app.api.v1.api import api_router

def create_app() -> FastAPI:
    """
    Función de fábrica de la aplicación.
    
    Returns:
        FastAPI: La instancia configurada de la aplicación FastAPI.
    """

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        start_scheduler()
        yield

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        lifespan=lifespan
    )

    app.mount("/static", StaticFiles(directory="static"), name="static")

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    allowed_origins = [
        "http://localhost:4200", 
        "http://localhost:8000"
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.API_V1_STR)

    @app.get("/health", methods=["GET", "HEAD"], tags=["Health Check"])
    def health_check() -> dict:
        """
        Endpoint de verificación de estado.
        """
        return {
            "status": "ok", 
            "message": "El servicio está operativo",
            "version": settings.VERSION
        }

    return app

app = create_app()