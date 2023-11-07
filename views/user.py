from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from services.database import get_session
from views.schemas.user import UserSchema, UserSchemaCreate
from models.user import User as UserModel

router = APIRouter(prefix='/users', tags=['user'])


@router.get('/{id}', response_model=UserSchema)
async def get_user(id: int, session: AsyncSession = Depends(get_session)):
    user = await UserModel.get(session, id)
    if user is None:
        raise HTTPException(status_code=404, detail="User with this id not found!")
    return user


@router.post('/create', response_model=UserSchema)
async def get_user(user_data: UserSchemaCreate, session: AsyncSession = Depends(get_session)):
    user = None
    try:
        new_user_data = user_data.model_dump(exclude_none=True)
        user = await UserModel.create(session, **new_user_data)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        if 'id' not in user.__dict__:
            raise HTTPException(status_code=400, detail="User with this name already exists!")

        return user
