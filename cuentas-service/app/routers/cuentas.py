from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from app.services.cuentas_service import CuentasService
from app.schemas import (
    CuentaCreate, CuentaUpdate, CuentaResponse,
    DepositoRequest, RetiroRequest, OperacionResponse,
    MovimientoResponse, CuentaFilter, MovimientoFilter
)
from app.models import EstadoCuenta, Moneda, Cuenta, Movimiento
from app.deps import get_cuentas_service


router = APIRouter(prefix="/cuentas", tags=["Cuentas"])


def cuenta_to_response(cuenta: Cuenta) -> CuentaResponse:
    """Convierte un modelo Cuenta a CuentaResponse"""
    return CuentaResponse(
        id=cuenta.id,
        cliente_id=cuenta.cliente_id,
        numero_cuenta=cuenta.numero_cuenta,
        tipo=cuenta.tipo if isinstance(cuenta.tipo, str) else cuenta.tipo.value,
        moneda=cuenta.moneda if isinstance(cuenta.moneda, str) else cuenta.moneda.value,
        saldo=cuenta.saldo,
        estado=cuenta.estado if isinstance(cuenta.estado, str) else cuenta.estado.value,
        fecha_apertura=cuenta.fecha_apertura,
        created_at=cuenta.created_at,
        updated_at=cuenta.updated_at
    )


def movimiento_to_response(mov: Movimiento) -> MovimientoResponse:
    """Convierte un modelo Movimiento a MovimientoResponse"""
    return MovimientoResponse(
        id=mov.id,
        cuenta_id=mov.cuenta_id,
        tipo=mov.tipo if isinstance(mov.tipo, str) else mov.tipo.value,
        monto=mov.monto,
        saldo_anterior=mov.saldo_anterior,
        saldo_nuevo=mov.saldo_nuevo,
        descripcion=mov.descripcion,
        referencia=mov.referencia,
        fecha=mov.fecha
    )


@router.post("/", response_model=CuentaResponse, status_code=status.HTTP_201_CREATED)
async def crear_cuenta(
    cuenta_data: CuentaCreate,
    service: CuentasService = Depends(get_cuentas_service)
):
    """
    Crea una nueva cuenta bancaria
    
    - **cliente_id**: ID del cliente propietario
    - **tipo**: Tipo de cuenta (AHORRO, CORRIENTE)
    - **moneda**: Moneda de la cuenta (BOB, USD)
    - **saldo_inicial**: Saldo inicial (opcional, por defecto 0)
    """
    try:
        cuenta = service.crear_cuenta(cuenta_data)
        return cuenta_to_response(cuenta)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear cuenta: {str(e)}"
        )


@router.get("/", response_model=List[CuentaResponse])
async def listar_cuentas(
    cliente_id: Optional[str] = Query(None, description="Filtrar por cliente"),
    numero_cuenta: Optional[str] = Query(None, description="Filtrar por número de cuenta"),
    estado: Optional[EstadoCuenta] = Query(None, description="Filtrar por estado"),
    moneda: Optional[Moneda] = Query(None, description="Filtrar por moneda"),
    service: CuentasService = Depends(get_cuentas_service)
):
    """
    Lista todas las cuentas con filtros opcionales
    
    - **cliente_id**: Filtrar cuentas de un cliente específico
    - **numero_cuenta**: Buscar por número de cuenta exacto
    - **estado**: Filtrar por estado (ACTIVA, BLOQUEADA, CERRADA)
    - **moneda**: Filtrar por moneda (BOB, USD)
    """
    filters = CuentaFilter(
        cliente_id=cliente_id,
        numero_cuenta=numero_cuenta,
        estado=estado,
        moneda=moneda
    )
    
    cuentas = service.listar_cuentas(filters)
    
    return [cuenta_to_response(cuenta) for cuenta in cuentas]


