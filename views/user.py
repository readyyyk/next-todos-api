from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from services.database import get_session
from views.schemas.user import UserSchema, UserSchemaCreate, UserSchemaUpdate
from models.user import User as UserModel
from utils import without_keys


router = APIRouter(prefix='/users', tags=['User'])


@router.get('/{id}', response_model=UserSchema)
async def get_user(id: int, session: AsyncSession = Depends(get_session)):
    user = await UserModel.get(session, id)
    if user is None:
        raise HTTPException(status_code=404, detail="User with this id not found!")
    return without_keys(user.__dict__, ["password"])


@router.post('/create', response_model=UserSchema)
async def create_user(user_data: UserSchemaCreate, session: AsyncSession = Depends(get_session)):
    try:
        new_user_data = user_data.model_dump(exclude_none=True)
        user = await UserModel.create(session, **new_user_data)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=str(e))
    if 'id' not in user.__dict__:
        raise HTTPException(status_code=400, detail="Error creating user!")
    return user


@router.put('/{id}/update', response_model=UserSchema)
async def update_user(id: int, data_to_update: UserSchemaUpdate, session: AsyncSession = Depends(get_session)):
    try:
        transaction = data_to_update.model_dump(exclude_none=True)
        todo = await UserModel.update(session, **transaction, id=id)
        return without_keys(todo.__dict__, ["password"])
    except HTTPException as e:
        raise e
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail="Error updating user!")


@router.delete('/{id}/delete')
async def delete_user(id: int, session: AsyncSession = Depends(get_session)):
    try:
        is_deleted = await UserModel.delete(session, id)
        if is_deleted:
            return Response(status_code=200, content="Successfully deleted user")
        else:
            raise HTTPException(status_code=404, detail="User not found!")
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail="Error deleting user")
