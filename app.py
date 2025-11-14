from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import csv
import os

app = FastAPI()

CSV_FILE = "employees.csv"

# Create CSV file with header if not exists
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode="w", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["id", "name", "role", "salary"])


class Employee(BaseModel):
    id: int
    name: str
    role: str
    salary: float


# Helper: Read all records
def read_employees():
    employees = []
    with open(CSV_FILE, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            employees.append(row)
    return employees


# Helper: Write all records
def write_employees(employees):
    with open(CSV_FILE, mode="w", newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["id", "name", "role", "salary"])
        writer.writeheader()
        writer.writerows(employees)


# ➕ Add Employee
@app.post("/employee")
def add_employee(emp: Employee):
    employees = read_employees()

    # Check duplicate ID
    for e in employees:
        if int(e["id"]) == emp.id:
            raise HTTPException(status_code=400, detail="Employee ID already exists")

    with open(CSV_FILE, mode="a", newline='') as file:
        writer = csv.writer(file)
        writer.writerow([emp.id, emp.name, emp.role, emp.salary])

    return {"message": "Employee added successfully", "employee": emp}


# 📄 List Employees
@app.get("/employee")
def list_employees():
    return read_employees()


# ✏️ Update Employee
@app.put("/employee/{emp_id}")
def update_employee(emp_id: int, updated: Employee):
    employees = read_employees()
    found = False

    for emp in employees:
        if int(emp["id"]) == emp_id:
            emp["name"] = updated.name
            emp["role"] = updated.role
            emp["salary"] = str(updated.salary)
            found = True
            break

    if not found:
        raise HTTPException(status_code=404, detail="Employee not found")

    write_employees(employees)

    return {"message": "Employee updated successfully"}


# ❌ Delete Employee
@app.delete("/employee/{emp_id}")
def delete_employee(emp_id: int):
    employees = read_employees()
    new_employees = [emp for emp in employees if int(emp["id"]) != emp_id]

    if len(new_employees) == len(employees):
        raise HTTPException(status_code=404, detail="Employee not found")

    write_employees(new_employees)

    return {"message": "Employee deleted successfully"}
