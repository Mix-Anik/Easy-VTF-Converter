from struct import pack, unpack


class CType:
    python_type = None
    c_type_format = None

    def __init__(self, byte_data):
        self.value = unpack(f'<{self.c_type_format}', byte_data)[0]

    def raw(self):
        return pack(f'<{self.c_type_format}', self.value)

    def set(self, new_value):
        if isinstance(new_value, self.python_type):
            self.value = new_value
        else:
            print(f'New value must be of type "{self.python_type}"')


class CUint32(CType):
    python_type = int
    c_type_format = 'I'

    def __init__(self, byte_data):
        super().__init__(byte_data)


class CUShort(CType):
    python_type = int
    c_type_format = 'H'

    def __init__(self, byte_data):
        super().__init__(byte_data)


class CFloat(CType):
    python_type = float
    c_type_format = 'f'

    def __init__(self, byte_data):
        super().__init__(byte_data)


class CUChar(CType):
    python_type = int
    c_type_format = 'B'

    def __init__(self, byte_data):
        super().__init__(byte_data)
