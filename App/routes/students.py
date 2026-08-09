from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Student
from app.schemas import (
    StudentCreate,
    StudentResponse,
    StudentStatistics,
    StudentUpdate,
)

router = APIRouter(prefix="/students", tags=["Students"])
router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED, summary="Student Registration",)
def create_student(student_in: StudentCreate, db: Session = Depends(get_db)):
    # Case-insensitive email uniqueness check
    existing_student = (
        db.query(Student)
        .filter(func.lower(Student.email) == func.lower(student_in.email))
        .first()
    )
    if existing_student:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists",
        )

    dept = (student_in.department or student_in.course or "Computer Science").strip()

    db_student = Student(
        name=student_in.name.strip(),
        email=student_in.email.lower().strip(),
        phone=student_in.phone.strip(),
        department=dept,
        course=dept,
        year=student_in.year,
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

