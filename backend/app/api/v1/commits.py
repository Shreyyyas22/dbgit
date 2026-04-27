from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import Any

from ...api.deps import get_db
from ...models import Commit, TrackedDatabase, Branch
from ...schemas import CommitCreate, CommitResponse
from ...services.commit_engine import CommitService

router = APIRouter()

@router.post("", response_model=CommitResponse, status_code=status.HTTP_201_CREATED)
async def create_commit(
    db_id: UUID,
    commit_in: CommitCreate,
    db: AsyncSession = Depends(get_db)
):
    # Verify DB exists
    db_record = await db.get(TrackedDatabase, db_id)
    if not db_record:
        raise HTTPException(status_code=404, detail="Database not found")

    try:
        commit = await CommitService.create_commit(
            db_session=db,
            database_id=db_id,
            branch_id=commit_in.branch_id,
            author_id=commit_in.author_id,
            message=commit_in.message,
            change_events=[ce.model_dump() for ce in commit_in.change_events]
        )
        return commit
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=list[CommitResponse])
async def list_commits(
    db_id: UUID,
    branch_id: UUID | None = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Commit).where(Commit.database_id == db_id).order_by(Commit.committed_at.desc())
    if branch_id:
        # Simplistic branch filtering for MVP
        query = query.where(Commit.branch_id == branch_id)
    
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{hash}", response_model=CommitResponse)
async def get_commit(
    db_id: UUID,
    hash: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Commit).where(Commit.database_id == db_id, Commit.hash == hash)
    )
    commit = result.scalars().first()
    if not commit:
        raise HTTPException(status_code=404, detail="Commit not found")
    return commit
