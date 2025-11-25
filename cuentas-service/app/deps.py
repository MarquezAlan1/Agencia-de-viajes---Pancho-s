from app.firebase import get_firebase_db
from app.repos.cuentas_repo import CuentasRepository
from app.services.cuentas_service import CuentasService
from fastapi import Depends


def get_cuentas_repository(db=Depends(get_firebase_db)) -> CuentasRepository:
    """Dependency para obtener el repositorio de cuentas"""
    return CuentasRepository(db)


def get_cuentas_service(
    repo: CuentasRepository = Depends(get_cuentas_repository)
) -> CuentasService:
    """Dependency para obtener el servicio de cuentas"""
    return CuentasService(repo)