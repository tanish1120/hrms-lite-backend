from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import date

class EmployeeCreate(BaseModel):
    employee_id: Optional[str] = None
    full_name: str
    email: EmailStr
    department: str


class AttendanceCreate(BaseModel):
    employee_id: int
    date: date
    status: str
