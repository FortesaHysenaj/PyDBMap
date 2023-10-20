from src.config import configuration

# import sqlalchemy

db_settings = {
    "user": configuration.DB_USERNAME,
    "password": configuration.DB_PASSWORD,
    "host": configuration.DB_HOST,
    "port": configuration.DB_PORT,
    "database": configuration.DB_NAME,
}
