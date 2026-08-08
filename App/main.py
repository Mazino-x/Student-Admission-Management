from fastapi import FastAPI

from app.database import engine, Base
from app.routes.students import router as students_router


app = FastAPI()