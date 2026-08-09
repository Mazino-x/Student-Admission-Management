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

router.get("", response_model=list[StudentResponse], status_code=status.HTTP_200_OK, summary="Fetch all Students",)
def list_students(
    year: int | None = Query(None, ge=1, le=4, description="Filter by academic year"),
    department: str | None = Query(None, description="Filter by department / course"),
    course: str | None = Query(None, description="Filter by course / department"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Max number of records to return"),
    db: Session = Depends(get_db),
):
    query = db.query(Student)
    if year is not None:
        query = query.filter(Student.year == year)

    dept_filter = department or course
    if dept_filter is not None:
        query = query.filter(
            (func.lower(Student.department) == func.lower(dept_filter.strip()))
            | (func.lower(Student.course) == func.lower(dept_filter.strip()))
        )

    students = query.offset(skip).limit(limit).all()
    return students

router.get("/statistics", response_model=StudentStatistics, status_code=status.HTTP_200_OK, summary="Fetch Student Statistics",)
def get_student_statistics(db: Session = Depends(get_db)):
    total = db.query(Student).count()

    year_counts = {"1": 0, "2": 0, "3": 0, "4": 0}
    year_results = (
        db.query(Student.year, func.count(Student.id)).group_by(Student.year).all()
    )
    for y, count in year_results:
        if str(y) in year_counts:
            year_counts[str(y)] = count

    dept_results = (
        db.query(Student.department, func.count(Student.id))
        .group_by(Student.department)
        .all()
    )
    dept_counts = {dept: count for dept, count in dept_results}

    return StudentStatistics(
        total_students=total,
        by_year=year_counts,
        year_distribution=year_counts,
        by_department=dept_counts,
    )

router.get("/{student_id}", response_model=StudentResponse, status_code=status.HTTP_200_OK, summary="Fetch Student by ID",)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )
    return student 

router.put("/{student_id}", response_model=StudentResponse, status_code=status.HTTP_200_OK, summary="Update Student by ID",)
def update_student(
    student_id: int,
    student_in: StudentUpdate,
    db: Session = Depends(get_db),
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    update_data = student_in.model_dump(exclude_unset=True)

    if "email" in update_data and update_data["email"] is not None:
        new_email = update_data["email"].lower().strip()
        existing = (
            db.query(Student)
            .filter(
                func.lower(Student.email) == new_email,
                Student.id != student_id,
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists",
            )
        update_data["email"] = new_email

    if "name" in update_data and update_data["name"] is not None:
        update_data["name"] = update_data["name"].strip()
    if "phone" in update_data and update_data["phone"] is not None:
        update_data["phone"] = update_data["phone"].strip()

    dept_val = update_data.get("department") or update_data.get("course")
    if dept_val is not None:
        update_data["department"] = dept_val.strip()
        update_data["course"] = dept_val.strip()

    for key, value in update_data.items():
        setattr(student, key, value)

    db.commit()
    db.refresh(student)
    return student

router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Student by ID",)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    db.delete(student)
    db.commit()
    return {"message": "Student deleted successfully"}