@router.get("/{cuenta_id}", response_model=CuentaResponse)
async def obtener_cuenta(
    cuenta_id: str,
    service: CuentasService = Depends(get_cuentas_service)
):
    """
    Obtiene los detalles de una cuenta específica
    
    - **cuenta_id**: ID de la cuenta
    """
    cuenta = service.obtener_cuenta(cuenta_id)
    return cuenta_to_response(cuenta)


@router.put("/{cuenta_id}", response_model=CuentaResponse)
async def actualizar_cuenta(
    cuenta_id: str,
    update_data: CuentaUpdate,
    service: CuentasService = Depends(get_cuentas_service)
):
    """
    Actualiza los datos de una cuenta (excepto el saldo)
    
    - **tipo**: Cambiar tipo de cuenta
    - **estado**: Cambiar estado de cuenta
    """
    cuenta = service.actualizar_cuenta(cuenta_id, update_data)
    return cuenta_to_response(cuenta)


@router.post("/{cuenta_id}/depositar", response_model=OperacionResponse)
async def depositar(
    cuenta_id: str,
    deposito: DepositoRequest,
    service: CuentasService = Depends(get_cuentas_service)
):
    """
    Realiza un depósito en la cuenta
    
    - **monto**: Cantidad a depositar (debe ser mayor a 0)
    - **descripcion**: Descripción del depósito
    """
    return service.depositar(cuenta_id, deposito)


@router.post("/{cuenta_id}/retirar", response_model=OperacionResponse)
async def retirar(
    cuenta_id: str,
    retiro: RetiroRequest,
    service: CuentasService = Depends(get_cuentas_service)
):
    """
    Realiza un retiro de la cuenta
    
    - **monto**: Cantidad a retirar (debe ser mayor a 0)
    - **descripcion**: Descripción del retiro
    
    Valida que haya saldo suficiente
    """
    return service.retirar(cuenta_id, retiro)


@router.post("/{cuenta_id}/bloquear", response_model=CuentaResponse)
async def bloquear_cuenta(
    cuenta_id: str,
    service: CuentasService = Depends(get_cuentas_service)
):
    """
    Bloquea una cuenta, impidiendo operaciones
    """
    cuenta = service.bloquear_cuenta(cuenta_id)
    return cuenta_to_response(cuenta)


@router.post("/{cuenta_id}/desbloquear", response_model=CuentaResponse)
async def desbloquear_cuenta(
    cuenta_id: str,
    service: CuentasService = Depends(get_cuentas_service)
):
    """
    Desbloquea una cuenta previamente bloqueada
    """
    cuenta = service.desbloquear_cuenta(cuenta_id)
    return cuenta_to_response(cuenta)


@router.get("/{cuenta_id}/movimientos", response_model=List[MovimientoResponse])
async def obtener_movimientos(
    cuenta_id: str,
    limit: int = Query(50, ge=1, le=200, description="Límite de resultados"),
    service: CuentasService = Depends(get_cuentas_service)
):
    """
    Obtiene el historial de movimientos de una cuenta
    
    - **limit**: Número máximo de movimientos a retornar (por defecto 50, máximo 200)
    """
    movimientos = service.obtener_movimientos(cuenta_id, limit=limit)
    return [movimiento_to_response(mov) for mov in movimientos]


# Endpoints adicionales para uso interno de otros microservicios
@router.post("/{cuenta_id}/validar-saldo", response_model=dict)
async def validar_saldo(
    cuenta_id: str,
    monto: float = Query(..., gt=0),
    service: CuentasService = Depends(get_cuentas_service)
):
    """
    Valida si una cuenta tiene saldo suficiente
    
    Endpoint útil para otros microservicios (transferencias, pagos)
    """
    tiene_saldo = service.validar_saldo_disponible(cuenta_id, monto)
    
    return {
        "cuenta_id": cuenta_id,
        "monto_solicitado": monto,
        "tiene_saldo": tiene_saldo
    }