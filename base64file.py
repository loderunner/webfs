from base64 import b64encode, b64decode

def len_b64encode(s):
 return ((s * 4) / 3) + ((3 - (s % 3) + 1) if (s % 3 != 0) else 0)

def len_b64decode(s):
 return ((s / 4) * 4)

class Base64File(file):
    """docstring for Base64File"""
    def __init__(self, name, mode='r', buffering=-1):
        super(Base64File, self).__init__(name, mode, buffering)

    def read(self, size=-1):
        if size == -1:
            return b64encode(super(Base64File, self).read())
        else:
            return b64encode(super(Base64File, self).read(len_b64decode(size)))
