"""FastAPI User API Controller."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request

from app.dependencies import get_jwt_service, get_user_service
from app.exceptions.user_exception import (
    UserAlreadyExistsException,
    UserIDNotFoundException,
    WrongEmailOrPasswordException,
)
from app.middleware.jwt_middleware import JWTBearer
from app.models.user_model import UserModel
from app.schemas.user_schema import UserCreateRequest, UserLoginRequest, UserResponse, UserResponseWithToken
from app.services.jwt_service import JWTService
from app.services.user_service import UserService
from app.utils.logger_util import get_logger

router = APIRouter(prefix="/user", tags=["user"])

def _convert_user_to_response(user: UserModel) -> UserResponse:
    """Convert UserModel to UserResponse schema using from_attributes."""
    return UserResponse.model_validate(user, from_attributes=True)

@router.post("/register", response_model=UserResponseWithToken)
async def register_user(
    user_data: UserCreateRequest,
    user_service: Annotated[UserService, Depends(get_user_service)],
    jwt_service: Annotated[JWTService, Depends(get_jwt_service)],
):
    try:
        user = await user_service.create_user(user_data)
        token = jwt_service.generate_token(user.id)

        return UserResponseWithToken(**_convert_user_to_response(user).model_dump(), token=token)
    except UserAlreadyExistsException as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        get_logger().error("Error creating user: %s", str(e))

        # get_logger().exception(pr)
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.post("/login", response_model=UserResponseWithToken)
async def login_user(
    login_data: UserLoginRequest,
    user_service: Annotated[UserService, Depends(get_user_service)],
    jwt_service: Annotated[JWTService, Depends(get_jwt_service)],
):
    try:
        user = await user_service.verify_user_exists(login_data)
        token = jwt_service.generate_token(user.id)
        return UserResponseWithToken(**_convert_user_to_response(user).model_dump(), token=token)
    except WrongEmailOrPasswordException:
        raise HTTPException(status_code=401, detail="Wrong email or password")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/profile", response_model=UserResponse, dependencies=[Depends(JWTBearer())])
async def get_user_by_id(
    user_service: Annotated[UserService, Depends(get_user_service)],
    request: Request = None,
):
    try:
        user_id = request.state.user_id
        user = await user_service.get_user_by_id(user_id)
        return _convert_user_to_response(user)
    except UserIDNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
