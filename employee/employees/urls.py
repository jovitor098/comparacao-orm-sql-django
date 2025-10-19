from django.urls import path
from . import views

urlpatterns = [
    # avg / comparison endpoints (separados, sem "compare" agregador)
    path("avg/simple/orm/", views.avg_simple_orm, name="avg_simple_orm"),
    path("avg/simple/sql/", views.avg_simple_sql, name="avg_simple_sql"),

    path("avg/complex/orm/", views.avg_complex_orm, name="avg_complex_orm"),
    path("avg/complex/sql/", views.avg_complex_sql, name="avg_complex_sql"),

    path("avg/large/orm/", views.avg_large_orm, name="avg_large_orm"),
    path("avg/large/sql/", views.avg_large_sql, name="avg_large_sql"),

    # N+1 endpoints já separados
    path("nplus1/orm/bad/", views.nplus1_orm_bad, name="nplus1_orm_bad"),
    path("nplus1/orm/fixed/", views.nplus1_orm_fixed, name="nplus1_orm_fixed"),
    path("nplus1/sql/reference/", views.nplus1_sql_reference, name="nplus1_sql_reference"),
]