class Column:
    def __init__(self, datatype, **kwargs):
        self.datatype = datatype
        self.primary_key = kwargs.get('primary_key', False)