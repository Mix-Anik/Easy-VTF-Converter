from struct import pack, unpack


class c_uint32():
    def __init__(self, bytes):
        self.value = unpack('<I', bytes)[0]

    def raw(self):
        return pack("<I", self.value)
    def set(self, new_value):
        if type(new_value) == int:
            self.value = new_value
        else:
            print("New value must be of type 'int'")

class c_ushort():
    def __init__(self, bytes):
        self.value = unpack('<H', bytes)[0]

    def raw(self):
        return pack("<H", self.value)
    def set(self, new_value):
        if type(new_value) == int:
            self.value = new_value
        else:
            print("New value must be of type 'int'")

class c_float():
    def __init__(self, bytes):
        self.value = unpack('<f', bytes)[0]

    def raw(self):
        return pack("<f", self.value)
    def set(self, new_value):
        if type(new_value) == float:
            self.value = new_value
        else:
            print("New value must be of type 'float'")

class c_uchar():
    def __init__(self, bytes):
        self.value = unpack('<B', bytes)[0]

    def raw(self):
        return pack('<B', self.value)
    def set(self, new_value):
        if type(new_value) == int:
            self.value = new_value
        else:
            print("New value must be of type 'int'")