from django.db import models

class Department(models.Model):
    id = models.CharField(primary_key=True, max_length=4)
    dept_name = models.CharField(max_length=40)

    class Meta:
        db_table = "department"
        managed = False

class Employee(models.Model):
    id = models.BigAutoField(primary_key=True)
    birth_date = models.DateField()
    first_name = models.CharField(max_length=14)
    last_name = models.CharField(max_length=16)
    gender = models.CharField(max_length=1)
    hire_date = models.DateField()

    class Meta:
        db_table = "employee"
        managed = False

class DepartmentEmployee(models.Model):
    # marcar employee como primary_key evita criação automática de "id" pelo Django
    employee = models.ForeignKey(
        Employee,
        db_column="employee_id",
        on_delete=models.DO_NOTHING,
        primary_key=True,
    )
    department = models.ForeignKey(Department, db_column="department_id", on_delete=models.DO_NOTHING)
    from_date = models.DateField()
    to_date = models.DateField()

    class Meta:
        db_table = "department_employee"
        managed = False
        unique_together = (("employee", "department"),)

class Salary(models.Model):
    employee = models.ForeignKey(
        Employee,
        db_column="employee_id",
        on_delete=models.DO_NOTHING,
        related_name="salaries"  # <- adicionado
    )
    amount = models.BigIntegerField()
    from_date = models.DateField()
    to_date = models.DateField()

    class Meta:
        db_table = "salary"
        managed = False
        unique_together = (("employee", "from_date"),)

class Title(models.Model):
    employee = models.ForeignKey(
        Employee,
        db_column="employee_id",
        on_delete=models.CASCADE,
        related_name="titles"
    )
    title = models.CharField(max_length=50)
    from_date = models.DateField()
    to_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "title"
        managed = False
        unique_together = (("employee", "title", "from_date"),)