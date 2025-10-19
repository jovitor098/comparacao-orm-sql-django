from django.db import connection
from django.db.models import Avg, Count, Prefetch, Q
from django.http import JsonResponse
from .models import Department, Employee, DepartmentEmployee
from .serializers import DepartmentEmployeeSerializer, EmployeeSerializer, DepartmentSerializer


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
    queryset = Employee.objects.values("gender").annotate(count=Count("id")).order_by("gender")
    return JsonResponse(list(queryset), safe=False)  # Serialização automática para dicts

def avg_simple_sql(request):
    sql = """
    SELECT gender, COUNT(*)::bigint AS count
    FROM employee
    GROUP BY gender
    ORDER BY gender;
    """
    with connection.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    return JsonResponse([{"gender": row[0], "count": row[1]} for row in rows], safe=False)

def avg_complex_orm(request):
    queryset = (
        Department.objects
        .filter(departmentemployee__employee__salaries__to_date="9999-01-01", departmentemployee__to_date="9999-01-01")
        .values("dept_name", "departmentemployee__employee__gender")
        .annotate(avg_salary=Avg("departmentemployee__employee__salaries__amount"))
        .order_by("dept_name", "departmentemployee__employee__gender")
    )
    return JsonResponse(list(queryset), safe=False)  # Serialização automática para dicts

def avg_complex_sql(request):
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
    with connection.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    return JsonResponse([{"dept_name": row[0], "gender": row[1], "avg_salary": row[2]} for row in rows], safe=False)

def avg_large_orm(request):
    queryset = DepartmentEmployee.objects.filter(
        to_date="9999-01-01", employee__salaries__to_date="9999-01-01"
    ).select_related("department", "employee")
    serializer = DepartmentEmployeeSerializer(queryset, many=True)
    return JsonResponse(serializer.data, safe=False)

def avg_large_sql(request):
    sql = """
    SELECT d.dept_name, e.id, e.first_name, e.last_name, e.gender, s.amount
    FROM department_employee de
    JOIN department d ON d.id = de.department_id
    JOIN employee e ON e.id = de.employee_id
    JOIN salary s ON s.employee_id = e.id AND s.to_date = '9999-01-01'
    WHERE de.to_date = '9999-01-01'
    ORDER BY d.dept_name, e.id;
    """
    with connection.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    return JsonResponse([
        {
            "dept_name": row[0],
            "employee_id": row[1],
            "first_name": row[2],
            "last_name": row[3],
            "gender": row[4],
            "salary": row[5],
        }
        for row in rows
    ], safe=False)

def nplus1_orm_bad(request):
    """
    N+1 Problem: ORM sem otimização.
    Retorna todos os registros de DepartmentEmployee com department e employee.
    """
    queryset = DepartmentEmployee.objects.filter(to_date="9999-01-01")
    serializer = DepartmentEmployeeSerializer(queryset, many=True)
    return JsonResponse(serializer.data, safe=False)

def nplus1_orm_fixed(request):
    """
    N+1 Problem: ORM otimizado com select_related.
    Retorna todos os registros de DepartmentEmployee com department e employee.
    """
    queryset = DepartmentEmployee.objects.filter(to_date="9999-01-01").select_related("department", "employee")
    serializer = DepartmentEmployeeSerializer(queryset, many=True)
    return JsonResponse(serializer.data, safe=False)

def nplus1_sql_reference(request):
    """
    N+1 Problem: SQL direto.
    Retorna todos os registros de DepartmentEmployee com department e employee.
    """
    sql = """
    SELECT d.dept_name, e.id, e.first_name, e.last_name, de.from_date, de.to_date
    FROM department_employee de
    JOIN department d ON d.id = de.department_id
    JOIN employee e ON e.id = de.employee_id
    WHERE de.to_date = '9999-01-01'
    ORDER BY d.dept_name, e.id;
    """
    with connection.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()

    # Serializa manualmente os resultados do SQL
    data = [
        {
            "department": {"dept_name": row[0]},
            "employee": {"id": row[1], "first_name": row[2], "last_name": row[3]},
            "from_date": row[4],
            "to_date": row[5],
        }
        for row in rows
    ]
    return JsonResponse(data, safe=False)