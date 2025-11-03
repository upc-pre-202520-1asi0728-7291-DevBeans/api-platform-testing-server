from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import date
from coffee_lot_management.domain.model.aggregates.coffee_lot import (
    CoffeeLot, LotStatus, CoffeeVariety, ProcessingMethod
)
from coffee_lot_management.domain.model.entities.origin_data import OriginData
from coffee_lot_management.domain.model.commands.register_coffee_lot_command import RegisterCoffeeLotCommand
from coffee_lot_management.domain.model.commands.update_coffee_lot_command import UpdateCoffeeLotCommand
from coffee_lot_management.domain.model.commands.change_lot_status_command import ChangeLotStatusCommand
from coffee_lot_management.domain.model.commands.delete_coffee_lot_command import DeleteCoffeeLotCommand
from coffee_lot_management.infrastructure.persistence.database.repositories.coffee_lot_repository import CoffeeLotRepository
from coffee_lot_management.domain.services.lot_number_generator_service import LotNumberGeneratorService


class CoffeeLotCommandService:
    """Servicio de comandos para CoffeeLot"""

    def __init__(self, db: Session):
        self.db = db
        self.repository = CoffeeLotRepository(db)
        self.lot_number_service = LotNumberGeneratorService(db)

    def handle_register_coffee_lot(self, command: RegisterCoffeeLotCommand) -> CoffeeLot:
        """Registra un nuevo lote de café"""
        # Validar fecha de cosecha (no futura)
        if command.harvest_date > date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Harvest date cannot be in the future"
            )

        # Generar número único de lote
        lot_number = self.lot_number_service.generate_lot_number()

        # Crear lote
        coffee_lot = CoffeeLot(
            lot_number=lot_number,
            producer_id=command.producer_id,
            harvest_date=command.harvest_date,
            coffee_variety=CoffeeVariety[command.coffee_variety.upper()],
            quantity=command.quantity,
            processing_method=ProcessingMethod[command.processing_method.upper()],
            latitude=command.latitude,
            longitude=command.longitude
        )

        # Asignar datos adicionales
        if command.altitude:
            coffee_lot.altitude = command.altitude
        if command.soil_type:
            coffee_lot.soil_type = command.soil_type
        if command.climate_zone:
            coffee_lot.climate_zone = command.climate_zone
        if command.farm_section:
            coffee_lot.farm_section = command.farm_section

        # Guardar lote
        coffee_lot = self.repository.save(coffee_lot)

        # Crear datos de origen si hay altitud
        if command.altitude:
            origin_data = OriginData(
                coffee_lot_id=coffee_lot.id,
                altitude=command.altitude,
                latitude=command.latitude,
                longitude=command.longitude,
                soil_type=command.soil_type,
                climate_zone=command.climate_zone,
                farm_section=command.farm_section
            )
            self.db.add(origin_data)
            self.db.commit()

        return coffee_lot

    def handle_update_coffee_lot(self, command: UpdateCoffeeLotCommand) -> CoffeeLot:
        """Actualiza información de un lote existente"""
        coffee_lot = self.repository.find_by_id(command.lot_id)
        if not coffee_lot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coffee lot not found"
            )

        # No permitir cambios si ya está clasificado
        if coffee_lot.status in [LotStatus.CLASSIFIED, LotStatus.CERTIFIED, LotStatus.SHIPPED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update lot after classification"
            )

        # Actualizar campos
        if command.quantity:
            coffee_lot.update_quantity(command.quantity)
        if command.processing_method:
            coffee_lot.processing_method = ProcessingMethod[command.processing_method.upper()]
        if command.altitude:
            coffee_lot.altitude = command.altitude
        if command.soil_type:
            coffee_lot.soil_type = command.soil_type
        if command.climate_zone:
            coffee_lot.climate_zone = command.climate_zone

        return self.repository.save(coffee_lot)

    def handle_change_lot_status(self, command: ChangeLotStatusCommand) -> CoffeeLot:
        """Cambia el estado de un lote"""
        coffee_lot = self.repository.find_by_id(command.lot_id)
        if not coffee_lot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coffee lot not found"
            )

        try:
            new_status = LotStatus[command.new_status.upper()]
            coffee_lot.change_status(new_status)
            return self.repository.save(coffee_lot)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    def handle_delete_coffee_lot(self, command: DeleteCoffeeLotCommand) -> None:
        """Elimina un lote del sistema"""
        coffee_lot = self.repository.find_by_id(command.lot_id)
        if not coffee_lot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coffee lot not found"
            )

        # Verificar si puede ser eliminado
        if not coffee_lot.can_be_deleted():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only lots in REGISTERED status can be deleted"
            )

        self.repository.delete(coffee_lot)