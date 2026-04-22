from fastapi import APIRouter, HTTPException, Query
import base64
from app.database import get_db
from app.models import EventCreate, EventResponse
import json
from datetime import datetime
import sqlite3
from typing import Optional, List

router = APIRouter()

@router.post("/events")
def create_event(event: EventCreate):
    "Create an event"
    with get_db() as conn:
        try:
            cursor = conn.cursor()
            recorded_at = datetime.utcnow().isoformat() + "Z"
            cursor.execute("""
                INSERT INTO events events
                (user_id, occurred_at, recorded_at, kind, tags, payload)
                VALUES(?, ?, ?, ?, ?, ?)
            """,
            (
                event.user_id,
                event.occurred_at,
                recorded_at,
                event.kind,
                json.dumps(event.tags or []),
                json.dumps(event.payload or {})
            ))
            conn.commit()
            event_id = cursor.lastrowid
            return {"id": event_id, "status": "created",}
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=409, detail={
                "error": "Event already exists",
                "code": "duplicate_eevent"
            })
            
            
@router.get("/events")
def list_events(
    user_id: Optional[str] = None,
    kind: Optional[List[str]] = Query(None),
    tag: Optional[List[str]] = Query(None),
    from_: Optional[str] = Query(None, alias="from"),
    to: Optional[str] = Query(None),
    limit: int = 50,
    cursor: Optional[int] = None
):
    conditions = []
    params = []
    if user_id:
        conditions.append("user_id = ?")
        params.append(user_id)
    if kind:
        placeholder = ",".join("?"*len(kind))
        conditions.append(f"kind IN ({placeholder})")
        params.extend(kind)
    
    if tag:
        for t in tag:
            conditions.append("EXISTS (SELECT 1 FROM json_each(tags) WHERE value = ?)")
            params.append(t)
    
    if from_:
        conditions.append("occurred_at >= ?")
        params.append(from_)
    if to:
        conditions.append("occurred_at <= ?")
        params.append(to)
    
    if cursor:
        try:
            decoded = base64.b64decode(cursor).decode()
            cursor_occured_at, cursor_id = decoded.split(",", 1)
            conditions.append(
                "(occurred_at < ? OR (occurred_at = ? AND id < ?))"
            )
            params.extend([cursor_occured_at, cursor_occured_at, cursor_id])
        except Exception:
            raise HTTPException(status_code=400, detail="Cursor is invalid")
    
    where_clause = ("WHERE " + " AND".join(conditions)) if conditions else ""
    query = f"""
        SELECT * FROM events
        {where_clause}
        ORDER BY occurred_at DESC, id DESC
        LIMIT ?
        """
    params.append(limit + 1)
    
    with get_db() as conn:
        rows = conn.execute(query, params).fetchall()
    
    has_more = len(rows) > limit
    rows = rows[:limit]
    
    next_cursor = None
    if has_more and rows:
        last = rows[-1]
        raw = f"{last['occurred_at']},{last['id']}"
        next_cursor = base64.b64encode(raw.encode()).decode()
    
    return {
        "data": [dict(row) for row in rows],
        "next_cursor": next_cursor,
        "has_more": has_more
    }


@router.get("/events/{event_id}")
def get_event(event_id: int):
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM events WHERE id = ?", (event_id)
        ).fetchone()
    
    if not row:
        raise HTTPException(
            status_code=404,
            detail={"error": "Event not found", "code": "event_not_found"}
        )
    
    event_dict = dict(row)
    event_dict["tags"] = json.loads(event_dict["tags"])
    event_dict["payload"] = json.loads(event_dict["payload"]) if event_dict["payload"] else None
    event_dict["created_at"] = event_dict["occured_at"]
    return event_dict


@router.patch("/events/{event_id}")
def update_event(event_id: int, updates: dict):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
    
    if not row:
        raise HTTPException(
            status_code=404,
            detail={"error": "Event not found", "code": "event_not_found"}
        )
    
    return {
        "status": "not updated",
        "reason": "not implemented yet."
    }


@router.delete("/events/{event_id}")
def delete_event(event_id: int):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
    
    if not row:
        raise HTTPException(
            status_code=404,
            detail={"error": "Event not found", "code": "event_not_found"}
        )
    
    conn.execute("DELETE FROM events WHERE id = ?", (event_id,))
    conn.commit()
    return {"status": "deleted"}

