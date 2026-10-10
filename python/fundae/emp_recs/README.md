# Employee Records API

A FastAPI CRUD service that stores employee records in `employees.json` beside
`main.py`. The file is created on the first write and retained across server
restarts.

## Run

```bash
python -m pip install -r requirements.txt
uvicorn main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the interactive API documentation.

## Endpoints

- `GET /employees` lists all employees.
- `POST /employees` creates an employee and assigns its integer ID.
- `GET /employees/{employee_id}` retrieves one employee.
- `PUT /employees/{employee_id}` replaces an employee's details.
- `DELETE /employees/{employee_id}` deletes an employee.

Create and update requests use JSON with `name`, `email`, `department`, and
`position` fields. Missing employee IDs return `404`.