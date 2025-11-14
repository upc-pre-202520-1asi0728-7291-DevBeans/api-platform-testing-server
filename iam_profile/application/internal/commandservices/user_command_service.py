from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from iam_profile.domain.model.aggregates.user import User, UserType
from iam_profile.domain.model.entities.producer_profile import ProducerProfile
from iam_profile.domain.model.entities.cooperative_profile import CooperativeProfile
from iam_profile.domain.model.commands.register_producer_command import RegisterProducerCommand
from iam_profile.domain.model.commands.register_cooperative_command import RegisterCooperativeCommand
from iam_profile.domain.model.commands.update_profile_command import UpdateProfileCommand
from iam_profile.domain.model.commands.change_password_command import ChangePasswordCommand
from iam_profile.infrastructure.persistence.database.repositories.user_repository import UserRepository
from iam_profile.infrastructure.persistence.database.repositories.producer_profile_repository import \
    ProducerProfileRepository
from iam_profile.infrastructure.persistence.database.repositories.cooperative_profile_repository import \
    CooperativeProfileRepository


class UserCommandService:
    """Servicio de comandos para User"""

    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)
        self.producer_repository = ProducerProfileRepository(db)
        self.cooperative_repository = CooperativeProfileRepository(db)


    def handle_register_producer(self, command: RegisterProducerCommand) -> User:
        """
        Registra un nuevo productor independiente
        """
        # Validar email único
        if self.user_repository.exists_by_email(command.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Crear usuario
        user = User(
            email=command.email,
            password=command.password,
            user_type=UserType.PRODUCER
        )

        # Guardar usuario
        user = self.user_repository.save(user)

        # Crear perfil de productor
        producer_profile = ProducerProfile(
            user_id=user.id,
            first_name=command.first_name,
            last_name=command.last_name,
            document_number=command.document_number,
            document_type=command.document_type,
            phone_number=command.phone_number,
            city=command.city,
            country=command.country,
            farm_name=command.farm_name,
            latitude=command.latitude,
            longitude=command.longitude,
            altitude=command.altitude,
            region=command.region,
            hectares=command.hectares,
            coffee_varieties=command.coffee_varieties or [],
            production_capacity=command.production_capacity
        )

        self.producer_repository.save(producer_profile)

        return user


    def handle_register_cooperative(self, command: RegisterCooperativeCommand) -> User:
        """
        Registra una nueva cooperativa
        """
        # Validar email único
        if self.user_repository.exists_by_email(command.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Validar registro legal único
        if self.cooperative_repository.find_by_legal_registration(command.legal_registration_number):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Legal registration number already exists"
            )

        # Crear usuario
        user = User(
            email=command.email,
            password=command.password,
            user_type=UserType.COOPERATIVE
        )

        user = self.user_repository.save(user)

        # Crear perfil de cooperativa
        cooperative_profile = CooperativeProfile(
            user_id=user.id,
            cooperative_name=command.cooperative_name,
            legal_registration_number=command.legal_registration_number,
            phone_number=command.phone_number,
            address=command.address,
            city=command.city,
            country=command.country,
            legal_representative_name=command.legal_representative_name,
            legal_representative_email=command.legal_representative_email,
            processing_capacity=command.processing_capacity,
            certifications=command.certifications or []
        )

        self.cooperative_repository.save(cooperative_profile)

        return user


    def handle_update_profile(self, command: UpdateProfileCommand) -> User:
        """
        Actualiza el perfil de un usuario
        """
        user = self.user_repository.find_by_id(command.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if user.user_type == UserType.PRODUCER:
            profile = self.producer_repository.find_by_user_id(user.id)
            if profile:
                # Solo actualiza los campos que no son None
                if command.first_name is not None:
                    profile.first_name = command.first_name
                if command.last_name is not None:
                    profile.last_name = command.last_name
                if command.phone_number is not None:
                    profile.phone_number = command.phone_number
                if command.city is not None:
                    profile.city = command.city
                if command.farm_name is not None:
                    profile.farm_name = command.farm_name
                if command.hectares is not None:
                    profile.hectares = command.hectares
                if command.production_capacity is not None:
                    profile.production_capacity = command.production_capacity

                self.producer_repository.save(profile)

        return user


    def handle_change_password(self, command: ChangePasswordCommand) -> User:
        """
        Cambia la contraseña de un usuario
        """
        user = self.user_repository.find_by_id(command.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Verificar contraseña actual
        if not user.verify_password(command.current_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        # Cambiar contraseña
        user.change_password(command.new_password)
        return self.user_repository.save(user)