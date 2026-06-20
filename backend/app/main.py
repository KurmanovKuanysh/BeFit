from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.mongo import init_db
from app.core.exceptions_handler import register_exception_handlers
from app.api.v1 import auth, workout, exercise, workout_plan, users, water, weight

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    print("Database connection established")
    yield
    print("Database connection closed")

app = FastAPI(
    title="BeFit API",
    description="BeFit API",
    version="0.1",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(workout.router, prefix="/api/v1")
app.include_router(exercise.router, prefix="/api/v1")
app.include_router(workout_plan.router, prefix="/api/v1")
app.include_router(weight.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(water.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"status": "ok"}
