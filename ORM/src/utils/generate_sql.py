import psycopg2
from src.utils.db import db_settings
from Modules.Column import Column


def get_column_definition(attr_name, attr):
    column_name = attr_name
    datatype = attr.datatype.__name__  # Convert to string
    primary_key = "PRIMARY KEY" if attr.primary_key else ""
    return f"{column_name} {datatype} {primary_key}"


def column_exists_in_db(table_name, column_name):
    with psycopg2.connect(**db_settings) as connection, connection.cursor() as cursor:
        table_name_lower = table_name.lower()
        cursor.execute(
            f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='{table_name_lower}' and column_name='{column_name}';
            """
        )
        return cursor.fetchone() is not None

def table_exists_in_db(table_name):
    with psycopg2.connect(**db_settings) as connection, connection.cursor() as cursor:
        table_name_lower = table_name.lower()
        cursor.execute(
            f"""
            SELECT 1
            FROM information_schema.tables
            WHERE table_name = '{table_name_lower}'
            """
        )
        return cursor.fetchone() is not None

def generate_alter_query(table_name, attr_name, attr):
    if table_exists_in_db(table_name) and not column_exists_in_db(table_name, attr_name):
        datatype = attr.datatype.__name__
        return f"""ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {attr_name} {datatype};"""
    return ""


def generate_create_table_sql(model_class):
    table_name = model_class.__tablename__
    columns_definitions = []
    alter_queries = []

    for attr_name, attr in model_class.__dict__.items():
        if isinstance(attr, Column):
            columns_definitions.append(get_column_definition(attr_name, attr))
            alter_queries.append(generate_alter_query(table_name, attr_name, attr))

    columns_sql = ", ".join(columns_definitions)
    alter_sql = "\n\t\t".join(alter_queries)

    create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name}\n\t\t\t({columns_sql});\n\t\t{alter_sql}"

    return create_table_sql
