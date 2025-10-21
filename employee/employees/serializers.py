from rest_framework import serializers
from .models import Department, Employee, DepartmentEmployee, Title

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = "__all__"

class DepartmentEmployeeSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer()
    employee = EmployeeSerializer()

    class Meta:
        model = DepartmentEmployee
        fields = "__all__"

class TitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Title
        fields = "__all__"