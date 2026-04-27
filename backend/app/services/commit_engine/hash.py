import hashlib
import json
from datetime import datetime
from typing import Any

def compute_commit_hash(
    parent_hash: str | None,
    branch_id: str,
    author_id: str,
    message: str,
    change_events: list[dict[str, Any]],
    timestamp: datetime,
) -> str:
    """
    Content-addressable hash — same content always produces same hash.
    Changes from Git: we also include a sorted representation of row changes
    so the hash captures the actual data state, not just metadata.
    """
    content = {
        "parent": parent_hash or "ROOT",
        "branch": branch_id,
        "author": author_id,
        "message": message,
        "timestamp": timestamp.isoformat(),
        # Sort changes for determinism
        "changes_fingerprint": _hash_changes(change_events),
    }
    canonical = json.dumps(content, sort_keys=True)
    return hashlib.sha256(canonical.encode()).hexdigest()

def _hash_changes(events: list[dict[str, Any]]) -> str:
    """Create a deterministic fingerprint of all change events."""
    # We sort by table name and then by row_pk (stringified)
    sorted_events = sorted(events, key=lambda e: (e["table_name"], json.dumps(e["row_pk"], sort_keys=True)))
    fingerprint = json.dumps(sorted_events, sort_keys=True)
    return hashlib.sha256(fingerprint.encode()).hexdigest()
