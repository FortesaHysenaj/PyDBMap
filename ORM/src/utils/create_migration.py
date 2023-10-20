import psycopg2
import os
import inspect
import datetime
from src.utils.db import db_settings
from src.utils.generate_sql import generate_create_table_sql


def get_model_classes(models_folder="Models"):
    model_files = [f for f in os.listdir(models_folder) if f.endswith(".py")]

    classes = []
    for model_file in model_files:
        module_name = os.path.splitext(model_file)[0]
        module = __import__(f"{models_folder}.{module_name}", fromlist=["*"])
        model_class = getattr(module, module_name, None)
        if inspect.isclass(model_class):
            classes.append(model_class)

    return classes


def generate_sql_queries(classes):
    return "".join(generate_create_table_sql(model_class) for model_class in classes)


def write_migration_file(sql_queries, description):
    version = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    migration_file = f"Migrations/migration_{version}_{description}.py"
    with open(migration_file, "w") as f:
        f.write(
            f"""
import psycopg2
from src.utils.db import db_settings

class Migration:
    def apply(self):
        with psycopg2.connect(**db_settings) as connection, connection.cursor() as cursor:
            cursor.execute('''
            {sql_queries}
            ''')
"""
        )


def insert_migration_history(migration_name):
    date_now = datetime.datetime.now()
    query = f"""
        INSERT INTO migration_history 
        (name, is_applied, date_created, date_updated) 
        VALUES 
        ('{migration_name}','0','{date_now}','{date_now}')
    """

    with psycopg2.connect(**db_settings) as connection, connection.cursor() as cursor:
        cursor.execute(query)


def create_migration_file(description):
    classes = get_model_classes()
    sql_queries = generate_sql_queries(classes)
    write_migration_file(sql_queries, description)
    version = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    migration_name = f"migration_{version}_{description}.py"
    insert_migration_history(migration_name)
