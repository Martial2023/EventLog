from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.database import init_db
from app.routes import events, stats, debug
import uvicorn


app = FastAPI(title="EventLog")

init_db()

@app.exception_handler(RequestValidationError)
async def validation_exception(request, exc):
    return JSONResponse(
        status_code=400,
        content={
            "error": str(exc),
            "code": "validationn errror"
        }
    )
    
app.include_router(events.router)
app.include_router(stats.router)
app.include_router(debug.router)
