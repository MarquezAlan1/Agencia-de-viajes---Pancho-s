from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.routers import cuentas
import uvicorn


# Crear aplicación FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Microservicio de gestión de cuentas bancarias",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Verifica el estado del servicio"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@app.get("/", tags=["Root"])
async def root():
    """Endpoint raíz con información del servicio"""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "Microservicio de gestión de cuentas bancarias",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "api": settings.API_V1_PREFIX
        }
    }


# Incluir routers
app.include_router(
    cuentas.router,
    prefix=settings.API_V1_PREFIX,
    tags=["Cuentas"]
)


# Manejador global de excepciones
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Error interno del servidor",
            "error": str(exc) if settings.DEBUG else "Error procesando la solicitud"
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )