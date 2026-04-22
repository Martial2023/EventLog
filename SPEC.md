# EventLog — Take-Home Project

**Time budget:** 3–4 hours. Submit whatever you have at that point, plus a short `NOTES.md` explaining decisions, trade-offs, and anything you'd do differently with more time.

**Stack:** Python 3.11+, Flask *or* FastAPI (your choice), SQLite. No ORM required, but you may use SQLAlchemy if you prefer. No authentication needed. No frontend.

**What we're looking for:** production-minded code. We care much more about correctness, clarity, and attention to the spec than about volume of code. Read the spec carefully — details matter.

---

## 1. Domain

EventLog stores time-series events submitted by users. Each event has:

| Field          | Type              | Notes                                                                 |
|----------------|-------------------|-----------------------------------------------------------------------|
| `id`           | int               | Auto-assigned.                                                        |
| `user_id`      | string            | Required. 1–64 chars, alphanumeric + underscore.                      |
| `occurred_at`  | string (datetime) | Required. When the event happened in the real world. See §3.          |
| `recorded_at`  | string (datetime) | Auto-assigned server-side at insert time, UTC.                        |
| `created_at`   | string (datetime) | **Alias of `occurred_at`** — kept for backwards compatibility. See §3. |
| `kind`         | string            | Required. One of: `click`, `view`, `purchase`, `signup`, `custom`.    |
| `tags`         | list of strings   | Optional. See §4 for validation rules.                                |
| `payload`      | object            | Optional. Arbitrary JSON object, max 4 KB serialized.                 |

## 2. Endpoints

- `POST   /events`              — create an event
- `GET    /events`              — list events (supports filtering, see §5)
- `GET    /events/<id>`         — retrieve one event
- `PATCH  /events/<id>`         — partial update (only `kind`, `tags`, `payload` are mutable)
- `DELETE /events/<id>`         — delete one event
- `GET    /stats`               — aggregate statistics (see §6)
- `POST   /debug/echo`          — debug helper (see §7)

All responses are JSON. Errors use `{"error": "<message>", "code": "<machine_code>"}` with appropriate HTTP status codes.

## 3. Timestamps

Timestamps are stored in UTC. The server normalizes all incoming timestamps to UTC before persistence.

Timestamps must be preserved exactly as submitted, including the original timezone offset, so that clients can display them in the user's local context.

Timestamps use ISO 8601. Examples of accepted input:

```
2026-04-21T14:30:00Z
2026-04-21T14:30:00.000+00:00Z
2026-04-21T10:30:00-04:00
```

`created_at` and `occurred_at` refer to the same moment: when the event happened in the real world (as reported by the client). This is distinct from `recorded_at`, which is when the server received the event. Clients may submit events hours or days after they occurred.

## 4. `tags` validation

- Must be a JSON array of strings.
- Each tag is 1–32 chars, lowercase, `[a-z0-9_-]` only.
- Empty arrays are rejected (omit the field instead).
- A bare string is **not** auto-coerced to a one-element array. `"tags": "foo"` is a 400 error.
- Duplicate tags within one event are rejected.
- Max 16 tags per event.

## 5. Listing & filtering (`GET /events`)

Query parameters:

- `user_id` — exact match
- `kind` — exact match, may be repeated (`?kind=click&kind=view`)
- `tag` — event must contain this tag; may be repeated (AND semantics)
- `from`, `to` — filter by `occurred_at`, inclusive on both ends, ISO 8601
- `limit` — default 50, max 500
- `cursor` — opaque pagination cursor returned by previous response

Response shape:

```json
{
  "event_count": 5,
  "events": [
    {"id": 101, "user_id": "alice", "kind": "click",  "occurred_at": "2026-04-21T14:30:00Z", "tags": ["checkout"]},
    {"id": 102, "user_id": "alice", "kind": "view",   "occurred_at": "2026-04-21T14:31:00Z", "tags": []},
    {"id": 103, "user_id": "bob",   "kind": "signup", "occurred_at": "2026-04-21T14:32:00Z", "tags": ["welcome"]},
    {"id": 104, "user_id": "alice", "kind": "click",  "occurred_at": "2026-04-21T14:35:00Z", "tags": ["checkout","promo"]}
  ],
  "next_cursor": "eyJpZCI6MTA0fQ=="
}
```

Events are returned ordered by `occurred_at` descending, then `id` descending.

## 6. `GET /stats`

Returns global aggregate stats over all events in the database (no filtering):

```json
{
  "total_events": 1234,
  "events_by_kind": {"click": 900, "view": 300, "purchase": 30, "signup": 4},
  "median_gap_seconds": 42.5,
  "unique_users": 57
}
```

`median_gap_seconds` is the median time gap, in seconds, between consecutive events when all events are ordered globally by `occurred_at`. If there are fewer than 2 events, return `null`.

## 7. `POST /debug/echo`

Accepts any JSON object as body. Returns a response where every **string value** in the body is reversed character-by-character — **except** any string whose key is literally `"preserve"`, which is returned unchanged.

String reversal applies recursively through nested objects and arrays. Non-string values (numbers, booleans, null, objects, arrays) pass through with their structure intact; only the strings inside them are reversed.

Examples:

```
Request:  {"name": "alice", "age": 30, "preserve": "keepme"}
Response: {"name": "ecila", "age": 30, "preserve": "keepme"}

Request:  {"items": ["foo", "bar"], "preserve": "ok"}
Response: {"items": ["oof", "rab"], "preserve": "ok"}

Request:  {"nested": {"x": "hello", "preserve": "hi"}}
Response: {"nested": {"x": "olleh", "preserve": "hi"}}
```

## 8. Integrity constraints

- Two events with the same `user_id` and identical `occurred_at` are rejected with HTTP 409 and `code: "duplicate_event"`. This rule must hold under concurrent requests.
- `PATCH` on a non-existent event returns 404.
- `DELETE` is idempotent (404 the first time a missing id is deleted, 404 every time after — do not silently succeed).

## 9. Deliverables

- Working code in a git repo (include `.git`).
- `README.md` with run instructions.
- `NOTES.md` with your reasoning on non-obvious decisions and any ambiguity you noticed in this spec.
- Tests for anything you consider important. We don't require 100% coverage.

Good luck.
