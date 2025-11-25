from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Configuración general
    APP_NAME: str = "Cuentas Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API Configuration
    API_V1_PREFIX: str = "/api"
    HOST: str = "0.0.0.0"
    PORT: int = 8002
    
    # Firebase
    FIREBASE_CREDENTIALS_PATH: str = "secrets/cuentas-service-credentials.json"
    FIREBASE_PROJECT_ID: Optional[str] = None
    
    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
    ]
    
    # Límites de operaciones
    LIMITE_DEPOSITO_DIARIO: float = 50000.0
    LIMITE_RETIRO_DIARIO: float = 20000.0
    SALDO_MINIMO_CUENTA: float = 0.0
    
    # Otros servicios (para integraciones futuras)
    CLIENTES_SERVICE_URL: Optional[str] = "http://localhost:8001"
    TRANSFERENCIAS_SERVICE_URL: Optional[str] = "http://localhost:8004"
    PAGOS_SERVICE_URL: Optional[str] = "http://localhost:8003"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()