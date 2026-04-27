from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID

from ...api.deps import get_db
from ...models import TrackedDatabase, Branch
from ...schemas import DatabaseCreate, DatabaseResponse

router = APIRouter()

@router.post("", response_model=DatabaseResponse, status_code=status.HTTP_201_CREATED)
async def register_database(
    db_in: DatabaseCreate,
    db: AsyncSession = Depends(get_db)
):
    # Check if exists
    result = await db.execute(select(TrackedDatabase).where(TrackedDatabase.name == db_in.name))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Database with this name already exists")
    
    # Create DB
    new_db = TrackedDatabase(
        name=db_in.name,
        connection_url=db_in.connection_url,
        config=db_in.config
    )
    db.add(new_db)
    await db.flush()

    # Create default 'main' branch
    main_branch = Branch(
        database_id=new_db.id,
        name="main",
        is_default=True
    )
    db.add(main_branch)
    await db.commit()
    await db.refresh(new_db)

    return new_db
