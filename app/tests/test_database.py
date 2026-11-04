import os

import pytest
from django.db import connection


@pytest.mark.django_db
def test_postgresql_uses_test_database():
    assert connection.vendor == "postgresql"

    with connection.cursor() as cursor:
        cursor.execute("SELECT current_database()")
        database_name = cursor.fetchone()[0]

    assert database_name == f"test_{os.environ['POSTGRES_DB']}"
