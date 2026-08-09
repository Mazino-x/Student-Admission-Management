from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class StudentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Student full name")
    email: EmailStr = Field(..., description="Unique email address")
    phone: str = Field(..., pattern=r"^\d{10}$", description="10-digit phone number")
    department: str | None = Field(None, description="Academic department")
    course: str | None = Field(None, description="Academic course / department")
    year: int = Field(..., ge=1, le=4, description="Academic year (1 to 4)")

    @model_validator(mode="after")
    def populate_course_department(self):
        dept = self.department or self.course or "Computer Science"
        self.department = dept
        self.course = dept
        return self


class StudentUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(None, pattern=r"^\d{10}$")
    department: str | None = Field(None, min_length=1)
    course: str | None = Field(None, min_length=1)
    year: int | None = Field(None, ge=1, le=4)

    @model_validator(mode="after")
    def populate_course_department(self):
        if self.course and not self.department:
            self.department = self.course
        elif self.department and not self.course:
            self.course = self.department
        return self


class StudentResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str
    department: str = "Computer Science"
    course: str = "Computer Science"
    year: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class StudentStatistics(BaseModel):
    total_students: int
    by_year: dict[str, int]
    year_distribution: dict[str, int]
    by_department: dict[str, int]