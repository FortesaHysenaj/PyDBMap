from Modules.Column import Column
from Modules.DataType import Integer, String


class Department:
    __tablename__ = "Departments"  # Table Name

    id = Column(Integer(), primary_key=True)
    dept_name = Column(String())
    manager = Column(String())
