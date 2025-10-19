from django.db import connection
from django.db.models import Avg, Count, Prefetch, Q
from django.http import JsonResponse
from .models import Department, Employee, DepartmentEmployee

# --- serializers -----------------------------------------------------------------
def _serialize_orm_row(item):
    """Serializa instância, dict ou tuple retornado pelo ORM."""
    if item is None:
        return None
    # dict (values())
    if isinstance(item, dict):
        return item
    # model instance (DepartmentEmployee)
    if hasattr(item, "department") and hasattr(item, "employee"):
        return {
            "dept_name": getattr(item.department, "dept_name", None),
            "employee_id": getattr(item.employee, "id", None),
            "first_name": getattr(item.employee, "first_name", None),
            "last_name": getattr(item.employee, "last_name", None),
        }
    # tuple/list (values_list)
    if isinstance(item, (list, tuple)):
        if len(item) >= 4:
            return {"dept_name": item[0], "employee_id": item[1], "first_name": item[2], "last_name": item[3]}
        if len(item) == 3:
            return {"dept_name": item[0], "employee_id": item[1], "first_name": item[2]}
        if len(item) == 2:
            return {"dept_name": item[0], "first_name": item[1]}
    return {"row": str(item)}

def _serialize_sql_row(row):
    """Serializa tuple retornado por cursor.fetchall()."""
    if not row:
        return {}
    if len(row) >= 6:
        return {
            "dept_name": row[0].strip() if isinstance(row[0], str) else row[0],
            "employee_id": row[1],
            "first_name": row[2],
            "last_name": row[3],
            "gender": row[4],
            "salary": float(row[5]) if row[5] is not None else None,
        }
    if len(row) == 3:
        return {"dept_name": row[0].strip() if isinstance(row[0], str) else row[0], "employee_id": row[1], "first_name": row[2]}
    if len(row) == 2:
        return {"dept_name": row[0].strip() if isinstance(row[0], str) else row[0], "first_name": row[1]}
    return {"row": tuple(row)}

# --- helpers to materialize results ------------------------------------------------
def _materialize_orm(fn):
    """Executa QuerySet/generator do ORM e retorna lista serializável."""
    raw = list(fn())
    return [_serialize_orm_row(r) for r in raw]

def _materialize_sql(fn):
    """Executa função que faz fetchall() e retorna lista serializável."""
    rows = fn()
    if not isinstance(rows, list):
        rows = list(rows)
    return [_serialize_sql_row(r) for r in rows]

# --- ORM / raw SQL builders -------------------------------------------------------
def orm_simple():
    return Employee.objects.values("gender").annotate(count=Count("id")).order_by("gender")

def sql_simple():
    sql = """
    SELECT gender, COUNT(*)::bigint AS count
    FROM employee
    GROUP BY gender
    ORDER BY gender;
    """
    def fetch_all():
        with connection.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()
    return fetch_all

def orm_complex():
    return (
        Department.objects
        .filter(departmentemployee__employee__salaries__to_date="9999-01-01", departmentemployee__to_date="9999-01-01")
        .values("dept_name", "departmentemployee__employee__gender")
        .annotate(avg_salary=Avg("departmentemployee__employee__salaries__amount"))
        .order_by("dept_name", "departmentemployee__employee__gender")
    )

def sql_complex():
    sql = """
    SELECT d.dept_name, e.gender, ROUND(AVG(s.amount)::numeric,2) AS avg_salary
    FROM department d
    JOIN department_employee de ON de.department_id = d.id
    JOIN employee e ON e.id = de.employee_id
    JOIN salary s ON s.employee_id = e.id
    WHERE s.to_date = '9999-01-01' AND de.to_date = '9999-01-01'
    GROUP BY d.dept_name, e.gender
    ORDER BY d.dept_name, e.gender;
    """
    def fetch_all():
        with connection.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()
    return fetch_all

def orm_large():
    return DepartmentEmployee.objects.filter(
        to_date="9999-01-01", employee__salaries__to_date="9999-01-01"
    ).values(
        "department__dept_name",
        "employee__id",
        "employee__first_name",
        "employee__last_name",
        "employee__gender",
        "employee__salaries__amount",
    ).order_by("department__dept_name", "employee__id")

def sql_large():
    sql = """
    SELECT d.dept_name, e.id, e.first_name, e.last_name, e.gender, s.amount
    FROM department_employee de
    JOIN department d ON d.id = de.department_id
    JOIN employee e ON e.id = de.employee_id
    JOIN salary s ON s.employee_id = e.id AND s.to_date = '9999-01-01'
    WHERE de.to_date = '9999-01-01'
    ORDER BY d.dept_name, e.id;
    """
    def fetch_all():
        with connection.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()
    return fetch_all

# --- N+1 examples -----------------------------------------------------------------
def n_plus_one_bad():
    return DepartmentEmployee.objects.filter(to_date="9999-01-01").all()

def n_plus_one_fixed():
    return DepartmentEmployee.objects.filter(to_date="9999-01-01").select_related("department", "employee").all()

def sql_n_plus_one():
    sql = """
    SELECT d.dept_name, e.first_name
    FROM department d
    JOIN department_employee de ON de.department_id = d.id
    JOIN employee e ON e.id = de.employee_id
    WHERE de.to_date = '9999-01-01'
    ORDER BY d.id;
    """
    def fetch_all():
        with connection.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()
    return fetch_all

# --- endpoints: executam a query e retornam tudo (rows_count + rows) -----------------
def avg_simple_orm(request):
    rows = _materialize_orm(orm_simple)
    return JsonResponse({"rows_count": len(rows), "rows": rows}, safe=False)

def avg_simple_sql(request):
    rows = _materialize_sql(sql_simple())
    return JsonResponse({"rows_count": len(rows), "rows": rows}, safe=False)

def avg_complex_orm(request):
    rows = _materialize_orm(orm_complex)
    return JsonResponse({"rows_count": len(rows), "rows": rows}, safe=False)

def avg_complex_sql(request):
    rows = _materialize_sql(sql_complex())
    return JsonResponse({"rows_count": len(rows), "rows": rows}, safe=False)

def avg_large_orm(request):
    rows = _materialize_orm(orm_large)
    return JsonResponse({"rows_count": len(rows), "rows": rows}, safe=False)

def avg_large_sql(request):
    rows = _materialize_sql(sql_large())
    return JsonResponse({"rows_count": len(rows), "rows": rows}, safe=False)

def nplus1_orm_bad(request):
    rows = _materialize_orm(n_plus_one_bad)
    return JsonResponse({"rows_count": len(rows), "rows": rows}, safe=False)

def nplus1_orm_fixed(request):
    rows = _materialize_orm(n_plus_one_fixed)
    return JsonResponse({"rows_count": len(rows), "rows": rows}, safe=False)

def nplus1_sql_reference(request):
    rows = _materialize_sql(sql_n_plus_one())
    return JsonResponse({"rows_count": len(rows), "rows": rows}, safe=False)