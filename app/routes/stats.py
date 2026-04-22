from fastapi import APIRouter
from datetime import datetime
from app.database import get_db
from statistics import median

router = APIRouter()

def compute_median_gap(times):
    if len(times) < 2:
        return None
    
    datetimes = []
    for time_str in times:
        dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
        datetimes.append(dt)
    gaps = []
    for i in range(1, len(datetimes)):
        gap_seconds = (datetimes[i] - datetimes[i-1]).total_seconds()
        gaps.append(gap_seconds)
    
    return median(gaps) if gaps else None
        

@router.get("/stats")
def get_stats():
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as cnt FROM events")
        total = cursor.fetchone()["cnt"]
        
        cursor.execute("""
                       SELECT kind, COUNT(*) as cnt FROM events GROUP BY kind
                       """)
        by_kind = {row["kind"]: row["cnt"] for row in cursor.fetchall()}
        cursor.execute("SELECT COUNT(DISTINCT user_id) as cnt FROM events")
        unique = cursor.fetchone()["cnt"]
        cursor.execute("""
                       SELECT occurred_at FROM events ORDER BY occurred_at ASC
                       """)
        times = [row["occurred_at"] for row in cursor.fetchall()]
        median_gap = compute_median_gap(times)
        return {
            "total_events": total,
            "events_by_kind": by_kind,
            "unique_users": unique,
            "median_time_gap_seconds": median_gap
        }