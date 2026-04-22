## Notes

### Key Decisions
### 1. Timestamp storage

**Decision**: store timestampss as-is, not normalized in DB

**Why**: The spec says "timestamps must be preserveed exactly as submitted


### 2. Deduplication with UNIQUE constraint
**Decision: Use `UNIQUE(user_id, occured_at)` at database level

**Why**: The spec requires this to work "under concurrent requests". A DB constraint is thread-safe by default-no manual lockin needed.

### 3. Cursor-Based Paggination
**Decision**: Opaque cursor encoded as base64, storing "{occurred_at}, {id}"
**Why**: Simple, stateless, and works with ordering. Avoids storing server-side cursor state.

### 4. Tags: Strict Validation
**Decision**: Reject non-array tags with 400 error. No auto-coercion.
**Why**: "A bare string is **not** auto-coerced to a one-element array". `"tags": "foo"` is a 400 errore"

### 5. `created_at`as Alias
**Decision**: Return `created_at` in response = `occured_at`

Because the spec says it's an "allias for backwards compatibility."

## Ambiuities in Spec
1. **Response format for `/events/{id}` and `PATCH /events/{id}`:**
    - Spec doesn't specify. Assuming full object like `/event` list.

2. **Empty tags in response:**
    - Spec shows `"tags": []` but says "empty array are rejected."
    - Decision: Return `[]` when no tags (not NULL
    
    )
3. **`recorded_at` in response:**
    - Spec does't say if it's included in GET responses
    - Decision: Include id (useful for clients)
4. **Cursor expiration**
    - No mention
    - Decision: Stateless, no expiration.

## If More time

1. Add validation for payload size(4KB limit)
2. Implement update_event function for PATCH endpoint
3. Extract tag tag validation into reusable function (currently duplicated)
4. Better test coverage
5. Add database indexes for common queries
6. Implement other robust error handling
7. Add logging and monitoring
8. Deploy it to a VPS or cloud platform