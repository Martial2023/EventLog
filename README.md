# EventLog API

EventLog is a simple Restful API for storing and querying timeseries events. 

# Intallation
### Requiments
- Python 3.11+
- pip

### Setup
1. Clone the repository
2. Creat a virtual environment (optional but recommended)
```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install the dependencies
```bash
pip install -r requirements.txt
```

4. Configuration of the database path in the `.env` file
DATABASE_PATH="./events.db


# Usage
uvicorn app.main:app --reload

Endpoints (CRUD)
 - POST / events: create a new event
 - GET / events: retrieve events with optional filters
 - GET /events/{id}: retrieve a specific event by ID
 - PATCH /events/{id}: update an existing event
 - DELETE /events/{id}: delete an event


Stats
- GET /stats: retrieve aggregated statistics

Debug
- POST /debug/echo: echo back the received payload



Swagger documentation
Go to /docs


