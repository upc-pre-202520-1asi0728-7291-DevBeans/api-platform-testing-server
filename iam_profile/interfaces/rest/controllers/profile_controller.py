from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Union
from shared.domain.database import get_db
from iam_profile.interfaces.rest.resources.producer_profile_resource import ProducerProfileResource
from iam_profile.interfaces.rest.resources.cooperative_profile_resource import CooperativeProfileResource
from iam_profile.domain.model.queries.get_producer_profile_query import GetProducerProfileQuery
from iam_profile.domain.model.queries.get_cooperative_profile_query import GetCooperativeProfileQuery
from iam_profile.domain.model.queries.get_user_by_id_query import GetUserByIdQuery
from iam_profile.application.internal.queryservices.profile_query_service import ProfileQueryService
from iam_profile.application.internal.queryservices.user_query_service import UserQueryService

router = APIRouter(prefix="/api/v1/profiles", tags=["Profiles"])


@router.get("/{user_id}", response_model=Union[ProducerProfileResource, CooperativeProfileResource])
async def get_profile(
        user_id: int,
        db: Session = Depends(get_db)
):
    """
    Obtiene el perfil completo de un usuario (productor o cooperativa)
    """
    user_query_service = UserQueryService(db)
    profile_query_service = ProfileQueryService(db)

    # Verificar que el usuario existe
    user_query = GetUserByIdQuery(user_id=user_id)
    user = user_query_service.handle_get_user_by_id(user_query)

    # Obtener perfil según tipo de usuario
    if user.user_type.value == "PRODUCER":
        query = GetProducerProfileQuery(user_id=user_id)
        profile = profile_query_service.handle_get_producer_profile(query)
        return ProducerProfileResource.model_validate(profile)
    else:  # COOPERATIVE
        query = GetCooperativeProfileQuery(user_id=user_id)
        profile = profile_query_service.handle_get_cooperative_profile(query)
        return CooperativeProfileResource.model_validate(profile)


@router.get("/producer/{producer_id}", response_model=ProducerProfileResource)
async def get_producer_profile(
        producer_id: int,
        db: Session = Depends(get_db)
):
    """
    Obtiene el perfil específico de un productor
    """
    profile_query_service = ProfileQueryService(db)
    query = GetProducerProfileQuery(user_id=producer_id)
    profile = profile_query_service.handle_get_producer_profile(query)
    return ProducerProfileResource.model_validate(profile)


@router.get("/cooperative/{cooperative_id}", response_model=CooperativeProfileResource)
async def get_cooperative_profile(
        cooperative_id: int,
        db: Session = Depends(get_db)
):
    """
    Obtiene el perfil específico de una cooperativa
    """
    profile_query_service = ProfileQueryService(db)
    query = GetCooperativeProfileQuery(user_id=cooperative_id)
    profile = profile_query_service.handle_get_cooperative_profile(query)
    return CooperativeProfileResource.model_validate(profile)