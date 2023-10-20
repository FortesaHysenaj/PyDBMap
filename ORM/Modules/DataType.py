class Integer:
    __name__ = 'INT'
    def __init__(self, primary_key=False):
        self.primary_key = primary_key

class String:
    __name__ = 'VARCHAR(255)'
    def __init__(self, length=255):
        __name__ = f'VARCHAR({length})'

class Numeric:
    __name__ = 'numeric'
    def __init__(self, p, s):
        __name__ = f'numeric({p}, {s})'

class Date:
    __name__ = 'date'
    def __init__(self):
        pass

class Timestamp:
    __name__ = 'timestamp'
    def __init__(self):
        pass

class Time:
    __name__ = 'time'
    def __init__(self):
        pass

class Money:
    __name__ = 'money'
    def __init__(self):
        pass

class Text:
    __name__ = 'text'
    def __init__(self):
        pass