from Modules.Column import Column

class CreateTable:
    def __init__(self, cls):
        self.cls = cls
        self.table_name = cls.__tablename__
        self.columns = [attr for attr in dir(cls) if isinstance(getattr(cls, attr), Column)]

    def execute(self):
        query = f"CREATE TABLE {self.table_name} ("
        for col in self.columns:
            col_obj = getattr(self.cls, col)
            query += f"{col} {col_obj.datatype.__name__}"
            if col_obj.primary_key:
                query += " PRIMARY KEY"
            query += ", "
        query = query.rstrip(', ') + ")"
        print(query)  # Replace with actual query execution in your system
