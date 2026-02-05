from typing import Optional
from datetime import date as date_type
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import SessionLocal
from models import Employee, Attendance
from schemas import EmployeeCreate
from uuid import uuid4

router = APIRouter(prefix="/employees", tags=["Employees"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _generate_employee_id(db: Session):
    # Generate a short unique employee id like EMPXXXXXXXX
    while True:
        candidate = f"EMP{uuid4().hex[:8].upper()}"
        exists = db.query(Employee).filter(Employee.employee_id == candidate).first()
        if not exists:
            return candidate


@router.post("/")
def add_employee(emp: EmployeeCreate, db: Session = Depends(get_db)):
    emp_data = emp.dict()

    # Prevent duplicate emails
    existing_email = db.query(Employee).filter(Employee.email == emp_data.get("email")).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")

    # Auto-generate employee_id if not provided
    if not emp_data.get("employee_id"):
        emp_data["employee_id"] = _generate_employee_id(db)

    existing = db.query(Employee).filter(Employee.employee_id == emp_data["employee_id"]).first()
    if existing:
        raise HTTPException(status_code=400, detail="Employee ID already exists")

    new_emp = Employee(**emp_data)
    db.add(new_emp)
    try:
        db.commit()
        db.refresh(new_emp)
        return new_emp
    except IntegrityError:
        # Rollback and return a friendly error (covers rare race conditions)
        db.rollback()
        raise HTTPException(status_code=400, detail="Employee with given email or employee_id already exists")


@router.get("/")
def list_employees(db: Session = Depends(get_db)):
    return db.query(Employee).all()


@router.delete("/{id}")
def delete_employee(id: int, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.id == id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    db.delete(emp)
    db.commit()
    return {"message": "Employee deleted"}


@router.get("/{id}")
def get_employee(id: int, sort: Optional[str] = "desc", start_date: Optional[date_type] = None, end_date: Optional[date_type] = None, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.id == id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    q = db.query(Attendance).filter(Attendance.employee_id == id)
    if start_date:
        q = q.filter(Attendance.date >= start_date)
    if end_date:
        q = q.filter(Attendance.date <= end_date)

    if sort and sort.lower() == "asc":
        q = q.order_by(Attendance.date.asc())
    else:
        q = q.order_by(Attendance.date.desc())

    attendance = [
        {"id": a.id, "date": a.date.isoformat(), "status": a.status}
        for a in q.all()
    ]

    present_count = sum(1 for a in attendance if a["status"] == "Present")
    absent_count = sum(1 for a in attendance if a["status"] == "Absent")

    return {
        "id": emp.id,
        "employee_id": emp.employee_id,
        "full_name": emp.full_name,
        "email": emp.email,
        "department": emp.department,
        "attendance": attendance,
        "present_count": present_count,
        "absent_count": absent_count,
        "total": len(attendance),
    }
