from typing import Optional
from datetime import date as date_type
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from database import SessionLocal
from models import Attendance, Employee
from schemas import AttendanceCreate

router = APIRouter(prefix="/attendance", tags=["Attendance"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def mark_attendance(data: AttendanceCreate, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.id == data.employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    record = Attendance(**data.dict())
    db.add(record)
    db.commit()
    return {"message": "Attendance marked"}


@router.get("/")
def list_attendance(date: Optional[date_type] = None, employee_id: Optional[int] = None, db: Session = Depends(get_db)):
    q = db.query(Attendance)
    if date:
        q = q.filter(Attendance.date == date)
    if employee_id:
        q = q.filter(Attendance.employee_id == employee_id)

    records = q.all()
    result = []
    for r in records:
        emp = db.query(Employee).filter(Employee.id == r.employee_id).first()
        result.append({
            "id": r.id,
            "employee_id": r.employee_id,
            "date": r.date.isoformat(),
            "status": r.status,
            "employee": {
                "id": emp.id,
                "employee_id": emp.employee_id,
                "full_name": emp.full_name,
                "email": emp.email,
                "department": emp.department,
            } if emp else None,
        })
    return result


@router.get("/summary")
def attendance_summary(start_date: Optional[date_type] = None, end_date: Optional[date_type] = None, db: Session = Depends(get_db)):
    # Base filters
    q = db.query(Attendance)
    if start_date:
        q = q.filter(Attendance.date >= start_date)
    if end_date:
        q = q.filter(Attendance.date <= end_date)

    total_records = q.count()
    total_present = q.filter(Attendance.status == "Present").count()
    total_absent = q.filter(Attendance.status == "Absent").count()

    total_employees = db.query(Employee).count()

    per_emp_q = (
        db.query(
            Employee.id,
            Employee.employee_id,
            Employee.full_name,
            Employee.email,
            Employee.department,
            func.coalesce(func.sum(case((Attendance.status == 'Present', 1), else_=0)), 0).label('present_count'),
            func.coalesce(func.sum(case((Attendance.status == 'Absent', 1), else_=0)), 0).label('absent_count'),
            func.count(Attendance.id).label('total'),
        )
        .outerjoin(Attendance, Attendance.employee_id == Employee.id)
    )

    if start_date:
        per_emp_q = per_emp_q.filter(Attendance.date >= start_date)
    if end_date:
        per_emp_q = per_emp_q.filter(Attendance.date <= end_date)

    per_emp = per_emp_q.group_by(Employee.id).all()

    per_emp_list = []
    for row in per_emp:
        per_emp_list.append({
            "id": row.id,
            "employee_id": row.employee_id,
            "full_name": row.full_name,
            "email": row.email,
            "department": row.department,
            "present_count": int(row.present_count or 0),
            "absent_count": int(row.absent_count or 0),
            "total": int(row.total or 0),
        })

    return {
        "total_employees": total_employees,
        "total_records": total_records,
        "total_present": total_present,
        "total_absent": total_absent,
        "per_employee": per_emp_list,
    }
