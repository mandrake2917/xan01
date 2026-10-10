import json
import os
import tempfile
from pathlib import Path
from threading import RLock

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict, Field


DATA_FILE = Path(__file__).with_name("employees.json")
_data_lock = RLock()


class EmployeeInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1)
    email: str = Field(min_length=1)
    department: str = Field(min_length=1)
    position: str = Field(min_length=1)


class Employee(EmployeeInput):
    id: int


app = FastAPI(title="Employee Records API", version="1.0.0")


def _read_employees() -> list[Employee]:
    if not DATA_FILE.exists():
        return []

    with DATA_FILE.open("r", encoding="utf-8") as data_file:
        records = json.load(data_file)
    return [Employee.model_validate(record) for record in records]


def _write_employees(employees: list[Employee]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=DATA_FILE.parent,
            prefix=f"{DATA_FILE.name}.",
            suffix=".tmp",
            delete=False,
        ) as data_file:
            temporary_path = Path(data_file.name)
            json.dump(
                [employee.model_dump() for employee in employees],
                data_file,
                indent=2,
            )
            data_file.write("\n")
        os.replace(temporary_path, DATA_FILE)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


@app.get("/employees", response_model=list[Employee])
def list_employees() -> list[Employee]:
    with _data_lock:
        return _read_employees()


@app.post(
    "/employees",
    response_model=Employee,
    status_code=status.HTTP_201_CREATED,
)
def create_employee(employee_input: EmployeeInput) -> Employee:
    with _data_lock:
        employees = _read_employees()
        employee_id = max((employee.id for employee in employees), default=0) + 1
        employee = Employee(id=employee_id, **employee_input.model_dump())
        employees.append(employee)
        _write_employees(employees)
        return employee


@app.get("/employees/{employee_id}", response_model=Employee)
def get_employee(employee_id: int) -> Employee:
    with _data_lock:
        employee = next(
            (item for item in _read_employees() if item.id == employee_id), None
        )
    if employee is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return employee


@app.put("/employees/{employee_id}", response_model=Employee)
def update_employee(employee_id: int, employee_input: EmployeeInput) -> Employee:
    with _data_lock:
        employees = _read_employees()
        for index, employee in enumerate(employees):
            if employee.id == employee_id:
                updated_employee = Employee(
                    id=employee_id, **employee_input.model_dump()
                )
                employees[index] = updated_employee
                _write_employees(employees)
                return updated_employee
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")


@app.delete(
    "/employees/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_employee(employee_id: int) -> Response:
    with _data_lock:
        employees = _read_employees()
        remaining_employees = [
            employee for employee in employees if employee.id != employee_id
        ]
        if len(remaining_employees) == len(employees):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found"
            )
        _write_employees(remaining_employees)
    return Response(status_code=status.HTTP_204_NO_CONTENT)