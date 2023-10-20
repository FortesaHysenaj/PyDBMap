from Modules.Column import Column
from Modules.DataType import Integer, String


class Student:
    __tablename__ = "Student"  # Table Name

    id = Column(Integer(), primary_key=True)
    name = Column(String())
    grade = Column(String())
