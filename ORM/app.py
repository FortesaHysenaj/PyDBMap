import psycopg2
from itertools import zip_longest
import click
import pyfiglet
from src.utils.db import db_settings
from src.utils.create_migration import create_migration_file
from src.utils.apply_migrations import apply_migration


# Migration class
class Migration:
    def __init__(self, version, description):
        self.version = version
        self.description = description

    def apply(self):
        pass  # Implement the actual schema changes here


# Click command for migrations
# Modify the Click command for migrations
@click.command()
@click.option("--migrations", is_flag=True, type=str)
@click.option("--add", type=str, is_flag=True, required=False)
@click.option("--apply", type=str, is_flag=True, required=False)
@click.argument("description", type=str, required=False)
def migrations(migrations, add, apply, description):
    click.echo(
        "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -"
    )
    font = pyfiglet.Figlet(font="slant")
    pydbmap_text = font.renderText("PyDBmap")
    click.echo(pydbmap_text)

    click.echo(
        "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -"
    )

    if migrations:
        if add:
            if not description:
                click.echo("Please provide a description for the migration.")
            else:
                create_migration_file(description)
                click.echo(f"Migration '{description}' added.")
        elif apply:
            try:
                apply_migration()
                click.echo("Migrations done!")
            except:
                click.echo("Migrations couldn't apply successfully.")
        else:
            click.echo("Invalid command")
    else:
        click.echo("Invalid command")

    click.echo(
        "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -"
    )


if __name__ == "__main__":
    migrations()


# ------------ Manager (Model objects handler) ------------ #
class BaseManager:
    connection = None

    @classmethod
    def set_connection(cls, database_settings):
        connection = psycopg2.connect(**database_settings)
        connection.autocommit = (
            True  # https://www.psycopg.org/docs/connection.html#connection.commit
        )
        cls.connection = connection

    @classmethod
    def _get_cursor(cls):
        return cls.connection.cursor()

    @classmethod
    def _execute_query(cls, query, params=None):
        cursor = cls._get_cursor()
        cursor.execute(query, params)

    def __init__(self, model_class):
        self.model_class = model_class

    def select(
        self,
        *field_names,
        group_by=None,
        order_by=None,
        order_direction="ASC",
        chunk_size=2000,
    ):
        # Build SELECT query
        fields_format = ", ".join(field_names)
        query = f"SELECT {fields_format} FROM {self.model_class.table_name}"

        # Add GROUP BY clause if specified
        if group_by:
            group_by_columns = ", ".join(group_by)
            query += f" GROUP BY {group_by_columns}"

        # Add ORDER BY clause if specified
        if order_by:
            order_direction = order_direction.upper()
            order_by_columns = ", ".join(order_by)
            query += f" ORDER BY {order_by_columns} {order_direction}"

        # Execute query
        cursor = self._get_cursor()
        cursor.execute(query)
        # Fetch data obtained with the previous query execution
        # and transform it into `model_class` objects.
        # The fetching is done by batches of `chunk_size` to
        # avoid to run out of memory.
        model_objects = list()
        is_fetching_completed = False
        while not is_fetching_completed:
            result = cursor.fetchmany(size=chunk_size)
            for row_values in result:
                keys, values = field_names, row_values
                row_data = dict(zip(keys, values))
                model_objects.append(self.model_class(**row_data))
            is_fetching_completed = len(result) < chunk_size

        return model_objects

    def bulk_insert(self, rows: list):
        # Build INSERT query and params:
        field_names = rows[0].keys()
        assert all(
            row.keys() == field_names for row in rows[1:]
        )  # confirm that all rows have the same fields

        fields_format = ", ".join(field_names)
        values_placeholder_format = ", ".join(
            [f'({", ".join(["%s"] * len(field_names))})'] * len(rows)
        )  # https://www.psycopg.org/docs/usage.html#passing-parameters-to-sql-queries

        query = (
            f"INSERT INTO {self.model_class.table_name} ({fields_format}) "
            f"VALUES {values_placeholder_format}"
        )

        params = list()
        for row in rows:
            row_values = [row[field_name] for field_name in field_names]
            params += row_values

        # Execute query
        self._execute_query(query, params)

    def update(self, new_data: dict):
        # Build UPDATE query and params
        field_names = new_data.keys()
        placeholder_format = ", ".join(
            [f"{field_name} = %s" for field_name in field_names]
        )
        query = f"UPDATE {self.model_class.table_name} SET {placeholder_format}"
        params = list(new_data.values())

        # Execute query
        self._execute_query(query, params)

    def delete(self):
        # Build DELETE query
        query = f"DELETE FROM {self.model_class.table_name} "

        # Execute query
        self._execute_query(query)

    def join(
        self,
        *tables,
        on_conditions=None,
        where_conditions=None,
        select_fields=None,
        chunk_size=2000,
    ):
        # Build JOIN query
        select_fields_format = ", ".join(select_fields) if select_fields else "*"
        tables_format = ", ".join(tables)
        on_conditions_format = " AND ".join(on_conditions) if on_conditions else ""
        where_conditions_format = (
            " AND ".join(where_conditions) if where_conditions else ""
        )

        query = f"SELECT {select_fields_format} FROM {tables_format.split(',')[0]}"

        tables_list = tables_format.split(",")[1:]
        conditions_list = on_conditions_format.split(",")

        for table, condition in zip_longest(tables_list, conditions_list):
            if on_conditions_format:
                query += f" JOIN {table} ON {condition}"
            if where_conditions_format:
                query += f" WHERE {where_conditions_format}"

        # Execute query
        cursor = self._get_cursor()
        cursor.execute(query)

        # Fetch data obtained with the query execution
        # and transform it into dictionaries.
        model_objects = list()
        is_fetching_completed = False
        while not is_fetching_completed:
            result = cursor.fetchmany(size=chunk_size)
            for row_values in result:
                keys, values = select_fields_format, row_values
                row_data = dict(zip(keys, values))
                model_objects.append(self.model_class(**row_data))
            is_fetching_completed = len(result) < chunk_size

        return model_objects

    def aggregate_sum(self, field_name):
        # Build SUM query
        query = f"SELECT SUM({field_name}) FROM {self.model_class.table_name}"

        # Execute query
        cursor = self._get_cursor()
        cursor.execute(query)

        # Fetch the result
        result = cursor.fetchone()
        return result[0] if result else None

    def aggregate_avg(self, field_name):
        # Build AVG query
        query = f"SELECT AVG({field_name}) FROM {self.model_class.table_name}"

        # Execute query
        cursor = self._get_cursor()
        cursor.execute(query)

        # Fetch the result
        result = cursor.fetchone()
        return result[0] if result else None

    def aggregate_count(self):
        # Build COUNT query
        query = f"SELECT COUNT(*) FROM {self.model_class.table_name}"

        # Execute query
        cursor = self._get_cursor()
        cursor.execute(query)

        # Fetch the result
        result = cursor.fetchone()
        return result[0] if result else 0

    def aggregate_min(self, field_name):
        # Build MIN query
        query = f"SELECT MIN({field_name}) FROM {self.model_class.table_name}"

        # Execute query
        cursor = self._get_cursor()
        cursor.execute(query)

        # Fetch the result
        result = cursor.fetchone()
        return result[0] if result else None

    def aggregate_max(self, field_name):
        # Build MAX query
        query = f"SELECT MAX({field_name}) FROM {self.model_class.table_name}"

        # Execute query
        cursor = self._get_cursor()
        cursor.execute(query)

        # Fetch the result
        result = cursor.fetchone()
        return result[0] if result else None


