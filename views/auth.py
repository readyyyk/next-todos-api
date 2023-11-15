from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi_jwt import JwtAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from config import jwt_config
from services.database import get_session
from views.schemas.user import UserSchemaSignin
from models.user import User as UserModel

router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post('/login')
async def login(user: UserSchemaSignin, session: AsyncSession = Depends(get_session)):
    user_data = await UserModel.login(session, user.username, user.password)

    if user_data is None:
        raise HTTPException(status_code=401, detail="Invalid username or password!")

    access_token = jwt_config.access_security.create_access_token(subject={"id": user_data.id})
    refresh_token = jwt_config.refresh_security.create_refresh_token(subject={"id": user_data.id})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


@router.post('/refresh-tokens')
async def refresh_tokens(credentials: JwtAuthorizationCredentials = Security(jwt_config.refresh_security)):
    access_token = jwt_config.access_security.create_access_token(subject=credentials.subject)
    refresh_token = jwt_config.refresh_security.create_refresh_token(subject=credentials.subject)

    return {"access_token": access_token, "refresh_token": refresh_token}
