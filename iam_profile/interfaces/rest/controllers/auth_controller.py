from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, UTC
from jose import jwt
from shared.domain.database import get_db
from shared.infrastructure.persistence.database.repositories.settings import settings
from iam_profile.interfaces.rest.resources.register_producer_resource import RegisterProducerResource
from iam_profile.interfaces.rest.resources.register_cooperative_resource import RegisterCooperativeResource
from iam_profile.interfaces.rest.resources.user_resource import UserResource
from iam_profile.interfaces.rest.resources.login_request_resource import LoginRequest
from iam_profile.interfaces.rest.resources.login_response_resource import LoginResponse
from iam_profile.domain.model.commands.register_producer_command import RegisterProducerCommand
from iam_profile.domain.model.commands.register_cooperative_command import RegisterCooperativeCommand
from iam_profile.domain.model.queries.get_user_by_email_query import GetUserByEmailQuery
from iam_profile.application.internal.commandservices.user_command_service import UserCommandService
from iam_profile.application.internal.queryservices.user_query_service import UserQueryService

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


def create_access_token(data: dict, expires_delta: timedelta = None):
    """Crea un token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


@router.post("/register/producer", response_model=UserResource, status_code=status.HTTP_201_CREATED)
async def register_producer(
        resource: RegisterProducerResource,
        db: Session = Depends(get_db)
):
    """
    Registra un nuevo productor independiente
    """
    command = RegisterProducerCommand(**resource.model_dump())
    command_service = UserCommandService(db)
    user = command_service.handle_register_producer(command)
    return UserResource.model_validate(user)


@router.post("/register/cooperative", response_model=UserResource, status_code=status.HTTP_201_CREATED)
async def register_cooperative(
        resource: RegisterCooperativeResource,
        db: Session = Depends(get_db)
):
    """
    Registra una nueva cooperativa
    """
    command = RegisterCooperativeCommand(**resource.model_dump())
    command_service = UserCommandService(db)
    user = command_service.handle_register_cooperative(command)
    return UserResource.model_validate(user)


@router.post("/login", response_model=LoginResponse)
async def login(
        login_request: LoginRequest,
        db: Session = Depends(get_db)
):
    """
    Inicia sesión con email y contraseña
    """
    query_service = UserQueryService(db)

    try:
        query = GetUserByEmailQuery(email=login_request.email)
        user = query_service.handle_get_user_by_email(query)

        # Verificar contraseña
        if not user.verify_password(login_request.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verificar estado del usuario
        if user.status != "ACTIVE":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is not active"
            )

        # Crear token de acceso
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id, "user_type": user.user_type.value},
            expires_delta=access_token_expires
        )

        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResource.model_validate(user)
        )

    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/logout")
async def logout():
    """
    Cierra sesión (en el cliente se debe eliminar el token)
    """
    return {"message": "Successfully logged out"}