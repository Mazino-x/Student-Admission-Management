from fastapi import FastAPI
from app.database import Base, engine
from app.routes.students import router as students_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Student Admission Management API",
    description="REST API for managing student admissions.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(students_router)


@app.get("/", tags=["Health Check"])
def root():
    return {
        "status": "ok",
        "message": "Student Admission Management API is running successfully",
        "docs": "/docs",
    }