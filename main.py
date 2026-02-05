import os
from fastapi import FastAPI
from database import Base, engine
from routes import employee, attendance
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="HRMS Lite API")

# Read allowed origins from environment variable (comma separated). Use '*' for open.
_allowed = os.getenv("ALLOWED_ORIGINS", "*")
if _allowed.strip() == "*":
    allow_origins = ["*"]
else:
    allow_origins = [o.strip() for o in _allowed.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(employee.router)
app.include_router(attendance.router)


@app.get("/")
def home():
    return {"message": "HRMS Lite Backend Running"}
