from Modules.Column import Column
from Modules.DataType import Integer, String, Numeric


class Employee:
    __tablename__ = "Employees"  # Table Name

    id = Column(Integer(), primary_key=True)
    emp_name = Column(String())
    manager = Column(String())
    date = Column(String())
    salary = Column(String())
