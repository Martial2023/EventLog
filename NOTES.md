## Notes

### Key Decisions
### 1. Timestamp storage

**Decision**: store timestampss as-is, not normalized in DB

**Why**: The spec says "timestamps must be preserveed exactly as submitted


###2.


### If More time

1. Add validation for payload size(4KB limit)
2. Extract tag tag validation into reusable function (currently duplicated)
3. Better test coverage
4. Add database indexes for common queries