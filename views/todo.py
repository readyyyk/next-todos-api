from fastapi import HTTPException, Depends, APIRouter, Response
from sqlalchemy.ext.asyncio import AsyncSession

from services.database import get_session
from views.schemas.todo import TodoSchemaCreate, TodoSchema, TodoSchemaUpdate
from models.todo import Todo as TodoModel

router = APIRouter(prefix='/todos', tags=['Todo'])


@router.get('/{id}', response_model=TodoSchema)
async def get_todo(id: int, session: AsyncSession = Depends(get_session)):
    user = await TodoModel.get(session, id)
    if user is None:
        raise HTTPException(status_code=404, detail="Todo with this id not found!")
    return user


@router.post('/create', response_model=TodoSchema)
async def create_todo(todo_data: TodoSchemaCreate, session: AsyncSession = Depends(get_session)):
    todo = None
    try:
        transaction = todo_data.model_dump(exclude_none=True)
        todo = await TodoModel.create(session, **transaction)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail="Error creating todo!")
    finally:
        if 'id' not in todo.__dict__:
            print(todo.__dict__)
            raise HTTPException(status_code=400, detail="Error creating todo!")
        return todo


@router.put('/{id}/update', response_model=TodoSchema)
async def update_todo(id: int, data_to_update: TodoSchemaUpdate, session: AsyncSession = Depends(get_session)):
    try:
        transaction = data_to_update.model_dump(exclude_none=True)
        todo = await TodoModel.update(session, **transaction, id=id)
        return todo
    except HTTPException as e:
        raise e
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail="Error updating todo!")


@router.delete('/{id}/delete')
async def delete_todo(id: int, session: AsyncSession = Depends(get_session)):
    try:
        is_deleted = await TodoModel.delete(session, id)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail="Error deleting todo")
    if is_deleted:
        return Response(status_code=200, content="Successfully deleted todo")
    else:
        raise HTTPException(status_code=404, detail="Todo not found!")
