class Move:
    def __init__(self, line, column, value):
        self._line = line
        self._column = column
        self._value = value

    def getLine(self):
        return self._line

    def getColumn(self):
        return self._column

    def getValue(self):
        return self._value