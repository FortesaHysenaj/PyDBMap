
import psycopg2
from src.utils.db import db_settings

class Migration:
    def apply(self):
        with psycopg2.connect(**db_settings) as connection, connection.cursor() as cursor:
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS Employees
			(id INT PRIMARY KEY, emp_name VARCHAR(255) , manager VARCHAR(255) , date VARCHAR(255) , salary VARCHAR(255) );
		
		
		
		
		CREATE TABLE IF NOT EXISTS Student
			(id INT PRIMARY KEY, name VARCHAR(255) , grade VARCHAR(255) );
		
		
		CREATE TABLE IF NOT EXISTS Departments
			(id INT PRIMARY KEY, dept_name VARCHAR(255) , manager VARCHAR(255) );
		
		
		
            ''')