# ----------------------- Model ----------------------- #
class MetaModel(type):
    manager_class = BaseManager

    def _get_manager(cls):
        return cls.manager_class(model_class=cls)

    @property
    def objects(cls):
        return cls._get_manager()


class BaseModel(metaclass=MetaModel):
    table_name = ""

    def __init__(self, **row_data):
        for field_name, value in row_data.items():
            setattr(self, field_name, value)

    def __repr__(self):
        attrs_format = ", ".join(
            [f"{field}={value}" for field, value in self.__dict__.items()]
        )
        return f"<{self.__class__.__name__}: ({attrs_format})>\n"


class Migration:
    def __init__(self, version, description):
        self.version = version
        self.description = description

    def apply(self):
        pass  # Implement the actual schema changes here


# ----------------------- Setup ----------------------- #
# DB_SETTINGS = {
#     'host': '127.0.0.1',
#     'port': '5432',
#     'database': 'ormify',
#     'user': 'postgres',
#     'password': ''
# }

BaseManager.set_connection(database_settings=db_settings)


# ----------------------- Usage ----------------------- #
class Employee(BaseModel):
    manager_class = BaseManager
    table_name = "employees"


# class Department(BaseModel):
#     manager_class = BaseManager
#     table_name = "departments"


# SQL: SELECT first_name, last_name, salary, grade FROM employees;
# employees = Employee.objects.select('first_name', 'last_name', 'salary', 'grade')  # employees: List[Employee]

# print(f"First select result:\n {employees} \n")


# SQL: INSERT INTO employees (first_name, last_name, salary)
#  	VALUES ('Yan', 'KIKI', 10000), ('Yoweri', 'ALOH', 15000);

# employees_data = [
#     {"id": 1,"emp_name": "Yan", "manager": "KIKI"},
#     {"id": 2,"emp_name": "Yoweri", "manager": "ALOH"}
# ]
# Employee.objects.bulk_insert(rows=employees_data)

# employees = Employee.objects.select('first_name', 'last_name', 'salary', 'grade')
# print(f"Select result after bulk insert:\n {employees} \n")


# SQL: UPDATE employees SET salary = 17000, grade = 'L2';
# Employee.objects.update(
#     new_data={'salary': 17000, 'grade': 'L2'}
# )

# employees = Employee.objects.select('first_name', 'last_name', 'salary', 'grade')
# print(f"Select result after update:\n {employees} \n")


# SQL: DELETE FROM employees;
# Employee.objects.delete()

# employees = Employee.objects.select('first_name', 'last_name', 'salary', 'grade')
# print(f"Select result after delete:\n {employees} \n")

# SQL: JOIN Tables
# join_results = Employee.objects.join('employees', 'departments', 'managers', on_conditions=['employees.department_id = departments.id'],
#                          select_fields=['employees.first_name', 'employees.last_name', 'departments.dept_name', 'managers.name'], chunk_size=500)
# for row in join_results:
#     print(row)
