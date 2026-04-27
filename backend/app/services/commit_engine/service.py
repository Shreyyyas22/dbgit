import uuid
from datetime import datetime
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ...models import Commit, ChangeEvent, Branch, OutboxEvent, TrackedDatabase
from .hash import compute_commit_hash

class CommitService:
    @staticmethod
    async def create_commit(
        db_session: AsyncSession,
        database_id: uuid.UUID,
        branch_id: uuid.UUID,
        author_id: uuid.UUID | None,
        message: str,
        change_events: list[dict[str, Any]],
    ) -> Commit:
        # 1. Get current branch HEAD
        branch = await db_session.get(Branch, branch_id)
        if not branch:
            raise ValueError(f"Branch {branch_id} not found")
        
        parent_hash = branch.head_commit_hash
        timestamp = datetime.utcnow()

        # 2. Compute commit hash
        commit_hash = compute_commit_hash(
            parent_hash=parent_hash,
            branch_id=str(branch_id),
            author_id=str(author_id) if author_id else "system",
            message=message,
            change_events=change_events,
            timestamp=timestamp,
        )

        # 3. Store commit object
        tables_affected = list({e["table_name"] for e in change_events})
        stats = {
            "inserts": sum(1 for e in change_events if e["operation"] == "INSERT"),
            "updates": sum(1 for e in change_events if e["operation"] == "UPDATE"),
            "deletes": sum(1 for e in change_events if e["operation"] == "DELETE"),
        }
        
        commit = Commit(
            hash=commit_hash,
            parent_hash=parent_hash,
            branch_id=branch_id,
            database_id=database_id,
            author_id=author_id,
            message=message,
            committed_at=timestamp,
            tables_affected=tables_affected,
            stats=stats,
        )
        db_session.add(commit)
        await db_session.flush()

        # 4. Store all change events linked to this commit
        for seq, event_data in enumerate(change_events):
            event = ChangeEvent(
                commit_hash=commit_hash,
                operation=event_data["operation"],
                table_name=event_data["table_name"],
                schema_name=event_data.get("schema_name", "public"),
                row_pk=event_data["row_pk"],
                before_state=event_data.get("before_state"),
                after_state=event_data.get("after_state"),
                changed_columns=event_data.get("changed_columns"),
                sequence_num=seq,
            )
            db_session.add(event)

        # 5. Update branch HEAD
        branch.head_commit_hash = commit_hash

        # 6. Write outbox event (for Kafka, processed async)
        outbox_event = OutboxEvent(
            event_type="CommitCreated",
            aggregate_id=commit.id, # id will be generated since we use uuid4 default
            payload={
                "commit_hash": commit_hash,
                "database_id": str(database_id),
                "branch_id": str(branch_id),
                "author_id": str(author_id) if author_id else None,
                "timestamp": timestamp.isoformat(),
            },
        )
        db_session.add(outbox_event)

        # 7. Flush all in one transaction
        await db_session.commit()
        await db_session.refresh(commit)
        
        return commit
