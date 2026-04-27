import pytest
import uuid
from datetime import datetime

from app.services.commit_engine.hash import compute_commit_hash
from app.services.commit_engine.service import CommitService
from app.models import Branch, TrackedDatabase, Commit, ChangeEvent, OutboxEvent
from sqlalchemy.future import select

def test_commit_hash_determinism():
    # Same inputs should produce exact same hash
    timestamp = datetime(2026, 1, 1, 12, 0, 0)
    
    events1 = [
        {"table_name": "users", "row_pk": {"id": 1}, "operation": "INSERT"},
        {"table_name": "orders", "row_pk": {"id": 2}, "operation": "UPDATE"},
    ]
    
    # Different order, should sort deterministically
    events2 = [
        {"table_name": "orders", "row_pk": {"id": 2}, "operation": "UPDATE"},
        {"table_name": "users", "row_pk": {"id": 1}, "operation": "INSERT"},
    ]
    
    hash1 = compute_commit_hash(
        parent_hash=None,
        branch_id="123",
        author_id="456",
        message="init",
        change_events=events1,
        timestamp=timestamp
    )
    
    hash2 = compute_commit_hash(
        parent_hash=None,
        branch_id="123",
        author_id="456",
        message="init",
        change_events=events2,
        timestamp=timestamp
    )
    
    assert hash1 == hash2

@pytest.mark.asyncio
async def test_commit_stores_change_events(db_session):
    # Setup
    db_id = uuid.uuid4()
    tracked_db = TrackedDatabase(id=db_id, name="test_db", connection_url="test://")
    db_session.add(tracked_db)
    await db_session.flush()
    
    branch_id = uuid.uuid4()
    branch = Branch(id=branch_id, database_id=db_id, name="main", head_commit_hash=None)
    db_session.add(branch)
    await db_session.commit()
    
    events = [
        {
            "table_name": "users",
            "operation": "INSERT",
            "row_pk": {"id": 1},
            "after_state": {"id": 1, "name": "Alice"}
        }
    ]
    
    # Execute
    commit = await CommitService.create_commit(
        db_session=db_session,
        database_id=db_id,
        branch_id=branch_id,
        author_id=None,
        message="Add Alice",
        change_events=events
    )
    
    # Verify commit
    assert commit.hash is not None
    assert commit.stats["inserts"] == 1
    
    # Verify branch updated
    await db_session.refresh(branch)
    assert branch.head_commit_hash == commit.hash
    
    # Verify events
    result = await db_session.execute(select(ChangeEvent).where(ChangeEvent.commit_hash == commit.hash))
    saved_events = result.scalars().all()
    assert len(saved_events) == 1
    assert saved_events[0].table_name == "users"
    
    # Verify outbox
    outbox_result = await db_session.execute(select(OutboxEvent).where(OutboxEvent.aggregate_id == commit.id))
    outbox_event = outbox_result.scalars().first()
    assert outbox_event is not None
    assert outbox_event.event_type == "CommitCreated"

@pytest.mark.asyncio
async def test_parent_hash_chain(db_session):
    # Setup
    db_id = uuid.uuid4()
    tracked_db = TrackedDatabase(id=db_id, name="test_db_chain", connection_url="test://")
    branch_id = uuid.uuid4()
    branch = Branch(id=branch_id, database_id=db_id, name="main", head_commit_hash=None)
    db_session.add(tracked_db)
    await db_session.flush()
    db_session.add(branch)
    await db_session.commit()
    
    # Commit 1
    commit1 = await CommitService.create_commit(
        db_session=db_session,
        database_id=db_id,
        branch_id=branch_id,
        author_id=None,
        message="First",
        change_events=[{"operation": "INSERT", "table_name": "t1", "row_pk": {"id": 1}}]
    )
    
    # Commit 2
    commit2 = await CommitService.create_commit(
        db_session=db_session,
        database_id=db_id,
        branch_id=branch_id,
        author_id=None,
        message="Second",
        change_events=[{"operation": "INSERT", "table_name": "t2", "row_pk": {"id": 2}}]
    )
    
    assert commit2.parent_hash == commit1.hash
    
    await db_session.refresh(branch)
    assert branch.head_commit_hash == commit2.hash
