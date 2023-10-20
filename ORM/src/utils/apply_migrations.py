import os
import importlib.util
import psycopg2
import datetime
from src.utils.db import db_settings
import click


def get_migration_files():
    """Retrieve sorted list of migration files."""
    return sorted(
        [
            f
            for f in os.listdir("Migrations")
            if f.startswith("migration_") and f.endswith(".py")
        ]
    )


def load_migration_module(migration_file):
    """Dynamically load the migration module."""
    module_name = f"Migrations.{migration_file[:-3]}"  # Remove '.py' extension
    spec = importlib.util.spec_from_file_location(
        module_name, os.path.join("Migrations", migration_file)
    )
    migration_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration_module)
    return migration_module


def is_migration_applied(cursor, migration_file):
    """Check if a migration has been applied."""
    select_query = (
        f"SELECT is_applied FROM migration_history WHERE name = '{migration_file}'"
    )
    cursor.execute(select_query)
    res = cursor.fetchone()
    return False if res and res[0] == 0 else True


def apply_migration():
    with psycopg2.connect(**db_settings) as connection, connection.cursor() as cursor:
        migration_files = get_migration_files()
        for migration_file in migration_files:
            try:
                migration_module = load_migration_module(migration_file)
                migration_class = getattr(migration_module, "Migration", None)

                if migration_class and not is_migration_applied(cursor, migration_file):
                    migration_instance = migration_class()
                    migration_instance.apply()
                    click.echo(f"Applied migration: {migration_file}\n")

                    date_updated = datetime.datetime.now()
                    query = f"UPDATE migration_history SET is_applied = '1', date_updated = '{date_updated}' WHERE name = '{migration_file}'"
                    cursor.execute(query)

                elif not migration_class:
                    click.echo(
                        f"Couldn't find the Migration class in {migration_file}\n"
                    )
            except Exception as e:
                click.echo(f"Error importing {migration_file}: {e}\n")
