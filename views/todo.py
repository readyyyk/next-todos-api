from typing import List

from fastapi import HTTPException, Depends, APIRouter, Response, Security
from fastapi_jwt import JwtAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from config import jwt_config
from services.database import get_session
from views.schemas.todo import TodoSchemaCreate, TodoSchema, TodoSchemaUpdate, TodoWithOwnerSchema
from models.todo import Todo as TodoModel
from models.user import User as UserModel

router = APIRouter(prefix='/todos', tags=['Todo'])


@router.get('/my', response_model=List[TodoSchema])
async def get_todos_by_owner(
        credentials: JwtAuthorizationCredentials = Security(jwt_config.access_security),
        session: AsyncSession = Depends(get_session)):
    todo_list = await TodoModel.get_by_owner(session, credentials.subject["id"])
    if todo_list is None:
        raise HTTPException(status_code=404, detail="Todos for this owner.id not found!")
    return todo_list


@router.post('/create', response_model=TodoSchema)
async def create_todo(
        todo_data: TodoSchemaCreate,
        credentials: JwtAuthorizationCredentials = Security(jwt_config.access_security),
        session: AsyncSession = Depends(get_session)):
    try:
        payload = todo_data.model_dump(exclude_none=True)
        todo = await TodoModel.create_for(credentials.subject["id"], session, **payload)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail="Error creating todo!")
    if 'id' not in todo.__dict__:
        print(todo.__dict__)
        raise HTTPException(status_code=400, detail="Error creating todo!")
    return todo


@router.put('/{id}/update', response_model=TodoSchema)
async def update_todo(
        id: int,
        data_to_update: TodoSchemaUpdate,
        credentials: JwtAuthorizationCredentials = Security(jwt_config.access_security),
        session: AsyncSession = Depends(get_session)):
    try:
        payload = data_to_update.model_dump(exclude_none=True)
        todo = await TodoModel.get(session, id=id)
        if todo is None:
            raise HTTPException(status_code=404, detail="Todo not found!")
        if todo.owner_id != credentials.subject["id"]:
            raise HTTPException(status_code=400, detail="Todo you want to update can't be accessed by you!")
        todo = await todo.update_inst(session, **payload)
        return todo
    except HTTPException as e:
        raise e
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.delete('/{id}/delete')
async def delete_todo(
        id: int,
        credentials: JwtAuthorizationCredentials = Security(jwt_config.access_security),
        session: AsyncSession = Depends(get_session)):
    try:
        todo = await TodoModel.get(session, id)
        if todo is None:
            raise HTTPException(status_code=404, detail="Todo not found!")
        if todo.owner_id != credentials.subject["id"]:
            raise HTTPException(status_code=400, detail="Todo you want to update can't be accessed by you!")
        is_deleted = await todo.delete_inst(session)
    except HTTPException as e:
        raise e
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail=str(e))
    if is_deleted:
        return Response(status_code=200, content="Successfully deleted todo")
    else:
        raise HTTPException(status_code=404, detail="Todo not found!")


@router.get('/{id}/with-owner', response_model=TodoWithOwnerSchema)
async def get_todo_with_owner_data(
        id: int,
        credentials: JwtAuthorizationCredentials = Security(jwt_config.access_security),
        session: AsyncSession = Depends(get_session)):
    todo = await get_todo(id, credentials, session)
    owner = await UserModel.get(session, todo.owner_id)
    if owner is None:
        raise HTTPException(status_code=404, detail="Owner for this todo.id not found!")
    return TodoWithOwnerSchema(**todo.__dict__, owner=owner)


@router.get('/{id}', response_model=TodoSchema)
async def get_todo(
        id: int,
        credentials: JwtAuthorizationCredentials = Security(jwt_config.access_security),
        session: AsyncSession = Depends(get_session)):
    todo = await TodoModel.get(session, id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo with this id not found!")
    if todo.owner_id != credentials.subject["id"]:
        raise HTTPException(status_code=401, detail="Requested todo is not yours!")
    return todo
