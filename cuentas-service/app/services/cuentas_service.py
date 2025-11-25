from typing import List, Optional
from datetime import datetime
from app.models import Cuenta, Movimiento, EstadoCuenta, TipoMovimiento
from app.schemas import (
    CuentaCreate, CuentaUpdate, CuentaFilter,
    DepositoRequest, RetiroRequest, OperacionResponse,
    MovimientoFilter
)
from app.repos.cuentas_repo import CuentasRepository
from fastapi import HTTPException, status


class CuentasService:
    def __init__(self, repo: CuentasRepository):
        self.repo = repo

    def crear_cuenta(self, cuenta_data: CuentaCreate) -> Cuenta:
        """Crea una nueva cuenta bancaria"""
        nueva_cuenta = Cuenta(
            cliente_id=cuenta_data.cliente_id,
            tipo=cuenta_data.tipo,
            moneda=cuenta_data.moneda,
            saldo=cuenta_data.saldo_inicial,
            estado=EstadoCuenta.ACTIVA,
            numero_cuenta="",  # Se genera en el repo
            fecha_apertura=datetime.now()
        )
        
        cuenta_id = self.repo.create(nueva_cuenta)
        cuenta_creada = self.repo.get_by_id(cuenta_id)
        
        # Registrar movimiento inicial si hay saldo
        if cuenta_data.saldo_inicial > 0:
            movimiento = Movimiento(
                cuenta_id=cuenta_id,
                tipo=TipoMovimiento.DEPOSITO,
                monto=cuenta_data.saldo_inicial,
                saldo_anterior=0.0,
                saldo_nuevo=cuenta_data.saldo_inicial,
                descripcion="Depósito inicial - Apertura de cuenta"
            )
            self.repo.crear_movimiento(movimiento)
        
        return cuenta_creada

    def obtener_cuenta(self, cuenta_id: str) -> Cuenta:
        """Obtiene una cuenta por ID"""
        cuenta = self.repo.get_by_id(cuenta_id)
        
        if not cuenta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cuenta con ID {cuenta_id} no encontrada"
            )
        
        return cuenta

    def listar_cuentas(self, filters: Optional[CuentaFilter] = None) -> List[Cuenta]:
        """Lista todas las cuentas con filtros opcionales"""
        return self.repo.list(filters)

    def actualizar_cuenta(self, cuenta_id: str, update_data: CuentaUpdate) -> Cuenta:
        """Actualiza los datos de una cuenta"""
        cuenta = self.obtener_cuenta(cuenta_id)
        
        update_dict = update_data.model_dump(exclude_unset=True)
        
        if update_dict:
            self.repo.update(cuenta_id, update_dict)
        
        return self.repo.get_by_id(cuenta_id)

    def depositar(self, cuenta_id: str, deposito: DepositoRequest) -> OperacionResponse:
        """Realiza un depósito en la cuenta"""
        cuenta = self.obtener_cuenta(cuenta_id)
        
        # Validar estado de la cuenta
        if cuenta.estado != EstadoCuenta.ACTIVA:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La cuenta está {cuenta.estado}. No se pueden realizar depósitos."
            )
        
        saldo_anterior = cuenta.saldo
        saldo_nuevo = saldo_anterior + deposito.monto
        
        # Actualizar saldo
        self.repo.update_saldo(cuenta_id, saldo_nuevo)
        
        # Registrar movimiento
        movimiento = Movimiento(
            cuenta_id=cuenta_id,
            tipo=TipoMovimiento.DEPOSITO,
            monto=deposito.monto,
            saldo_anterior=saldo_anterior,
            saldo_nuevo=saldo_nuevo,
            descripcion=deposito.descripcion
        )
        
        movimiento_id = self.repo.crear_movimiento(movimiento)
        
        return OperacionResponse(
            success=True,
            mensaje="Depósito realizado exitosamente",
            cuenta_id=cuenta_id,
            saldo_anterior=saldo_anterior,
            saldo_nuevo=saldo_nuevo,
            monto=deposito.monto,
            movimiento_id=movimiento_id
        )

    def retirar(self, cuenta_id: str, retiro: RetiroRequest) -> OperacionResponse:
        """Realiza un retiro de la cuenta"""
        cuenta = self.obtener_cuenta(cuenta_id)
        
        # Validar estado de la cuenta
        if cuenta.estado != EstadoCuenta.ACTIVA:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La cuenta está {cuenta.estado}. No se pueden realizar retiros."
            )
        
        # Validar saldo suficiente
        if cuenta.saldo < retiro.monto:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Saldo insuficiente. Saldo disponible: {cuenta.saldo} {cuenta.moneda}"
            )
        
        saldo_anterior = cuenta.saldo
        saldo_nuevo = saldo_anterior - retiro.monto
        
        # Actualizar saldo
        self.repo.update_saldo(cuenta_id, saldo_nuevo)
        
        # Registrar movimiento
        movimiento = Movimiento(
            cuenta_id=cuenta_id,
            tipo=TipoMovimiento.RETIRO,
            monto=retiro.monto,
            saldo_anterior=saldo_anterior,
            saldo_nuevo=saldo_nuevo,
            descripcion=retiro.descripcion
        )
        
        movimiento_id = self.repo.crear_movimiento(movimiento)
        
        return OperacionResponse(
            success=True,
            mensaje="Retiro realizado exitosamente",
            cuenta_id=cuenta_id,
            saldo_anterior=saldo_anterior,
            saldo_nuevo=saldo_nuevo,
            monto=retiro.monto,
            movimiento_id=movimiento_id
        )

    def bloquear_cuenta(self, cuenta_id: str) -> Cuenta:
        """Bloquea una cuenta"""
        cuenta = self.obtener_cuenta(cuenta_id)
        
        if cuenta.estado == EstadoCuenta.BLOQUEADA:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La cuenta ya está bloqueada"
            )
        
        self.repo.cambiar_estado(cuenta_id, EstadoCuenta.BLOQUEADA)
        return self.repo.get_by_id(cuenta_id)

    def desbloquear_cuenta(self, cuenta_id: str) -> Cuenta:
        """Desbloquea una cuenta"""
        cuenta = self.obtener_cuenta(cuenta_id)
        
        if cuenta.estado != EstadoCuenta.BLOQUEADA:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La cuenta no está bloqueada"
            )
        
        self.repo.cambiar_estado(cuenta_id, EstadoCuenta.ACTIVA)
        return self.repo.get_by_id(cuenta_id)

    def obtener_movimientos(
        self, 
        cuenta_id: str, 
        filters: Optional[MovimientoFilter] = None,
        limit: int = 50
    ) -> List[Movimiento]:
        """Obtiene el historial de movimientos de una cuenta"""
        # Validar que la cuenta existe
        self.obtener_cuenta(cuenta_id)
        
        return self.repo.get_movimientos(cuenta_id, filters, limit)

    def validar_saldo_disponible(self, cuenta_id: str, monto: float) -> bool:
        """Valida si hay saldo suficiente (útil para otros servicios)"""
        cuenta = self.obtener_cuenta(cuenta_id)
        
        if cuenta.estado != EstadoCuenta.ACTIVA:
            return False
        
        return cuenta.saldo >= monto

    def descontar_saldo(
        self, 
        cuenta_id: str, 
        monto: float, 
        descripcion: str,
        tipo_movimiento: TipoMovimiento = TipoMovimiento.RETIRO
    ) -> OperacionResponse:
        """Descuenta saldo (usado por otros servicios como transferencias/pagos)"""
        cuenta = self.obtener_cuenta(cuenta_id)
        
        if cuenta.estado != EstadoCuenta.ACTIVA:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La cuenta no está activa"
            )
        
        if cuenta.saldo < monto:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Saldo insuficiente"
            )
        
        saldo_anterior = cuenta.saldo
        saldo_nuevo = saldo_anterior - monto
        
        self.repo.update_saldo(cuenta_id, saldo_nuevo)
        
        movimiento = Movimiento(
            cuenta_id=cuenta_id,
            tipo=tipo_movimiento,
            monto=monto,
            saldo_anterior=saldo_anterior,
            saldo_nuevo=saldo_nuevo,
            descripcion=descripcion
        )
        
        movimiento_id = self.repo.crear_movimiento(movimiento)
        
        return OperacionResponse(
            success=True,
            mensaje="Descuento realizado exitosamente",
            cuenta_id=cuenta_id,
            saldo_anterior=saldo_anterior,
            saldo_nuevo=saldo_nuevo,
            monto=monto,
            movimiento_id=movimiento_id
        )

    def acreditar_saldo(
        self, 
        cuenta_id: str, 
        monto: float, 
        descripcion: str,
        tipo_movimiento: TipoMovimiento = TipoMovimiento.DEPOSITO
    ) -> OperacionResponse:
        """Acredita saldo (usado por otros servicios como transferencias)"""
        cuenta = self.obtener_cuenta(cuenta_id)
        
        if cuenta.estado != EstadoCuenta.ACTIVA:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La cuenta no está activa"
            )
        
        saldo_anterior = cuenta.saldo
        saldo_nuevo = saldo_anterior + monto
        
        self.repo.update_saldo(cuenta_id, saldo_nuevo)
        
        movimiento = Movimiento(
            cuenta_id=cuenta_id,
            tipo=tipo_movimiento,
            monto=monto,
            saldo_anterior=saldo_anterior,
            saldo_nuevo=saldo_nuevo,
            descripcion=descripcion
        )
        
        movimiento_id = self.repo.crear_movimiento(movimiento)
        
        return OperacionResponse(
            success=True,
            mensaje="Acreditación realizada exitosamente",
            cuenta_id=cuenta_id,
            saldo_anterior=saldo_anterior,
            saldo_nuevo=saldo_nuevo,
            monto=monto,
            movimiento_id=movimiento_id
        )