from fastapi import APIRouter, Depends, HTTPException, Response, Security
from fastapi_jwt import JwtAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from config import jwt_config
from services.database import get_session
from views.auth import login
from views.schemas.user import UserSchema, UserSchemaCreate, UserSchemaUpdate, UserSchemaSignin, UserSchemaCreateResponse
from models.user import User as UserModel
from utils import without_keys, JWTPayloadError

router = APIRouter(prefix='/users', tags=['User'])


@router.get('/me', response_model=UserSchema)
async def me(session: AsyncSession = Depends(get_session),
             credentials: JwtAuthorizationCredentials = Security(jwt_config.access_security)):
    return await get_user(credentials.subject["id"], session)


@router.post('/create', response_model=UserSchemaCreateResponse)
async def create_user(user_data: UserSchemaCreate, session: AsyncSession = Depends(get_session)):
    try:
        new_user_data = user_data.model_dump(exclude_none=True)
        user = await UserModel.create(session, **new_user_data)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=str(e))
    if 'id' not in user.__dict__:
        raise HTTPException(status_code=400, detail="Error creating user!")
    tokens = await login(UserSchemaSignin(username=user_data.username, password=user_data.password), session=session)
    return UserSchemaCreateResponse(**user.__dict__, tokens=tokens)


@router.put('/update', response_model=UserSchema)
async def update_user(
        data_to_update: UserSchemaUpdate,
        session: AsyncSession = Depends(get_session),
        credentials: JwtAuthorizationCredentials = Security(jwt_config.access_security),
):
    try:
        transaction = data_to_update.model_dump(exclude_none=True)
        todo = await UserModel.update(session, **transaction, id=credentials.subject["id"])
        return without_keys(todo.__dict__, ["password"])
    except HTTPException as e:
        raise e
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail="Error updating user!")


@router.delete('/delete')
async def delete_user(
        credentials: JwtAuthorizationCredentials = Security(jwt_config.access_security),
        session: AsyncSession = Depends(get_session)
):
    try:
        is_deleted = await UserModel.delete(session, credentials.subject["id"])
        if is_deleted:
            return Response(status_code=200, content="Successfully deleted user")
        else:
            raise HTTPException(status_code=404, detail="User not found!")
    except KeyError as e:
        print(str(e))
        raise JWTPayloadError(detail=str(e))
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail="Error deleting user")


@router.get('/{id}', response_model=UserSchema)
async def get_user(id: int, session: AsyncSession = Depends(get_session)):
    user = await UserModel.get(session, id)
    if user is None:
        raise HTTPException(status_code=404, detail="User with this id not found!")
    return without_keys(user.__dict__, ["password"])
