from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal, Union
from datetime import datetime
from enum import Enum


class TipoCuenta(str, Enum):
    AHORRO = "AHORRO"
    CORRIENTE = "CORRIENTE"


class Moneda(str, Enum):
    BOB = "BOB"
    USD = "USD"


class EstadoCuenta(str, Enum):
    ACTIVA = "ACTIVA"
    BLOQUEADA = "BLOQUEADA"
    CERRADA = "CERRADA"


class TipoMovimiento(str, Enum):
    DEPOSITO = "DEPOSITO"
    RETIRO = "RETIRO"
    TRANSFERENCIA_ENTRADA = "TRANSFERENCIA_ENTRADA"
    TRANSFERENCIA_SALIDA = "TRANSFERENCIA_SALIDA"
    PAGO_SERVICIO = "PAGO_SERVICIO"


class Cuenta(BaseModel):
    id: Optional[str] = None
    cliente_id: str
    numero_cuenta: str
    tipo: Union[TipoCuenta, str] = TipoCuenta.AHORRO
    moneda: Union[Moneda, str] = Moneda.BOB
    saldo: float = 0.0
    estado: Union[EstadoCuenta, str] = EstadoCuenta.ACTIVA
    fecha_apertura: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @field_validator('tipo', mode='before')
    @classmethod
    def validate_tipo(cls, v):
        if isinstance(v, str):
            return v
        return v.value if hasattr(v, 'value') else v

    @field_validator('moneda', mode='before')
    @classmethod
    def validate_moneda(cls, v):
        if isinstance(v, str):
            return v
        return v.value if hasattr(v, 'value') else v

    @field_validator('estado', mode='before')
    @classmethod
    def validate_estado(cls, v):
        if isinstance(v, str):
            return v
        return v.value if hasattr(v, 'value') else v

    class Config:
        use_enum_values = True


class Movimiento(BaseModel):
    id: Optional[str] = None
    cuenta_id: str
    tipo: Union[TipoMovimiento, str]
    monto: float
    saldo_anterior: float
    saldo_nuevo: float
    descripcion: str
    referencia: Optional[str] = None
    fecha: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)

    @field_validator('tipo', mode='before')
    @classmethod
    def validate_tipo(cls, v):
        if isinstance(v, str):
            return v
        return v.value if hasattr(v, 'value') else v

    class Config:
        use_enum_values = True