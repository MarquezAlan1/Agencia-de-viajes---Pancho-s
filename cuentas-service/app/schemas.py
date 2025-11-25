from pydantic import BaseModel, Field, validator
from typing import Optional, Literal
from datetime import datetime
from app.models import TipoCuenta, Moneda, EstadoCuenta, TipoMovimiento


# Schemas para Cuenta
class CuentaCreate(BaseModel):
    cliente_id: str
    tipo: TipoCuenta = TipoCuenta.AHORRO
    moneda: Moneda = Moneda.BOB
    saldo_inicial: float = Field(default=0.0, ge=0)

    @validator('saldo_inicial')
    def validar_saldo_inicial(cls, v):
        if v < 0:
            raise ValueError('El saldo inicial no puede ser negativo')
        return v


class CuentaUpdate(BaseModel):
    tipo: Optional[TipoCuenta] = None
    estado: Optional[EstadoCuenta] = None

    class Config:
        use_enum_values = True


class CuentaResponse(BaseModel):
    id: str
    cliente_id: str
    numero_cuenta: str
    tipo: str
    moneda: str
    saldo: float
    estado: str
    fecha_apertura: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Schemas para Operaciones
class DepositoRequest(BaseModel):
    monto: float = Field(gt=0)
    descripcion: str = Field(min_length=1, max_length=255)

    @validator('monto')
    def validar_monto_deposito(cls, v):
        if v <= 0:
            raise ValueError('El monto debe ser mayor a 0')
        if v > 1000000:
            raise ValueError('El monto excede el límite permitido')
        return round(v, 2)


class RetiroRequest(BaseModel):
    monto: float = Field(gt=0)
    descripcion: str = Field(min_length=1, max_length=255)

    @validator('monto')
    def validar_monto_retiro(cls, v):
        if v <= 0:
            raise ValueError('El monto debe ser mayor a 0')
        return round(v, 2)


class OperacionResponse(BaseModel):
    success: bool
    mensaje: str
    cuenta_id: str
    saldo_anterior: float
    saldo_nuevo: float
    monto: float
    movimiento_id: Optional[str] = None


# Schemas para Movimiento
class MovimientoResponse(BaseModel):
    id: str
    cuenta_id: str
    tipo: str
    monto: float
    saldo_anterior: float
    saldo_nuevo: float
    descripcion: str
    referencia: Optional[str] = None
    fecha: datetime

    class Config:
        from_attributes = True


# Schemas para consultas
class CuentaFilter(BaseModel):
    cliente_id: Optional[str] = None
    numero_cuenta: Optional[str] = None
    estado: Optional[EstadoCuenta] = None
    moneda: Optional[Moneda] = None


class MovimientoFilter(BaseModel):
    tipo: Optional[TipoMovimiento] = None
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None